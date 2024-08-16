from __future__ import annotations
from typing import TYPE_CHECKING, Any, Sequence, Tuple, Union
from medvol import MedVol

if TYPE_CHECKING:
    DataType = Union[Any, Sequence[Any]]
    FullLayerData = Tuple[DataType, dict, str]


def write_single_image(path: str, data: Any, meta: dict):
    """Writes a single image layer"""
    meta = meta["metadata"]
    spacing, origin, direction, header = None, None, None, None
    if "spacing" in meta:
        spacing = meta["spacing"]
    if "origin" in meta:
        origin = meta["origin"]
    if "direction" in meta:
        direction = meta["direction"]
    if "header" in meta:
        header = meta["header"]
    MedVol(data, spacing, origin, direction, header).save(path)
    return [path]
