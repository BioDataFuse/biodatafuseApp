import streamlit as st
import os
from PIL import Image
from requests.exceptions import RequestException
from pyBiodatafuse import id_mapper
from pyBiodatafuse.constants import DATA_DIR
import sys
sys.path.append("E:\BioDataFuse\BioDataFuse_app")
from src.query.process_ids import process_identifiers
from src.query.process_sources import process_selected_sources
from src.download.data_link import download_tsv_as_link
from src.download.metadata_link import download_json_as_link
from src.visualization.cytoscape import importNetworkToCytoscape


## import the CSS styling
with open("style.css") as file:
    st.markdown(
        f"<style>{file.read()}</style>",
        unsafe_allow_html = True)

about = "📄About"
query = "🔍Query biological databases"
analysis = "📊Analysis"

def render_about():
    st.markdown(
    "<h1 style='font-size: 16px; text-align: justify; font-face: Italic'>To be added</h1>",
    unsafe_allow_html = True)

def render_query():
    # Step 1: Import a list of identifiers
    st.markdown(
        '<p style="font-size: 25px;">1. Import Identifiers</p>',
        unsafe_allow_html = True)
    
    col1, col2 = st.columns([2, 1])
    with col1:
        uploaded_file = st.file_uploader(
            "Upload a file containing identifiers",
            help = "Upload a file with one identifier per row or a comma-separated list (CSV or TXT)",
            type = ["csv", "txt"]
        )   
    with col2:
        text_input = st.text_area("Or enter identifiers (one per line)", "")

    # Step 2: Process input data using data_loader module
    identifiers_df = process_identifiers(uploaded_file, text_input)

    # Step 3: Select identifier type (only when a file is uploaded)
    if identifiers_df is not None:
        identifier_type = "Select identifier type"
        identifier_type = st.selectbox(
            "**Identifier Type**",
            ["Select identifier type",
             "RefSeq",
             "WikiGenes",
             "OMIM",
             "Uniprot-TrEMBL",
             "NCBI Gene",
             "Ensembl",
             "HGNC Accession Number",
             "PDB",
             "HGNC"]
        )
    
    # Step 4: Show the number of inputs
    if identifiers_df is not None and identifier_type != "Select identifier type":
        st.write(f"Number of input identifiers: {len(identifiers_df)}")
        st.write(f"Selected identifier type: {identifier_type}")

        # Step 5: Convert idenifiers using BridgeDb
        identifiers_df = id_mapper.bridgedb_Xref(
            identifiers_df["identifier"],
            inputSpecies = "Human",
            inputDatasource = identifier_type,
            outputDatasource = "All")

        # Check if the input is valid
        if identifiers_df["target"].str.strip().eq("").all():
            st.warning(
                f"The input is not valid",
                icon = "🚨")
        else:
            # Step 6: Select data sources for graph creation
            st.markdown(
                '<p style="font-size: 25px;">2. Select datasources to annotate your input with</p>',
                unsafe_allow_html = True)
            selected_sources = st.multiselect(
                "**Select datasources**", 
                [
                 "WikiPathway",
                 "DisGeNet",
                 "OpenTarget"
                ]
            )

            # Dictionary to map data sources to their additional options
            data_source_options = {
                # "WikiPathway": ["W1", "W2"],
                # "DisGeNet": ["D1", "D2"],
                "OpenTarget": [
                    "Gene location",
                    "Gene Ontology (GO)",
                    "Reactome pathways",
                    "Drug interactions",
                    "Disease associations"],
            }

            # Store the selected sources in a list
            selected_sources_list = []

            # Step 7: Display additional options when the user selects a source
            if selected_sources:
                for source in selected_sources:
                    options = data_source_options.get(source, [])
                    if options: st.markdown(f"**Options for {source}**")    
                    # Use checkboxes to show options for the current source
                    selected_options = [st.checkbox(f"{option}") for option in options]
                    # Display selected options
                    selected_options = [option for option, is_selected in zip(options, selected_options) if is_selected]
                    # Append the selected source and options to the list
                    selected_sources_list.append((source, selected_options))
            
            # Step 8: Add a "Query" button
            if not selected_sources_list:
                st.warning("Please select at least one datasource option.", icon = "⚠️")
            else:
                # Warningto import to "Cytoscape"
                st.warning("To visualize the query results in Cytoscape, please start the app.",
                           icon = "⚠️")
                
                # # Remove the existing metadata.json file
                # try:
                #     os.remove(os.path.join(DATA_DIR, "metadata.json"))
                # except OSError:
                #     pass

                query_button = st.button(
                    "Query",
                    key = "query_button")

            # Step 9: Execute selected functions when the "Query" button is clicked
            if selected_sources_list and query_button:
                combined_data = process_selected_sources(identifiers_df, selected_sources_list)
                
                # Check if the DataFrame is empty
                if combined_data.empty:
                    st.warning("The DataFrame is empty")
                elif not combined_data.empty:
                    # Convert the DataFrame to a TSV
                    combined_table = combined_data.to_csv(
                        index = False,
                        sep = "\t") # Saved for internal check

                    # import to "Cytoscape"
                    try:
                        importNetworkToCytoscape(
                            combined_data,
                            "BioDataFuse Network")
                    except RequestException as e:
                         pass


                    # Step 10: Display download links
                    st.markdown(
                        '<p style="font-size: 25px;">3. Export data</p>',
                        unsafe_allow_html = True)

                    # metadata
                    metadata_path = os.path.join(DATA_DIR, "metadata.json")
                    metadata_url = download_json_as_link(metadata_path, "BioDataFuse_metadata")
                    st.markdown(
                        metadata_url,
                        unsafe_allow_html = True)

                    # TSV
                    tsv_url = download_tsv_as_link(combined_data, "BioDataFuse_combined_table")    
                    st.markdown(
                        tsv_url,
                        unsafe_allow_html = True)

def render_analysis():
    st.write("To be developed")

# Add sidebar
logo = Image.open("logo.png")
st.sidebar.image(logo)
st.sidebar.markdown(
    "<h1 style='font-size: 40px; text-align: center;'>BioDataFuse</h1>",
    unsafe_allow_html = True)
st.sidebar.markdown(
    "<h1 style='font-size: 16px; text-align: center; font-face: italic;'>a user-friendly application to create and analyze content-specific knowledge graphs</h1>",
     unsafe_allow_html = True)

# Create a list of options for the sidebar
options = [
    "📄About",
    "🔍Query biological databases",
    "📊Analysis"]
display_page = st.sidebar.radio(
    "Select a page:",
    options, 
    label_visibility = "collapsed")

st.subheader(
    f"**{display_page}**", 
    divider = "rainbow")


if display_page == about:
    render_about()
elif display_page == query:
    render_query()
elif display_page == analysis:
    render_analysis()