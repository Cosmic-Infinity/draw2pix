# draw2pix Web Application

This web application provides a real-time drawing interface that converts your sketches into photorealistic images using your trained pix2pix model.

## Features

- 🎨 **Interactive Drawing Canvas**: Draw directly in your browser
- ⚡ **Real-time Generation**: Automatic conversion as you draw (optional)
- 🎯 **Customizable Brush**: Adjust size and color
- 💾 **Download Results**: Save your generated images
- 📱 **Mobile Support**: Touch-enabled for tablets and phones

## Setup Instructions

### 1. Install Dependencies

First, make sure you have all the required packages installed:

```powershell
# Install Flask for the web server
pip install flask

# Or install from requirements file
pip install -r requirements_webapp.txt
```

### 2. Verify Your Model

Make sure your trained model file `latest_net_G.pth` is in the project root directory.

### 3. Run the Web Application

```powershell
# Basic usage (assumes grayscale sketch input, RGB photo output)
python web_app.py --model_path latest_net_G.pth

# Custom configuration
python web_app.py --model_path latest_net_G.pth --input_nc 1 --output_nc 3 --port 5000
```

### 4. Open in Browser

Navigate to: **http://127.0.0.1:5000**

## Command Line Arguments

| Argument       | Default            | Description                                     |
| -------------- | ------------------ | ----------------------------------------------- |
| `--model_path` | `latest_net_G.pth` | Path to your trained model file                 |
| `--input_nc`   | `1`                | Number of input channels (1=grayscale, 3=RGB)   |
| `--output_nc`  | `3`                | Number of output channels (3=RGB photo)         |
| `--port`       | `5000`             | Port to run the web server                      |
| `--host`       | `127.0.0.1`        | Host address (use `0.0.0.0` for network access) |

## Usage Tips

### Auto-Generate Mode

- **Enabled (default)**: The image generates automatically after you finish each stroke
- **Disabled**: Click the "Generate Photo" button manually to create the image

### Drawing Tips

1. Start with rough outlines
2. Add details gradually
3. Use different brush sizes for variety
4. Experiment with the auto-generate toggle for better performance

### Brush Controls

- **Brush Size**: Adjust from 1-30 pixels
- **Brush Color**: Change color for different sketch styles (black is typical)

### Buttons

- **Generate Photo**: Manually trigger image generation
- **Download Result**: Save the generated photo as PNG
- **Clear Canvas**: Reset both canvases to start fresh

## Troubleshooting

### Model Not Found

```
Warning: Model file latest_net_G.pth not found!
```

**Solution**: Ensure the model file path is correct. Use absolute path if needed:

```powershell
python web_app.py --model_path "C:\path\to\your\model.pth"
```

### CUDA Out of Memory

If you get CUDA memory errors, the app will automatically fall back to CPU. For better performance on CPU:

- Reduce the frequency of auto-generation
- Use manual generation mode

### Slow Generation

- The first generation might be slow (model initialization)
- Subsequent generations should be faster
- GPU (CUDA) will be much faster than CPU if available

### Port Already in Use

```
OSError: [WinError 10048] Only one usage of each socket address
```

**Solution**: Use a different port:

```powershell
python web_app.py --port 5001
```

## Advanced Configuration

### Network Access (Access from Other Devices)

To make the app accessible from other devices on your network:

```powershell
python web_app.py --host 0.0.0.0 --port 5000
```

Then access from other devices using: `http://YOUR_IP_ADDRESS:5000`

### Custom Image Size

The default canvas size is 256x256 (matching typical pix2pix training). To modify:

1. Edit `web_app.py`: Change `target_size` parameter in `preprocess_sketch()`
2. Edit `app/index.html`: Change canvas width/height attributes

### Model Parameters

If your model was trained with different settings, adjust the parameters:

```powershell
# Example: RGB sketch input instead of grayscale
python web_app.py --input_nc 3 --output_nc 3

# Different architecture
# Edit web_app.py and modify the --netG parameter in initialize_model()
```

## Architecture

### Backend (`web_app.py`)

- Flask web server
- Model loading and inference
- Image preprocessing and postprocessing
- RESTful API endpoint for generation

### Frontend (`app/index.html`)

- HTML5 Canvas for drawing
- Vanilla JavaScript (no framework dependencies)
- Responsive design with CSS
- Real-time communication with backend

### API Endpoints

#### `GET /`

Serves the main application page

#### `POST /generate`

Generates photo from sketch

- **Input**: JSON with base64-encoded sketch image
- **Output**: JSON with base64-encoded result image

#### `GET /health`

Health check endpoint

- **Output**: Server status and model information

## Development

### Testing the API Directly

You can test the generation API using curl or Python:

```python
import requests
import base64

# Read a sketch image
with open('sketch.png', 'rb') as f:
    sketch_b64 = base64.b64encode(f.read()).decode()

# Send to API
response = requests.post('http://127.0.0.1:5000/generate',
    json={'sketch': f'data:image/png;base64,{sketch_b64}'})

# Get result
result = response.json()
print(result)
```

### Modifying the UI

Edit `app/index.html` to customize:

- Colors and styling (CSS section)
- Canvas size
- Control options
- Layout

## Performance Optimization

1. **Use GPU**: Ensure CUDA is available for faster inference
2. **Disable Auto-Generate**: Use manual mode for complex drawings
3. **Batch Processing**: Process multiple images at once (requires code modification)
4. **Model Optimization**: Consider converting to TorchScript or ONNX

## Credits

Built on top of [pytorch-CycleGAN-and-pix2pix](https://github.com/junyanz/pytorch-CycleGAN-and-pix2pix) by Jun-Yan Zhu and Taesung Park.

## License & Distribution

This web application wrapper (`web_app.py`, `app/`, and this documentation) can be licensed under your choice of license.

The underlying pix2pix model code (`models/`, `options/`, `util/`) is from the original repository and is licensed under the BSD 2-Clause License. See `THIRD_PARTY_LICENSES.txt` for complete license details.

**For deployment guidance**, including which components to ship and licensing requirements, see `DEPLOYMENT_GUIDE.md`.
