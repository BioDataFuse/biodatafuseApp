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
    # Dictionary to map the datasource names to their corresponding functions
    data_source_functions = {
        "WikiPathway": wikipathways.annotateGenesWithWikipathwaysPathways,
        "DisGeNet": disgenet.disgenetAnnotator,
        "OpenTarget": {
            "Gene location": opentargets.get_gene_location,
            "Gene Ontology (GO)": opentargets.get_gene_go_process,
            "Reactome pathways": opentargets.get_gene_reactome_pathways,
            "Drug interactions": opentargets.get_gene_drug_interactions,
            "Disease associations": opentargets.get_gene_disease_associations
        }
    }

    for source, options in selected_sources_list:
        if source in data_source_functions:
            if options:
                for option in options:
                    tmp = data_source_functions[source][option](bridgedb_df)
                    if tmp.empty:
                        st.warning(f"No annotation available for {source}(option: {option})")
                    if not tmp.empty:
                        combined_data = combine_sources([combined_data, tmp])
            else:
                tmp = data_source_functions[source](bridgedb_df)
                if tmp.empty:
                    st.warning(f"No annotation available for {source}")
                if not tmp.empty:
                    combined_data = combine_sources([combined_data, tmp])

    return combined_data