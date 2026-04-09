from __future__ import annotations
from typing import TYPE_CHECKING, Any, Sequence, Tuple, Union
from medvol import MedVol

if TYPE_CHECKING:
    DataType = Union[Any, Sequence[Any]]
    FullLayerData = Tuple[DataType, dict, str]


def write_single_image(path: str, data: Any, meta: dict):
    """Writes a single image layer"""
    meta = meta["metadata"]
    spacing = meta.get("spacing")
    origin = meta.get("origin")
    direction = meta.get("direction")
    header = meta.get("header")
    coordinate_system = meta.get("coordinate_system")
    MedVol(data, spacing=spacing, origin=origin, direction=direction, header=header, coordinate_system=coordinate_system).save(path)
    return [path]
