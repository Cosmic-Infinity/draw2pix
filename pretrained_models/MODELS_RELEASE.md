# Pretrained Models Distribution

To avoid costs associated with Git LFS, the pretrained models are distributed via GitHub releases.

## Download Instructions

### Windows Users
Simply launch the app using `start.bat`, which will automatically prompt you to download the models if they're not already present. The script will:
- Detect and download single or split archive files (if the release is split due to GitHub size limits)
- Show progress indicators during download and extraction
- Automatically handle version updates

*Alternatively*, you may also do the download+extraction manually as explained below.

### Mac/Linux Users
1. Download the latest release files from the [releases page](https://github.com/Cosmic-Infinity/draw2pix/releases/latest/)
   - If the release contains a single `pretrained_models.zip`, download that file
   - If the release is split (due to GitHub size limits), download all parts: `pretrained_models_1.zip`, `pretrained_models_2.zip`, etc.
2. Extract all downloaded zip files directly into the `draw2pix/pretrained_models/` directory in your project
3. All parts will extract to the same location and combine into the complete model set

## File Structure

The release archive(s) contain:
```
pretrained_models.zip (or pretrained_models_1.zip, pretrained_models_2.zip, etc.)
  ├── *.pth                  # Multiple pretrained model files
  └── version.txt            # Release version tracking
```

**⚠️ Important**: Extract the `.pth` model files and `version.txt` directly into the `pretrained_models/` directory, **not** into a subdirectory. If using split archives, extract all parts to the same location.

## Model Architectures

The web application automatically detects the architecture of each model from its filename prefix, allowing you to mix different architectures in the same directory. Models without a recognized prefix will default to **U-Net 256** architecture.

### Filename Naming Convention

Model filenames use prefixes to indicate their architecture. The application automatically detects these prefixes:

| Prefix | Architecture | Example |
|--------|-------------|---------|
| `U256_` | U-Net 256 | `U256_Flower_1.pth` |
| `U128_` | U-Net 128 | `U128_Flower_1.pth` |
| `R9_` | ResNet 9 blocks | `R9_Flower_13.pth` |
| `R6_` | ResNet 6 blocks | `R6_Flower_1.pth` |

**Note**: 
- Prefixes are case-insensitive
- Models without a recognized prefix default to U-Net 256 architecture
- See [docs/MODEL_REFERENCE.md](../docs/MODEL_REFERENCE.md) for complete details on all available models

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

### How It Works
- The script compares your local `version.txt` with the latest GitHub release tag
- If an update is available, it offers to download and install it automatically
- Your existing models are backed up before updating (with option to delete backup after successful update)
- Supports both single archive and split archive downloads seamlessly

### Manual Version Check
To check which version you have installed, look at the contents of `pretrained_models/version.txt`.
