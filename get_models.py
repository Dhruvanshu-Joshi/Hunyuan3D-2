from huggingface_hub import snapshot_download

# Replace with the model repo ID you want
repo_id = "tencent/Hunyuan3D-2"

# Destination folder to save the model
local_dir = "models"

# Download the model
snapshot_download(
    repo_id="tencent/Hunyuan3D-2",
    local_dir="models",
    allow_patterns=[
        "hunyuan3d-dit-v2-0/model.fp16.safetensors",
        "hunyuan3d-dit-v2-0/config.yaml"
    ],
)

print("Model downloaded to:", local_dir)
