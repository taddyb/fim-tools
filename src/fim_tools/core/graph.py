"""A file to contain all hydrofabric related functions"""

import geopandas as gpd
import networkx as nx


def _get_hydrofabric_graph(nexus: gpd.GeoDataFrame, flowlines: gpd.GeoDataFrame) -> nx.DiGraph:
    """Creates a networkx graph object to

    Parameters
    ----------
    nexus: gpd.GeoDataFrame
        Node points within the v20.1 hydrofabric
    flowlines: gpd.GeoDataFrame
        Edges within the v20.1 hydrofabric

    Returns
    -------
    nx.DiGraph
        The networkx directed graph
    """
    G = nx.DiGraph()
    nexus_to_toid = dict(zip(nexus["id"], nexus["toid"], strict=False))
    for _, node in nexus.iterrows():
        G.add_node(node["id"], type=node["type"], geometry=node["geometry"], toid=node["toid"])

    for _, edge in flowlines.iterrows():
        G.add_edge(
            edge["id"],
            edge["toid"],
            mainstem=edge["mainstem"],
            order=edge["order"],
            hydroseq=edge["hydroseq"],
            lengthkm=edge["lengthkm"],
            areasqkm=edge["areasqkm"],
            tot_drainage_areasqkm=edge["tot_drainage_areasqkm"],
            has_divide=edge["has_divide"],
            divide_id=edge["divide_id"],
            geometry=edge["geometry"],
        )

        if edge["toid"] in nexus_to_toid:
            G.add_edge(edge["toid"], nexus_to_toid[edge["toid"]])
    return G
