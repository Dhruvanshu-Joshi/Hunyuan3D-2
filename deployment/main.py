import sys
import os
import glob
import gc
import time
import torch
import numpy as np
import trimesh
import open3d as o3d
from PIL import Image
from torchvision import transforms

# Custom imports (ensure these exist in your environment)
from Image_generator import mymodel
from hy3dgen.texgen import Hunyuan3DPaintPipeline
from hy3dgen.shapegen import Hunyuan3DDiTFlowMatchingPipeline
from hy3dgen.rembg import BackgroundRemover
from fathomnet.api import images
from utils import get_best_crop_image

# Dynamically locate the custom rasterizer .so path
rasterizer_libs = glob.glob(
    os.path.join(
        os.getcwd(),
        "hy3dgen",
        "texgen",
        "custom_rasterizer",
        "build",
        "lib.*",
        "*custom_rasterizer_kernel*.so"
    )
)
if rasterizer_libs:
    sys.path.append(os.path.dirname(rasterizer_libs[0]))


def clean_memory():
    """Clean CPU and GPU memory."""
    gc.collect()
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
        torch.cuda.ipc_collect()
        print("GPU memory cleared.")
    else:
        print("No GPU available.")


# Device selection
clean_memory()
DEVICE_2 = torch.device(
    "cuda:1" if torch.cuda.device_count() > 1
    else ("cuda:0" if torch.cuda.is_available() else "cpu")
)

# --- Load Mesh Generation Pipeline ---
mesh_pipeline = Hunyuan3DDiTFlowMatchingPipeline.from_pretrained(
    'models',
    device=DEVICE_2
)

# --- Load Texture Painting Pipeline ---
clean_memory()
paint_pipeline = Hunyuan3DPaintPipeline.from_pretrained(
    'models',
    subfolder='hunyuan3d-paint-v2-0-turbo'
)

print("Model Loaded")

# --- Load FathomNet images ---
CONCEPT = 'Grimpoteuthis'
fathomnet_image_list = images.find_by_concept(CONCEPT)
image_urls = [img.url for img in fathomnet_image_list]

# --- Load SRGAN model ---
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = mymodel()
model.load_state_dict(torch.load('image_models/SR_GAN_best.pth'))
model.to(device)
model.eval()

sr_transform = transforms.Compose([
    transforms.Resize((256, 256)),
    transforms.ToTensor(),
    transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))
])

zero_time = time.time()

# --- Get best image ---
user_input = input("Enter concept name (default: Grimpoteuthis): ").strip()
concept = user_input if user_input else "Grimpoteuthis"
best_image = get_best_crop_image(concept)
if best_image:
    best_image.show()
    best_image.save("best_result.jpg")

# --- Remove Background ---
image = best_image.convert("RGBA")
rembg = BackgroundRemover()
image = rembg(image)
image.save("no_bg.png")

# --- Mesh simplification & painting ---
# NOTE: Ensure img_mesh is defined somewhere earlier in the pipeline
if isinstance(img_mesh, trimesh.Scene):
    meshes = [g for g in img_mesh.geometry.values()]
    mesh = trimesh.util.concatenate(meshes)
else:
    mesh = img_mesh

print("mesh_loaded")

initial_tic = time.time()

# Convert to Open3D format
o3d_mesh = o3d.geometry.TriangleMesh()
o3d_mesh.vertices = o3d.utility.Vector3dVector(mesh.vertices)
o3d_mesh.triangles = o3d.utility.Vector3iVector(mesh.faces)

target_faces = int(len(mesh.faces) * 0.1)
simplified = o3d_mesh.simplify_quadric_decimation(target_faces)

decimated_mesh_90 = trimesh.Trimesh(
    vertices=np.asarray(simplified.vertices),
    faces=np.asarray(simplified.triangles),
    process=False
)

tic = time.time()
print("Total Time for decimation:", tic - initial_tic)

# Paint mesh
paint_mesh = paint_pipeline(decimated_mesh_90, image=image)

print("Total Time for model formation:", time.time() - tic)
print("Total Time for model formation with decimation:", time.time() - initial_tic)
print("Total Time for model formation with decimation:", time.time() - zero_time)

clean_memory()

# Export results
img_mesh.export(f'img_mesh_{concept}.glb')
paint_mesh.export(f'paint_mesh_{concept}.glb')
