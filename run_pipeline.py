import sys
import os
import glob

# Dynamically locate the custom rasterizer .so path
rasterizer_libs = glob.glob(
    os.path.join(os.getcwd(), "hy3dgen", "texgen", "custom_rasterizer", "build", "lib.*", "*custom_rasterizer_kernel*.so")
)
if rasterizer_libs:
    sys.path.append(os.path.dirname(rasterizer_libs[0]))

# Load the DiT-based shape generator
from hy3dgen.shapegen import Hunyuan3DDiTFlowMatchingPipeline
pipeline = Hunyuan3DDiTFlowMatchingPipeline.from_pretrained('models')
mesh = pipeline(image='assets/cfimg.png')[0]

# Load the texture paint generator
from hy3dgen.texgen import Hunyuan3DPaintPipeline
paint_pipeline = Hunyuan3DPaintPipeline.from_pretrained(
    'models',
    subfolder='hunyuan3d-paint-v2-0-turbo'
)

# Generate final textured mesh
final_mesh = paint_pipeline(mesh, image='assets/cfimg.png')

# Export the mesh
final_mesh.export("output_model.glb")
print("Mesh exported as output_model.glb")
