import pandas as pd
import py4cytoscape as p4c
import streamlit as st
from pyBiodatafuse.constants import DATA_DIR
from pyBiodatafuse.utils import create_or_append_to_metadata

"""Python file for exporting the network to Cytoscape."""

def importNetworkToCytoscape(
        dataset: pd.DataFrame, 
        network_name: str = "Network") -> p4c.networks:
    """Import the network to cytoscape.

    @param dataset: the combined table created by combine_sources
    @param network_name: network name given by users 

    Usage example:
    >> dataset = combine_sources
    >> network_name = "Network"
    >> importNetworkToCytoscape(dataset, network_name)
    """
    # Initialize lists to store nodes and edges
    nodes_data = []
    edges_data = []

    # Process each row in the input data
    for index, row in dataset.iterrows():

        # Extract gene information
        gene_id = row["target"]
        gene_name = row["identifier"]
        gene_id_source = row["target.source"]

        gene_dsi = gene_dpi = gene_pli = None
        # gene_loc_identifier = gene_subcellular_loc = gene_location = None
        gene_location = []

        # Extract informations related to gene from DisGeNET (if availble)
        if "DisGeNET" in dataset.columns:
            disgenet_data = row["DisGeNET"]
            if disgenet_data and isinstance(disgenet_data, list):
                disgenet_keys = row["DisGeNET"][0].keys() 
                if "gene_dsi" in disgenet_keys:
                    gene_dsi = row["DisGeNET"][0]["gene_dsi"]
                if "gene_dpi" in disgenet_keys:
                    gene_dpi = row["DisGeNET"][0]["gene_dpi"]
                if "gene_pli" in disgenet_keys:
                    gene_pli = row["DisGeNET"][0]["gene_pli"]

        # Extract informations related to gene from OpenTargets location (if availble)
        if "OpenTargets_Location" in dataset.columns:
            opentargets_data = row["OpenTargets_Location"]
            if opentargets_data and isinstance(opentargets_data, list):
                opentargets_keys = row["OpenTargets_Location"][0].keys()
        #         if "loc_identifier" in opentargets_keys:
        #             gene_loc_identifier = row["OpenTargets_Location"][0]["loc_identifier"]
        #         if "subcellular_loc" in opentargets_keys:
        #             gene_subcellular_loc = row["OpenTargets_Location"][0]["subcellular_loc"]
        #         if "location" in opentargets_keys:
        #             gene_location = row["OpenTargets_Location"][0]["location"]
                if "location" in opentargets_keys:
                    location = row["OpenTargets_Location"][0]["location"]
                    if location is not None:
                        gene_location.append(location)

        # Create nodes
        nodes_data.append({
            "id": gene_id,
            "name": gene_name,
            "id_source": gene_id_source,
            "node_type": "gene",
            "gene_location": gene_location,
            # "gene_loc_id": gene_loc_identifier if gene_loc_identifier is not None and gene_loc_identifier != "" else None,
            # "gene_subcellular_loc": gene_subcellular_loc if gene_subcellular_loc is not None and gene_subcellular_loc != "" else None,
            # "gene_location": gene_location if gene_location is not None and gene_location != "" else None,
            "gene_dsi": gene_dsi if gene_dsi is not None and gene_dsi != "" else None,
            "gene_dpi": gene_dpi if gene_dpi is not None and gene_dpi != "" else None,
            "gene_pli": gene_pli if gene_pli is not None and gene_pli != "" else None
        })

        # Extract gene information from DisGeNET
        if "DisGeNET" in dataset.columns:
            # disgenet_data = json.loads(row["DisGeNET"])
            disgenet_data = row["DisGeNET"]
            if disgenet_data and disgenet_data is not None:  # Check if it"s a non-empty list
                for item in disgenet_data:
                    disgenet_disease_id = item.get("diseaseid", "")
                    disgenet_disease_name = item.get("disease_name", "")
                    disgenet_disease_class = item.get("disease_class", "")
                    disgenet_disease_class_name = item.get("disease_class_name", "")
                    disgenet_disease_type = item.get("disease_type", "")
                    disgenet_disease_semantic_type = item.get("disease_semantic_type", "")
                    disgenet_score = item.get("score", "")
                    disgenet_ei = item.get("ei", "")
                    disgenet_el = item.get("el", "")
                    disgenet_source = item.get("source", "")
                    nodes_data.append({
                        "id" : disgenet_disease_id,
                        "name" : disgenet_disease_name,
                        "node_type": "disease",
                        "disease_class" : disgenet_disease_class,
                        "disease_class_name" : disgenet_disease_class_name,
                        "disease_type": disgenet_disease_type,
                        "disease_semantic_type": disgenet_disease_semantic_type,
                        "disgenet_score" : disgenet_score,
                        "ei" : disgenet_ei,
                        "el" : disgenet_el,
                        "source": disgenet_source,
                        "datasource": "DisGeNET"
                    })
                    # Create edges
                    if disgenet_disease_id != "":
                        edges_data.append({"source": gene_id, "target": disgenet_disease_id, "interaction": "association"})
            
        # Extract OpenTargets_Diseases information
        if "OpenTargets_Diseases" in dataset.columns:
            opentargets_data = row["OpenTargets_Diseases"]
            if opentargets_data:  # Check if it"s a non-empty list
                for item in opentargets_data:
                    opentargets_disease_id = item.get("disease_id", "")
                    opentargets_disease_name = item.get("disease_name", "")
                    opentargets_therapeutic_areas = item.get("therapeutic_areas", "")
                    nodes_data.append({
                        "id" : opentargets_disease_id,
                        "name" : opentargets_disease_name,
                        "node_type": "disease",
                        "therapeutic_areas" : opentargets_therapeutic_areas,
                        "datasource": "OpenTargets"
                    })                    
                    # Create edges
                    if opentargets_disease_id != "":
                        edges_data.append({"source": gene_id, "target": opentargets_disease_id, "interaction": "association"})

        # Extract GO_Process information
        if "GO_Process" in dataset.columns:
            opentargets_data = row["GO_Process"]
            if opentargets_data:  # Check if it"s a non-empty list
                for item in opentargets_data:
                    opentargets_go_id = item.get("go_id", "")
                    opentargets_go_name = item.get("go_name", "")
                    nodes_data.append({
                        "id" : opentargets_go_id,
                        "name" : opentargets_go_name,
                        "node_type": "gene ontology",
                        "datasource": "OpenTargets"
                    })    
                    # Create edges
                    if opentargets_go_id != "":
                        edges_data.append({"source": gene_id, "target": opentargets_go_id, "interaction": "part of"})

        # Extract Reactome_Pathways information
        if "Reactome_Pathways" in dataset.columns:
            opentargets_data = row["Reactome_Pathways"]
            if opentargets_data:  # Check if it"s a non-empty list
                for item in opentargets_data:
                    opentargets_pathway_id = item.get("pathway_id", "")
                    opentargets_pathway_name = item.get("pathway_name", "")
                    nodes_data.append({
                        "id" : opentargets_pathway_id,
                        "name" : opentargets_pathway_name,
                        "node_type": "reactome pathways",
                        "datasource": "OpenTargets"
                    })    
                    # Create edges
                    if opentargets_pathway_id != "":
                        edges_data.append({"source": gene_id, "target": opentargets_pathway_id, "interaction": "part of"})

        # Extract ChEMBL_Drugs information
        if "ChEMBL_Drugs" in dataset.columns:
            opentargets_data = row["ChEMBL_Drugs"]
            if opentargets_data:  # Check if it"s a non-empty list
                for item in opentargets_data:
                    opentargets_chembl_id = item.get("chembl_id", "")
                    opentargets_drug_name = item.get("drug_name", "")
                    opentargets_relation = item.get("relation", "")

                    nodes_data.append({
                        "id" : opentargets_chembl_id,
                        "name" : opentargets_drug_name,
                        "drug_gene_relation": opentargets_relation,
                        "node_type": "drug interactions",
                        "datasource": "OpenTargets"
                    })    
                    # Create edges
                    if opentargets_chembl_id != "":
                        edges_data.append({"source": gene_id, "target": opentargets_chembl_id, "interaction": opentargets_relation})


    # Create DataFrames for nodes and edges
    nodes = pd.DataFrame(nodes_data)
    edges = pd.DataFrame(edges_data)

    # Replace NaN values with empty strings and remove empty rows
    if not nodes.empty and not edges.empty:
        nodes = nodes.fillna("")
        nodes = nodes[nodes["id"] != ""]
        edges = edges.fillna("")
        edges = edges[edges["target"] != ""].drop_duplicates()

        # Define the visual style as a dictionary
        default = {
            "title": "BioDataFuse_style",
            "defaults": [
                {
                    "visualProperty": "NODE_FILL_COLOR",
                    "value": "#FF0000" 
                },
                {
                    "visualProperty": "EDGE_COLOR",
                    "value": "#000000"  
                }
            ],
            "mappings": []  
        }

        # Create the network in Cytoscape
        p4c.networks.create_network_from_data_frames(
            nodes,
            edges,
            title = network_name,
            collection="BioDataFuse", 
        )

        # Apply the visual style
        p4c.styles.create_visual_style(default)

        # Define node shape and color mapping 
        column = "node_type"
        values = [
            "gene", "disease", "gene ontology", "reactome pathways", "drug interactions"]
        shapes = ["DIAMOND", "RECTANGLE", "OCTAGON", "HEXAGON", "ELLIPSE"] 
        colors = ["#AAFF88", "#B0C4DE", "pink", "yellow", "red"]

        # Apply node shape and color mappings
        p4c.set_node_color_mapping(
            column,
            values,
            colors,
            mapping_type="d",
            style_name = "default")
        p4c.set_node_shape_mapping(
            column,
            values,
            shapes,
            style_name = "default")
        
        st.success("Data imported to Cytoscape!", icon = "✅")

        """Metdata details"""
        # Add version to metadata file
        cytoscape_version = p4c.cytoscape_version_info()
        # Add the datasource, query, query time, and the date to metadata
        cytoscape_metadata = {
            "datasource": "Cytoscape",
            "metadata": {"source_version": cytoscape_version}
        }

        create_or_append_to_metadata(
            cytoscape_metadata
        )  # Call the function from the metadata module

        print(f"The query metadata is appended: {DATA_DIR}\metadata.json")

        return None
    else:
        st.success("No graph to import to Cytoscape.", icon =  "🚨")