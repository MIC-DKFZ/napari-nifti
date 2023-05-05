from napari_nifti._reader import load_nifti
from napari_nifti._writer import write_single_image
import napari
from napari import Viewer

filepath = "/home/k539i/Downloads/A2E3W4_0000_0000.nii.gz"

data = load_nifti(filepath)
write_single_image("/home/k539i/Downloads/001.nii.gz", data["image"], data["metadata"])

viewer = Viewer()
# viewer.add_image(data["image"], scale=data["scale"])
# viewer.add_image(data["image"], affine=data["affine"])

# napari.run()