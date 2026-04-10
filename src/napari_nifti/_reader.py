import numpy as np
from medvol import MedVol

def napari_get_reader(path):
    """A basic implementation of a Reader contribution.

    Parameters
    ----------
    path : str or list of str
        Path to file, or list of paths.

    Returns
    -------
    function or None
        If the path is a recognized format, return a function that accepts the
        same path or list of paths, and returns a list of layer data tuples.
    """
    if isinstance(path, list):
        # reader plugins may be handed single path, or a list of paths.
        # if it is a list, it is assumed to be an image stack...
        # so we are only going to look at the first file.
        path = path[0]

    # if we know we cannot read the file, we immediately return None.
    if not (path.endswith(".nii") or path.endswith(".nii.gz") or path.endswith(".nrrd")):
        return None

    # otherwise we return the *function* that can read ``path``.
    return reader_function


def reader_function(path):
    """Take a path or list of paths and return a list of LayerData tuples.

    Readers are expected to return data as a list of tuples, where each tuple
    is (data, [add_kwargs, [layer_type]]), "add_kwargs" and "layer_type" are
    both optional.

    Parameters
    ----------
    path : str or list of str
        Path to file, or list of paths.

    Returns
    -------
    layer_data : list of tuples
        A list of LayerData tuples where each tuple in the list contains
        (data, metadata, layer_type), where data is a numpy array, metadata is
        a dict of keyword arguments for the corresponding viewer.add_* method
        in napari, and layer_type is a lower-case string naming the type of layer.
        Both "meta", and "layer_type" are optional. napari will default to
        layer_type=="image" if not provided
    """
    # handle both a string and a list of strings
    paths = [path] if isinstance(path, str) else path
    layer_data = []
    for _path in paths:
        image = MedVol(_path)

        # SAR+ axis order: dim 0 = Superior/Inferior (axial slider), dim 1 = Anterior/Posterior,
        # dim 2 = Right/Left.  This matches napari's roll cycle to Slicer's three standard views:
        #   Roll 0 → Axial   (A at top, R at left — radiological)
        #   Roll 1 → Sagittal (S at top, A at left)
        #   Roll 2 + T key → Coronal (S at top, R at left — radiological)
        array_sar = image.get_array("SAR+")

        # Deobliqued SAR+ geometry: diagonal spacing/origin used for the display affine.
        # deoblique=True gives the effective per-axis voxel size without interpolation,
        # which is what we need for the napari diagonal-affine constraint.
        geom = image.get_geometry("SAR+", deoblique=True)
        sp   = geom["spacing"]   # [sz, sy, sx] — always positive
        orig = geom["origin"]    # world coords of voxel (0,0,0) in SAR+ space
        sh   = array_sar.shape   # (Nz, Ny, Nx)  [spatial dims; time appended for 4-D]

        # Diagonal display affine with negative scales and far-corner origins.
        # Negative scale on dim i → world-high maps to canvas-top/left → correct anatomy:
        #   dim 0 (S): −sz  →  superior end at top of slider
        #   dim 1 (A): −sy  →  anterior end at top of canvas (axial/coronal)
        #   dim 2 (R): −sx  →  patient's right at left of canvas (radiological convention)
        ndim = image.ndims
        display_affine = np.eye(ndim + 1)
        for i in range(3):
            display_affine[i, i] = -sp[i]
            display_affine[i, ndim] = orig[i] + (sh[i] - 1) * sp[i]
        # Non-spatial axes (e.g. time for 4-D) keep identity scaling.
        for i in range(3, ndim):
            display_affine[i, i] = sp[i] if i < len(sp) else 1.0

        metadata = {
            "affine": image.affine,             # true oblique RAS+ affine — used for saving
            "spacing": image.spacing,
            "origin": image.origin,
            "direction": image.direction,
            "header": image.header,
            "coordinate_system": image.coordinate_system,
        }
        layer_data.append((array_sar, {"affine": display_affine, "metadata": metadata}, "image"))
    return layer_data
