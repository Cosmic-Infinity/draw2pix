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

## Versioning & Auto-Update

Each release is tracked with a version number stored in `version.txt`. The auto-update feature (Windows only, via `start.bat`) checks your current version against the latest release and prompts you to update if a newer version is available.
