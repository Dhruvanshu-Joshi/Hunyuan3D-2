import sys
import os
import glob

# Load the DiT-based shape generator
from hy3dgen.shapegen import Hunyuan3DDiTFlowMatchingPipeline
pipeline = Hunyuan3DDiTFlowMatchingPipeline.from_pretrained('models')
mesh = pipeline(image='assets/cfimg.png')[0]

# Export the mesh
mesh.export("mesh.glb")
print("Mesh exported as output_model.glb")
