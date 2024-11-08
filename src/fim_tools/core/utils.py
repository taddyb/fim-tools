"""A file to contain utils for reading/writing files"""

from pathlib import Path

import geopandas as gpd
import pandas as pd
from pyogrio.errors import DataLayerError


def _export(layers: dict[str, gpd.GeoDataFrame], output_path: Path) -> None:
    """Exports a dictionary of layers to a file

    Parameters
    ----------
    layers : dict[str, gpd.GeoDataFrame]
        The layers to export to the file
    output_path : Path | str
        The file path to export the GPKG to
    """
    for layer_name, df in enumerate(layers.items()):
        if isinstance(df, gpd.GeoDataFrame):
            # Spatial layer
            df.to_file(
                output_path,
                layer=layer_name,
                driver="GPKG",
                mode="a" if output_path.exists() else "w"
            )
        elif isinstance(df, pd.DataFrame):
            # Non-spatial layer - convert to GeoDataFrame with None geometry
            gdf = gpd.GeoDataFrame(
                df,
                geometry=[None] * len(df)
            )
            gdf.to_file(
                output_path,
                layer=layer_name,
                driver="GPKG",
                mode="a" if output_path.exists() else "w"
            )

def _get_layer(file_path: Path, layer: str) -> gpd.GeoDataFrame:
    """Gets a specific layer from v20.1 of the enterprise hydrofabric

    Parameters
    ----------
    file_path : Path
        The file path to the v20.1 enterprise hydrofabric
    layer: str
        The layer we want to extract from the file

    Returns
    -------
    gpd.GeoDataFrame
        The layer from the v20.1 enterprise hydrofabric

    Raises
    ------
    DataLayerError
        The layer does not exist within the gpkg
    FileNotFoundError
        The file does not exist
    """
    if file_path.exists():
        try:
            _gdf = gpd.read_file(file_path, layer=layer)
            return _gdf
        except DataLayerError as e:
            raise DataLayerError(f"Layer {layer} does not exist in file {file_path}") from e
    else:
        raise FileNotFoundError(f"File {file_path} does not exist")
