from __future__ import annotations
from typing import TYPE_CHECKING, Any, Sequence, Tuple, Union
import numpy as np
from medvol import MedVol

if TYPE_CHECKING:
    DataType = Union[Any, Sequence[Any]]
    FullLayerData = Tuple[DataType, dict, str]


def write_single_image(path: str, data: Any, meta: dict):
    """Writes a single image layer"""
    meta = meta["metadata"]
    # Napari stores the layer in ZYX order (axis 0 = Z).
    # Permute back to XYZ so MedVol saves in canonical orientation.
    array_xyz = np.transpose(data, (2, 1, 0))
    MedVol(
        array_xyz,
        affine=meta.get("affine"),             # true oblique XYZ affine from load
        header=meta.get("header"),
        coordinate_system=meta.get("coordinate_system"),
    ).save(path)
    return [path]
