import streamlit as st
import pandas as pd
from pyBiodatafuse.annotators import(
    wikipathways,
    disgenet,
    opentargets
)
from pyBiodatafuse.utils import(
    combine_sources
) 

def process_selected_sources(bridgedb_df: pd.DataFrame,
                             selected_sources_list: list) -> pd.DataFrame:
    """query the selected databases and convert the output to a dataframe.
    
    @param bridgedb_df: BridgeDb output for creating the list of gene ids to query
    @param selected_sources_list: list of selected databases 
    """

    # Initialize variables
    combined_data = pd.DataFrame()
    combined_metadata = {}
    # Dictionary to map the datasource names to their corresponding functions
    data_source_functions = {
        "WikiPathway": wikipathways.get_gene_pathway,
        "DisGeNet": disgenet.get_gene_disease,
        "OpenTarget": {
            "Metadata": opentargets.get_version,
            "Gene location": opentargets.get_gene_location,
            "Gene Ontology (GO)": opentargets.get_gene_go_process,
            "Reactome pathways": opentargets.get_gene_reactome_pathways,
            "Drug interactions": opentargets.get_gene_drug_interactions,
            "Disease associations": opentargets.get_gene_disease_associations
        }
    }

    for source, options in selected_sources_list:
        if source in data_source_functions:
            if source == "OpenTarget":
                tmp_metadata = data_source_functions[source]["Metadata"]()
                combined_metadata[source] = tmp_metadata

                for option in options:
                    tmp_data = data_source_functions[source][option](bridgedb_df)
                    if tmp_data.empty:
                        st.warning(f"No annotation available for {source}(option: {option})")
                    if not tmp_data.empty:
                        combined_data = combine_sources([combined_data, tmp_data])
            elif source == "WikiPathway":
                combined_metadata[source] = {}
                tmp_data = data_source_functions[source](bridgedb_df)
                if tmp_data.empty:
                    st.warning(f"No annotation available for {source}")
                if not tmp_data.empty:
                    combined_data = combine_sources([combined_data, tmp_data])

            else:
                tmp_data, tmp_metadata = data_source_functions[source](bridgedb_df)
                combined_metadata[source] = tmp_metadata
                if tmp_data.empty:
                    st.warning(f"No annotation available for {source}")
                if not tmp_data.empty:
                    combined_data = combine_sources([combined_data, tmp_data])

    return combined_data, combined_metadata