from __future__ import annotations
from typing import TYPE_CHECKING, Any, Sequence, Tuple, Union
import SimpleITK as sitk
import numpy as np

if TYPE_CHECKING:
    DataType = Union[Any, Sequence[Any]]
    FullLayerData = Tuple[DataType, dict, str]

dtype_mapping = {"int8": np.int8, "int16": np.int16, "int32": np.int32, "int64": np.int64}


def write_single_image(path: str, data: Any, meta: dict):
    """Writes a single image layer"""
    meta = meta["metadata"]
    metadata, origin, direction, spacing = None, None, None, None
    if "metadata" in meta:
        metadata = meta["metadata"]
    if "origin" in meta:
        origin = meta["origin"]
    if "direction" in meta:
        direction = meta["direction"]
    if "spacing" in meta:
        spacing = meta["spacing"]
    save_nifti(path, data, metadata=metadata, origin=origin, direction=direction, spacing=spacing)
    return [path]


def save_nifti(filename, image, metadata=None, origin=None, direction=None, spacing=None):
    if str(image.dtype) in dtype_mapping:
        image = image.astype(dtype_mapping[str(image.dtype)])
    image = sitk.GetImageFromArray(image)

    if metadata is not None:
        [image.SetMetaData(key, metadata[key]) for key in metadata.keys()]

    if origin is not None:
        image.SetOrigin(origin)

    if direction is not None:
        image.SetDirection(direction)

    if spacing is not None:
        image.SetSpacing(spacing)

    sitk.WriteImage(image, filename)
