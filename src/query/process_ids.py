import streamlit as st
import pandas as pd
from pyBiodatafuse.data_loader import(
    create_df_from_text
)

def process_identifiers(
    uploaded_file,
    text_input) -> pd.DataFrame:
    """convert the input identifier list to a dataframe.

    @param uploaded_file: a CSV or TXT file contains identifiers
    @param text_input: the identifiers in the st.text_area (one identifier per line)
    """

    if uploaded_file is None and text_input.strip() == "":
        st.warning(
            "Please provide your identifiers!",
            icon = "⚠️"
        )
        return None

    if uploaded_file is not None and uploaded_file.type not in ["application/vnd.ms-excel", "text/plain"]:
        st.error("Unsupported file format. Please upload a CSV or TXT file.")
        st.stop()

    identifiers_df = []

    if text_input.strip() != "":
        # Create a DataFrame from the list of identifiers
        identifiers_df = create_df_from_text(text_input)

    if uploaded_file is not None:
        # Read the uploaded file
        file_contents = uploaded_file.getvalue().decode('utf-8')
        if identifiers_df:
            identifiers_df = pd.concat([
                identifiers_df,
                create_df_from_text(file_contents)]).unique()
        else:
            identifiers_df = create_df_from_text(file_contents)

    return identifiers_df
