# Pretrained Models Distribution

To avoid costs associated with Git LFS, the pretrained models are distributed via GitHub releases.

## Download Instructions

### Windows Users
Simply launch the app using `start.bat`, which will automatically prompt you to download the models if they're not already present. *Alternatively*, you may also do the download+extraction manually as explained below.

### Mac/Linux Users
1. Download the latest [pretrained_models.zip](https://github.com/Cosmic-Infinity/draw2pix/releases/latest/) from the releases page
2. Extract the contents directly into the `draw2pix/pretrained_models/` directory in your project

## File Structure

The release zip file contains:
```
pretrained_models.zip
  ├── G_100e_cleanT_L65_Lr25.pth
  ├── G_250e_cleanT_L50_Lr10.pth
  ├── G_250e_cleanT_L85_Lr22.pth
  ├── G_300e_dirtyT_L100_Lr20.pth
  └── version.txt
```

**⚠️ Important**: Extract the `.pth` model files and `version.txt` directly into the `pretrained_models/` directory, **not** into a subdirectory.

## Model Architectures

The current release models use **U-Net 256** architecture. The web application automatically detects the architecture of each model from its filename prefix, so you can mix different architectures in the same directory.

### Current Release Models

The models in this release (v1.x) follow the legacy naming convention and will default to **U-Net 256** architecture:
```
G_100e_cleanT_L65_Lr25.pth
G_250e_cleanT_L50_Lr10.pth
G_250e_cleanT_L85_Lr22.pth
G_300e_dirtyT_L100_Lr20.pth
```

These models will work correctly as they use the U-Net 256 architecture (the default when no prefix is detected).

### Filename Naming Convention (For Custom Models)

To enable automatic architecture detection for your own trained models, follow this naming convention:

| Prefix | Architecture | Example |
|--------|-------------|---------|
| `U256_` | U-Net 256 | `U256_flowers_100e.pth` |
| `U128_` | U-Net 128 | `U128_flowers_50e.pth` |
| `R9_` | ResNet 9 blocks | `R9_flowers_200e.pth` |
| `R6_` | ResNet 6 blocks | `R6_flowers_150e.pth` |

**Note**: Prefixes are case-insensitive.

### Usage

```bash
# Auto-detection from filenames (recommended)
python app/web_app.py --model_dir pretrained_models

# Force specific architecture for all models
python app/web_app.py --model_dir pretrained_models --netG resnet_9blocks
```

**Supported architectures**: `unet_256`, `unet_128`, `resnet_9blocks`, `resnet_6blocks`

## Versioning & Auto-Update

Each release is tracked with a version number stored in `version.txt`. The auto-update feature (Windows only, via `start.bat`) checks your current version against the latest release and prompts you to update if a newer version is available.
