import runpod
import os
import glob
import sys

# Load model components once (on cold start)
# This avoids reloading the models for every request
print("Loading models...")

# Dynamically locate the custom rasterizer .so path
rasterizer_libs = glob.glob(
    os.path.join(os.getcwd(), "hy3dgen", "texgen", "custom_rasterizer", "build", "lib.*", "*custom_rasterizer_kernel*.so")
)
if rasterizer_libs:
    sys.path.append(os.path.dirname(rasterizer_libs[0]))

from hy3dgen.shapegen import Hunyuan3DDiTFlowMatchingPipeline
from hy3dgen.texgen import Hunyuan3DPaintPipeline

shape_pipeline = Hunyuan3DDiTFlowMatchingPipeline.from_pretrained('models')
paint_pipeline = Hunyuan3DPaintPipeline.from_pretrained('models', subfolder='hunyuan3d-paint-v2-0-turbo')

print("Models loaded.")


def handler(event):
    print("Worker received job.")

    try:
        input_data = event["input"]
        image_path = input_data.get("image", "assets/cfimg.png")  # fallback to default

        print(f"Using image: {image_path}")

        # Step 1: Shape generation
        mesh = shape_pipeline(image=image_path)[0]

        # Step 2: Texture painting
        final_mesh = paint_pipeline(mesh, image=image_path)

        # Step 3: Export mesh
        output_path = "/app/output_model.glb"
        final_mesh.export(output_path)

        print("Mesh exported successfully.")

        return {
            "status": "success",
            "output_file": output_path
            # Optionally: Add a presigned URL if you upload this somewhere
        }

    except Exception as e:
        print(f"Error: {str(e)}")
        return {"status": "error", "message": str(e)}


# Start serverless worker
if __name__ == "__main__":
    runpod.serverless.start({"handler": handler})
