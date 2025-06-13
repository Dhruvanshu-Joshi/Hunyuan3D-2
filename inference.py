import sys
import os
from hy3dgen.shapegen import Hunyuan3DDiTFlowMatchingPipeline
from hy3dgen.texgen import Hunyuan3DPaintPipeline
from PIL import Image
from txt2img import get_relevant_wikipedia_image  # if saved in a file

# Step 1: Get image from Wikipedia using user input
article_title = input("Enter Wikipedia article name (e.g., Grey reef shark): ").strip()
selected_image: Image.Image = get_relevant_wikipedia_image(article_title)

if selected_image is None:
    print("Failed to get a usable image. Exiting.")
    sys.exit(1)

# Step 2: Initialize DiT-based shape generator pipeline
pipeline = Hunyuan3DDiTFlowMatchingPipeline.from_pretrained("models")

# Step 3: Run the pipeline with the selected image
print("Generating base 3D mesh...")
mesh = pipeline(image=selected_image)[0]

# Step 4: Initialize texture paint pipeline
paint_pipeline = Hunyuan3DPaintPipeline.from_pretrained(
    "models",
    subfolder="hunyuan3d-paint-v2-0-turbo"
)

# Step 5: Generate textured mesh
print("Painting texture onto mesh...")
final_mesh = paint_pipeline(mesh, image=selected_image)

# Step 6: Export the final mesh
output_path = "output_model.glb"
final_mesh.export(output_path)
print(f"Mesh exported successfully as {output_path}")
