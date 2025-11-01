# Release Guide for Pretrained Models

## Overview

This guide explains how to create GitHub releases for distributing pretrained models. The `start.bat` script automatically downloads and manages these models, checking the version from the GitHub releases API and comparing it with the local `version.txt` file.

## Creating a New Release

### 1. Prepare the Models and Version File

Ensure all pretrained model files (`.pth` files) are in the `pretrained_models/` directory along with a `version.txt` file:

```
pretrained_models/
  ├── G_100e_cleanT_L65_Lr25.pth
  ├── G_250e_cleanT_L50_Lr10.pth
  ├── G_250e_cleanT_L85_Lr22.pth
  ├── G_300e_dirtyT_L100_Lr20.pth
  └── version.txt
```

**Create the version.txt file:**

```powershell
# Windows PowerShell
"v1.0.0" | Out-File -FilePath pretrained_models\version.txt -Encoding ascii -NoNewline
```

```bash
# Linux/Mac
echo -n "v1.0.0" > pretrained_models/version.txt
```

**Important:** The version string in `version.txt` must match the Git tag you'll use for the release (e.g., `v1.0.0`).

### 2. Create the ZIP Archive

**Windows (PowerShell):**

```powershell
Compress-Archive -Path pretrained_models\* -DestinationPath pretrained_models.zip -Force
```

**Linux/Mac:**

```bash
cd pretrained_models
zip ../pretrained_models.zip *.pth version.txt
cd ..
```

**Important:** The ZIP file should contain both the `.pth` files and `version.txt` directly at the root, not inside a subfolder.

### 3. Create GitHub Release

1. Go to your repository on GitHub: `https://github.com/Cosmic-Infinity/draw2pix`
2. Click on "Releases" in the right sidebar
3. Click "Draft a new release"
4. Fill in the release information:
   - **Tag version**: Use semantic versioning matching version.txt (e.g., `v1.0.0`, `v1.1.0`, `v2.0.0`)
   - **Release title**: Descriptive name (e.g., "Pretrained Models v1.0.0")
   - **Description**: Describe what models are included and any changes

Example description:

```markdown
## Pretrained Models Release v1.0.0

This release contains pretrained pix2pix models for sketch-to-image generation.

### Included Models:

- **G_100e_cleanT_L65_Lr25.pth** - 100 epochs, clean training, L1 loss 65%, LR 2.5e-4
- **G_250e_cleanT_L50_Lr10.pth** - 250 epochs, clean training, L1 loss 50%, LR 1.0e-4
- **G_250e_cleanT_L85_Lr22.pth** - 250 epochs, clean training, L1 loss 85%, LR 2.2e-4
- **G_300e_dirtyT_L100_Lr20.pth** - 300 epochs, dirty training, L1 loss 100%, LR 2.0e-4

### Installation:

Models will be automatically downloaded when running `start.bat` if not present.

### Manual Installation:

1. Download `pretrained_models.zip`
2. Extract all `.pth` files to the `pretrained_models/` directory
```

5. Upload the `pretrained_models.zip` file as a release asset
6. Click "Publish release"

**Note:** You no longer need to manually update `start.bat` - it automatically fetches the latest release version from GitHub!

## Version Numbering Guidelines

Use semantic versioning (MAJOR.MINOR.PATCH):

- **MAJOR (v2.0.0)**: Incompatible changes, new model architecture
- **MINOR (v1.1.0)**: New models added, compatible changes
- **PATCH (v1.0.1)**: Bug fixes, re-trained models with same architecture

## How the Auto-Download Works

### First-Time Setup

1. User runs `start.bat`
2. Script checks if `.pth` files exist in `pretrained_models/`
3. If missing, script fetches latest release info from GitHub API
4. Prompts user to download from GitHub releases
5. Downloads `pretrained_models.zip` from the latest release
6. Extracts all files (models and `version.txt`) to `pretrained_models/` directory root

### Version Updates

1. User runs `start.bat`
2. Script reads the version from local `pretrained_models/version.txt`
3. Script fetches latest release version from GitHub API
4. If versions differ, prompts user to update
5. Backs up current models to `pretrained_models_old_<VERSION>/` directory
6. Downloads and extracts new models to `pretrained_models/` directory
7. Asks user if they want to delete the backup (they probably won't need it)

### Version Tracking

- The `version.txt` file is included in the release ZIP and extracted with the models
- The script compares this local version with the GitHub release tag
- Old versions are backed up to `pretrained_models_old_<VERSION>/` directories
- Users can optionally delete backups to save disk space

1. When `LATEST_VERSION` in `start.bat` is updated
2. Script compares with version in `.model_version` file
3. If newer version available, prompts user to update
4. Backs up current models before downloading new ones
5. Downloads and extracts new models
6. Updates `.model_version` file

### Version Tracking

- The `.model_version` file stores the currently installed version
- This file is created in `pretrained_models/.model_version`
- It's automatically managed by `start.bat`
- Users should not modify this file manually

## Testing the Release

Before publishing:

1. **Test the ZIP structure:**

   ```powershell
   # Extract to temp directory to verify structure
   Expand-Archive -Path pretrained_models.zip -DestinationPath temp_test
   dir temp_test
   # Should show .pth files AND version.txt directly, not in a subfolder
   ```

2. **Verify version.txt content:**

   ```powershell
   Get-Content temp_test\version.txt
   # Should display the version tag, e.g., v1.0.0
   ```

3. **Test automatic download:**

   - Remove local `pretrained_models/` directory or its contents
   - Run `start.bat` and test the download process
   - Verify models are extracted to `pretrained_models/` root

4. **Test version update:**
   - Ensure old models exist with a `version.txt` file
   - Create a new release with a different version tag
   - Run `start.bat` and verify it detects the new version
   - Confirm backup directory is created correctly

## Troubleshooting

### Common Issues:

**ZIP file structure is wrong:**

- Ensure `.pth` files AND `version.txt` are at the root of the ZIP, not in a nested folder
- Re-create ZIP using the commands in step 2

**Download fails:**

- Verify the release is published (not draft)
- Ensure `pretrained_models.zip` is attached to the release as an asset
- Check your internet connection

**Models not extracted correctly:**

- Check that ZIP contains `.pth` files AND `version.txt` directly
- Verify file permissions on `pretrained_models/` directory

**version.txt missing:**

- The ZIP must include `version.txt` at the root level
- If missing, the script will create one, but it's better to include it in the ZIP

**Backup directories accumulating:**

- Old backups are kept as `pretrained_models_old_<VERSION>/`
- Users are prompted to delete them, but may choose to keep them
- Manually delete old backup directories if needed

## Best Practices

1. **Always test releases** before announcing to users
2. **Document model changes** in release notes
3. **Include version.txt** in every release ZIP
4. **Don't delete old releases** - users may need them
5. **Use semantic versioning** consistently
6. **Consider file size** - GitHub has a 2GB limit per file

## Example Release Workflow

```powershell
# 1. Ensure models and version.txt are ready
cd pretrained_models
ls *.pth
cat version.txt  # Should show v1.0.0 or similar

# 2. Create version.txt if needed
"v1.1.0" | Out-File -FilePath version.txt -Encoding ascii -NoNewline

# 3. Create ZIP with all files
cd ..
Compress-Archive -Path pretrained_models\* -DestinationPath pretrained_models.zip -Force

# 4. Verify ZIP contents
Expand-Archive -Path pretrained_models.zip -DestinationPath temp_verify
dir temp_verify
# Should show: *.pth files and version.txt
rm -r temp_verify

# 5. Create release on GitHub (use web interface)
#    - Tag: v1.1.0
#    - Upload: pretrained_models.zip
#    - Publish release

# 6. Test automatic download
rm -r pretrained_models
.\start.bat
```

## Notes

- The `version.txt` file is included in the release ZIP and extracted with models
- Old model backup directories (`pretrained_models_old_*/`) are excluded from git via `.gitignore`
- Users can manually place `.pth` files and `version.txt` without downloading
- The script automatically fetches the latest release from GitHub API (no need to update `start.bat`)
- The script creates version-specific backups before updating
- PowerShell is required for automatic download on Windows
- Users are prompted to delete old backups to save disk space
