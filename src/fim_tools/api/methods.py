from pathlib import Path

import geopandas as gpd
import networkx as nx

from fim_tools.core.graph import _get_hydrofabric_graph
from fim_tools.core.utils import _export, _get_layer

__all__ = [
    "get_upstream",
]


def get_upstream(
    file_path: Path | str, output_path: Path | str, source: str, flowpath_attr_cols: list[str] | None = None
) -> gpd.GeoDataFrame:
    """Gets upstream divides, nexus, flowpaths, and attributes from a source nexus

    Parameters
    ----------
    file_path : Path | str
        The file path to the v2.2 hydrofabric file
    source : str
        The Nexus point (ex: "tnx-1000006230")
    flowpath_attr_cols : list[str] | None, optional
        Columns that we are requesting from the flowpath attributes, by default None

    Returns
    -------
    gpd.GeoDataFrame
        The upstream data from the source nexus
    """
    if isinstance(file_path, str):
        file_path = Path(file_path)
    if isinstance(output_path, str):
        output_path = Path(output_path)

    flowpaths = _get_layer(file_path, layer="flowpaths")
    nexus = _get_layer(file_path, layer="nexus")
    divides = _get_layer(file_path, layer="divides")
    flowpath_attributes = _get_layer(file_path, layer="flowpath-attributes")
    network = _get_layer(file_path, layer="network")

    G = _get_hydrofabric_graph(nexus, flowpaths)
    subset = list(nx.ancestors(G=G, source=source))
    subset.append(source)

    subset_divide_ids = [f"cat-{x.split('-')[1]}" for x in subset]
    if flowpath_attr_cols is not None:
        flowpath_attributes = flowpath_attributes[flowpath_attr_cols]

    divide_mask = divides["divide_id"].isin(subset_divide_ids)
    nexus_mask = nexus["id"].isin(subset)
    flowpaths_mask = flowpaths["id"].isin(subset)
    flowpaths_attributes_mask = flowpath_attributes["link"].isin(subset)
    network_mask = network["divide_id"].isin(subset_divide_ids)

    subset_divides = divides[divide_mask]
    subset_nexus = nexus[nexus_mask]
    subset_flowpaths = flowpaths[flowpaths_mask]
    subset_flowpath_attributes = flowpath_attributes[flowpaths_attributes_mask]
    subset_network = network[network_mask]

    _export(
        layers={
            "divides": subset_divides,
            "nexus": subset_nexus,
            "flowpaths": subset_flowpaths,
            "flowpath-attributes": subset_flowpath_attributes.drop_duplicates(),
            "network": subset_network,
        },
        output_path=output_path,
    )
