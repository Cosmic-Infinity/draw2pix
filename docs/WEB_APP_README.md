# draw2pix Web Application

This web application provides a real-time drawing interface that converts flower sketches into photorealistic images using trained pix2pix GAN models.

## Features

- 🎨 **Interactive Drawing Canvas**: Draw directly in your browser with mouse or stylus
- ⚡ **Real-time Generation**: Instant conversion from sketch to photo
- 🔄 **Multiple Variations**: Generate 1-4 different outputs from a single sketch
- � **Output Diversity Controls**: 
  - Dropout mode for variation
  - Input perturbations (rotation, translation, brightness/contrast)
  - Adjustable perturbation strength (low/medium/high)
- 🔀 **Model Switching**: Load and switch between multiple trained models
- 💾 **Download Results**: Save your generated images as PNG
- ⚙️ **Adjustable Settings**: Control number of variations and generation parameters

## Quick Start

### Using the Automated Script (Windows)

The easiest way to get started:

```batch
start.bat
```

This script will:
- Check for required dependencies (installs Flask if missing)
- Download pretrained models from GitHub releases if not present
- Check for updates and offer to download new versions
- Start the web server automatically
- Open your browser to http://127.0.0.1:5000

### Manual Setup

#### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

#### 2. Download Pretrained Models

Download model files (.pth) from [GitHub Releases](https://github.com/Cosmic-Infinity/draw2pix/releases) and place them in the `pretrained_models/` directory.

#### 3. Run the Application

```bash
# Windows
start.bat

# Linux/Mac
python app/web_app.py --model_dir pretrained_models
```

#### 4. Open in Browser

Navigate to: **http://127.0.0.1:5000**

## Command Line Arguments

| Argument       | Default              | Description                                     |
| -------------- | -------------------- | ----------------------------------------------- |
| `--model_dir`  | `pretrained_models`  | Directory containing .pth model files           |
| `--input_nc`   | `1`                  | Number of input channels (1=grayscale, 3=RGB)   |
| `--output_nc`  | `3`                  | Number of output channels (3=RGB photo)         |
| `--port`       | `5000`               | Port to run the web server                      |
| `--host`       | `127.0.0.1`          | Host address (use `0.0.0.0` for network access) |

Example:
```bash
python app/web_app.py --model_dir pretrained_models --port 5000 --host 127.0.0.1
```

## How to Use

### Basic Drawing

1. **Draw your sketch** on the left canvas using your mouse or stylus
2. **Click "Generate"** to convert your sketch to a photo
3. **View the result** on the right canvas(es)
4. **Clear** the canvas to start over or **Download** your results

### Generating Multiple Variations

1. Adjust the **"Number of Variations"** slider (1-4)
2. Enable **"Enable Dropout"** for random variation in the model
3. Enable **"Perturb Input"** to apply random transformations
4. Select **perturbation strength** (Low/Medium/High) if perturbations are enabled
5. Click **"Generate"** to see multiple different results

**Note**: The first variation is always generated from your clean sketch. Perturbations are only applied to variations 2, 3, and 4.

### Model Selection

- Use the **model dropdown** at the top to switch between loaded models
- All models in the `pretrained_models/` directory are loaded at startup
- The current model is displayed in the dropdown

### Generation Settings Explained

- **Dropout Mode**: When enabled, the model uses dropout layers for randomness, creating different outputs from the same input
- **Input Perturbation**: Applies small random transformations (rotation, translation, brightness/contrast) to the input sketch
- **Perturbation Strength**:
  - **Low**: ±2° rotation, ±2px translation, ±5% brightness/contrast
  - **Medium**: ±5° rotation, ±3px translation, ±10% brightness/contrast  
  - **High**: ±10° rotation, ±5px translation, ±15% brightness/contrast

## Troubleshooting

### No Models Found

```
Error initializing models: No .pth model files found in pretrained_models
```

**Solution**: 
1. Run `start.bat` (Windows) which will automatically download models
2. Or manually download models from [GitHub Releases](https://github.com/Cosmic-Infinity/draw2pix/releases) and place them in `pretrained_models/`

### Model Loading Errors

If specific models fail to load:
- Check that the .pth files are not corrupted
- Ensure sufficient disk space
- Verify the model architecture matches (U-Net 256)

### CUDA Out of Memory

If you get CUDA memory errors:
- The app automatically falls back to CPU
- Consider loading fewer models if you have limited VRAM
- Close other GPU-intensive applications

### Slow Generation (CPU Mode)

- First generation takes 1-2 seconds for model warmup
- Subsequent generations should be faster
- Generating multiple variations (2-4) is more efficient than generating them individually
- GPU will be 5-20× faster than CPU if available

### Port Already in Use

```
OSError: [WinError 10048] Only one usage of each socket address
```

**Solution**: Use a different port:

```bash
python app/web_app.py --model_dir pretrained_models --port 5001
```

## Advanced Configuration

### Network Access (Access from Other Devices)

To make the app accessible from other devices on your network:

```bash
python app/web_app.py --host 0.0.0.0 --port 5000
```

Then access from other devices using: `http://YOUR_IP_ADDRESS:5000`

**Security Note**: Only use `0.0.0.0` on trusted networks. This makes the app accessible to anyone on your network.

### Custom Image Size

The default canvas and model size is 256×256. The model is trained for this resolution and changing it is not recommended without retraining. However, if you want to experiment:

1. The canvas size is fixed at 256×256 in `app/index.html`
2. The preprocessing always resizes to 256×256 for the model
3. Post-training upscaling would require additional processing

### Changing Input/Output Channels

If you have models trained with different settings:

```bash
# Example: RGB sketch input instead of grayscale
python app/web_app.py --model_dir pretrained_models --input_nc 3 --output_nc 3
```

**Note**: Most pix2pix flower models use grayscale input (1 channel) and RGB output (3 channels).

## Architecture

### Backend (`app/web_app.py`)

- Flask web server
- Multi-model loading and management
- Real-time model switching
- Image preprocessing pipeline with optional perturbations
- Batch inference for multiple variations
- Image postprocessing and encoding

### Frontend (`app/index.html`)

- HTML5 Canvas for drawing interface
- Vanilla JavaScript (no framework dependencies)
- Responsive design with CSS
- Model selection dropdown
- Variation controls (dropdown, sliders, toggles)
- Multiple result canvases for variations

### API Endpoints

#### `GET /`
Serves the main application page

#### `POST /generate`
Generates photo(s) from sketch

**Request:**
```json
{
  "sketch": "data:image/png;base64,...",
  "num_variations": 1-4,
  "use_dropout": boolean,
  "use_perturbation": boolean,
  "perturbation_strength": "low"|"medium"|"high"
}
```

**Response (single):**
```json
{
  "result": "data:image/png;base64,..."
}
```

**Response (multiple):**
```json
{
  "results": [
    "data:image/png;base64,...",
    "data:image/png;base64,...",
    ...
  ]
}
```

#### `GET /models`
Lists available models

**Response:**
```json
{
  "models": ["model1.pth", "model2.pth", ...],
  "current": "model1.pth"
}
```

#### `POST /models/select`
Switches the active model

**Request:**
```json
{
  "model": "model_name.pth"
}
```

**Response:**
```json
{
  "success": true,
  "current": "model_name.pth"
}
```

#### `GET /health`
Health check endpoint

**Response:**
```json
{
  "status": "ok",
  "models_loaded": 4,
  "current_model": "model_name.pth",
  "available_models": ["model1.pth", "model2.pth", ...],
  "device": "cuda:0" or "cpu"
}
```

## Development

### Testing the API Directly

You can test the generation API using curl or Python:

```python
import requests
import base64
from PIL import Image
import io

# Create or load a sketch image
sketch = Image.new('L', (256, 256), color=255)  # White canvas
# Draw something or load existing sketch
# sketch = Image.open('sketch.png').convert('L')

# Convert to base64
buffer = io.BytesIO()
sketch.save(buffer, format='PNG')
sketch_b64 = base64.b64encode(buffer.getvalue()).decode()

# Send to API with variations
response = requests.post('http://127.0.0.1:5000/generate',
    json={
        'sketch': f'data:image/png;base64,{sketch_b64}',
        'num_variations': 2,
        'use_dropout': True,
        'use_perturbation': False
    })

# Get results
result = response.json()
print(f"Generated {len(result.get('results', [result]))} variation(s)")
```

### Model Switching via API

```python
import requests

# List available models
models_response = requests.get('http://127.0.0.1:5000/models')
print(models_response.json())

# Switch to a different model
switch_response = requests.post('http://127.0.0.1:5000/models/select',
    json={'model': 'G_250e_cleanT_L85_Lr22.pth'})
print(switch_response.json())
```

### Modifying the UI

Edit `app/index.html` to customize:
- Colors and styling (CSS section at top)
- Canvas layout and arrangement
- Control options and settings
- Button text and labels
- Add new features or controls

## Performance Optimization

### GPU Acceleration
1. **Use CUDA**: Ensure PyTorch with CUDA support is installed
2. **Check GPU availability**: The app automatically detects and uses GPU if available
3. **Monitor VRAM**: Each loaded model uses ~500MB-1GB of VRAM
4. **Expected performance**:
   - GPU: 50-100ms per image
   - CPU: 500-2000ms per image

### Batch Processing
- Generating 4 variations together (~400-600ms) is faster than 4 individual generations (~400ms + overhead)
- The app automatically batches multiple variations for efficiency
- Batch size is limited to 4 variations maximum

### Model Management
- All models are loaded into memory at startup for instant switching
- This uses more RAM/VRAM but provides zero-latency model switching
- If memory is limited, consider keeping fewer model files in `pretrained_models/`

### Further Optimization
1. **TorchScript**: Convert models to TorchScript for faster inference
2. **ONNX**: Use ONNX runtime for cross-platform optimization
3. **Quantization**: INT8 quantization for 2-4× CPU speedup
4. **Half-precision**: FP16 inference on GPU for faster processing

## Production Deployment

### Important Notes
- The current setup uses Flask's development server
- **DO NOT use in production** without a proper WSGI server
- See the warning: `"This is a development server. Do not use it in a production deployment."`

### Production Setup
For production deployment, use a WSGI server like:

```bash
# Install Gunicorn
pip install gunicorn

# Run with Gunicorn (Linux/Mac)
gunicorn -w 4 -b 0.0.0.0:5000 app.web_app:app

# Or use uWSGI, Waitress (Windows-compatible), etc.
```

### Security Considerations
- Enable HTTPS/TLS
- Add authentication if needed
- Implement rate limiting
- Validate all inputs
- Use proper CORS settings
- Monitor resource usage
- See [ARCHITECTURE.md](ARCHITECTURE.md) for detailed security recommendations

## Related Documentation

- **[ARCHITECTURE.md](ARCHITECTURE.md)** - Detailed system architecture and data flow
- **[RELEASE_GUIDE.md](RELEASE_GUIDE.md)** - Guide for creating and publishing releases
- **[README.md](../README.md)** - Main project documentation

## Credits

Built on top of [pytorch-CycleGAN-and-pix2pix](https://github.com/junyanz/pytorch-CycleGAN-and-pix2pix) by Jun-Yan Zhu and Taesung Park.

## License

- **Custom Code** (app/, docs/, start.bat, etc.): [MIT License](../LICENSE)
- **pix2pix Framework** (pix2pix/): BSD 2-Clause License - See [pix2pix/THIRD_PARTY_LICENSES.txt](../pix2pix/THIRD_PARTY_LICENSES.txt)
- **Trained Models**: Created by this project (MIT License)
