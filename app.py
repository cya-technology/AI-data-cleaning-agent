import streamlit as st
import pandas as pd
from io import BytesIO

from foundry_service import clean_excel_with_foundry


# ------------------------------------------------------------
# PAGE CONFIGURATION
# ------------------------------------------------------------

st.set_page_config(
    page_title="Data Migration Tool",
    page_icon="📊",
    layout="wide",
)


# ------------------------------------------------------------
# HEADER
# ------------------------------------------------------------

st.title("📊 Data Migration Tool")

st.write(
    "Upload a client Excel spreadsheet. Microsoft Foundry will "
    "analyze and clean the data using Code Interpreter."
)

st.divider()


# ------------------------------------------------------------
# FILE UPLOAD
# ------------------------------------------------------------

uploaded_file = st.file_uploader(
    "Choose an Excel file",
    type=["xlsx", "xls"],
)


# ------------------------------------------------------------
# DISPLAY ORIGINAL DATA
# ------------------------------------------------------------

if uploaded_file is not None:

    st.success(f"Uploaded: {uploaded_file.name}")

    try:

        # Keep the uploaded file in memory
        original_bytes = uploaded_file.getvalue()

        # Read Excel file
        original_df = pd.read_excel(
            BytesIO(original_bytes)
        )

        # Display basic information
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric(
                "Rows",
                len(original_df)
            )

        with col2:
            st.metric(
                "Columns",
                len(original_df.columns)
            )

        with col3:
            st.metric(
                "Missing Values",
                int(original_df.isna().sum().sum())
            )

        # Display original spreadsheet
        st.subheader("Original Data")

        st.dataframe(
            original_df,
            use_container_width=True,
            height=400,
        )

    except Exception as exc:

        st.error(
            f"Unable to read the Excel file: {exc}"
        )

        st.stop()


    st.divider()


    # --------------------------------------------------------
    # SEND FILE TO FOUNDRY
    # --------------------------------------------------------

    if st.button(
        "🤖 Clean Data with AI",
        type="primary",
        use_container_width=True,
    ):

        with st.spinner(
            "Uploading the file to Microsoft Foundry "
            "and cleaning the data..."
        ):

            try:

                result = clean_excel_with_foundry(
                    file_bytes=original_bytes,
                    filename=uploaded_file.name,
                )

                # Save result for this Streamlit session
                st.session_state[
                    "cleaning_result"
                ] = result

                st.success(
                    "AI cleaning completed successfully!"
                )

            except Exception as exc:

                st.error(
                    "The Foundry cleaning process failed."
                )

                st.exception(exc)

                st.stop()


# ------------------------------------------------------------
# DISPLAY CLEANED RESULTS
# ------------------------------------------------------------

if "cleaning_result" in st.session_state:

    result = st.session_state["cleaning_result"]

    cleaned_bytes = result["file_bytes"]

    cleaned_filename = result["filename"]


    # --------------------------------------------------------
    # AI SUMMARY
    # --------------------------------------------------------

    st.divider()

    st.subheader("🤖 AI Cleaning Summary")

    if result["summary"]:

        st.write(
            result["summary"]
        )


    # --------------------------------------------------------
    # READ GENERATED WORKBOOK
    # --------------------------------------------------------

    try:

        workbook = pd.ExcelFile(
            BytesIO(cleaned_bytes)
        )

        st.subheader("📋 Cleaned Workbook")

        st.write(
            "Worksheets created by the AI:"
        )

        st.write(
            ", ".join(workbook.sheet_names)
        )


        # ----------------------------------------------------
        # CLEANED DATA
        # ----------------------------------------------------

        if "Cleaned_Data" in workbook.sheet_names:

            cleaned_df = pd.read_excel(
                BytesIO(cleaned_bytes),
                sheet_name="Cleaned_Data",
            )

            st.subheader("Cleaned Data")

            st.dataframe(
                cleaned_df,
                use_container_width=True,
                height=400,
            )


        # ----------------------------------------------------
        # CLEANING LOG
        # ----------------------------------------------------

        if "Cleaning_Log" in workbook.sheet_names:

            log_df = pd.read_excel(
                BytesIO(cleaned_bytes),
                sheet_name="Cleaning_Log",
            )

            st.subheader("🔎 Cleaning Log")

            st.dataframe(
                log_df,
                use_container_width=True,
                height=300,
            )


        # ----------------------------------------------------
        # DOWNLOAD
        # ----------------------------------------------------

        st.divider()

        st.subheader("📥 Download")

        st.download_button(
            label="⬇️ Download Cleaned Excel File",

            data=cleaned_bytes,

            file_name=cleaned_filename,

            mime=(
                "application/vnd.openxmlformats-officedocument."
                "spreadsheetml.sheet"
            ),

            type="primary",

            use_container_width=True,
        )


        # ----------------------------------------------------
        # SQL SERVER - NEXT PHASE
        # ----------------------------------------------------

        st.divider()

        st.subheader("🗄️ SQL Server")

        st.info(
            "SQL Server import will be enabled in the next phase."
        )


    except Exception as exc:

        st.error(
            "The cleaned workbook was generated, but "
            "Streamlit could not read it."
        )

        st.exception(exc)