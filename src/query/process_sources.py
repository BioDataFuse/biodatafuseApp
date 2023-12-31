import streamlit as st
import pandas as pd
from collections import defaultdict
from pyBiodatafuse.annotators import wikipathways, disgenet, opentargets, stringdb
from pyBiodatafuse.utils import combine_sources


def process_selected_sources(
    bridgedb_df: pd.DataFrame, selected_sources_list: list
) -> pd.DataFrame:
    """query the selected databases and convert the output to a dataframe.

    @param bridgedb_df: BridgeDb output for creating the list of gene ids to query
    @param selected_sources_list: list of selected databases
    """

    # Initialize variables
    combined_data = pd.DataFrame()
    combined_metadata = defaultdict(lambda: defaultdict(str))
    # Dictionary to map the datasource names to their corresponding functions
    data_source_functions = {
        "WikiPathway": wikipathways.get_gene_wikipathway,
        "DisGeNet": disgenet.get_gene_disease,
        "OpenTarget": {
            "Gene location": opentargets.get_gene_location,
            "Gene Ontology (GO)": opentargets.get_gene_go_process,
            "Reactome pathways": opentargets.get_gene_reactome_pathways,
            "Drug interactions": opentargets.get_gene_drug_interactions,
            "Disease associations": opentargets.get_gene_disease_associations,
        },
        "STRING-DB": stringdb.get_ppi
    }

    for source, options in selected_sources_list:
        if source in data_source_functions:
            if options:
                for option in options:
                    tmp_data, tmp_metadata = data_source_functions[source][option](
                        bridgedb_df
                    )
                    print(tmp_data)
                    combined_metadata[source][option] = tmp_metadata
                    if tmp_data.empty:
                        st.warning(
                            f"No annotation available for {source}(option: {option})"
                        )
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
