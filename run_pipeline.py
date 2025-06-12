from hy3dgen.shapegen import Hunyuan3DDiTFlowMatchingPipeline
from hy3dgen.texgen import Hunyuan3DPaintPipeline
import os

# Ensure asset image path exists
assert os.path.exists("assets/cfimg.png"), "Image not found at assets/cfimg.png"

print("Loading shape generation pipeline...")
pipeline = Hunyuan3DDiTFlowMatchingPipeline.from_pretrained('models')
mesh = pipeline(image='assets/cfimg.png')[0]

print("Shape generated")

print("Loading texture generation pipeline...")
paint_pipeline = Hunyuan3DPaintPipeline.from_pretrained(
    'models',
    subfolder='hunyuan3d-paint-v2-0-turbo'
)

print("Painting mesh...")
final_mesh = paint_pipeline(mesh, image='assets/cfimg.png')

# Optional: save result
print("Saving final textured mesh...")
final_mesh.export('output_model_texture.glb')

print("Done. Mesh saved as output_model_texture.glb")
