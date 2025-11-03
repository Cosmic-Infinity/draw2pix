# draw2pix Web App Architecture

## System Overview

The draw2pix web application is a real-time sketch-to-photo conversion system that uses a pix2pix GAN model. It features a browser-based drawing interface that communicates with a Flask backend, which performs inference using PyTorch.

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         USER BROWSER                         │
│  ┌───────────────────────────────────────────────────────┐  │
│  │              index.html (Frontend UI)                  │  │
│  │  ┌──────────────┐              ┌──────────────┐      │  │
│  │  │   Drawing    │              │   Result     │      │  │
│  │  │   Canvas     │    ──────>   │   Canvas(es) │      │  │
│  │  │  (256x256)   │              │  (256x256)   │      │  │
│  │  └──────────────┘              └──────────────┘      │  │
│  │         │                              ▲               │  │
│  │         │ User draws                   │ Display       │  │
│  │         ▼                              │               │  │
│  │  ┌─────────────────────────────────────────────────┐  │  │
│  │  │         JavaScript Controller                   │  │  │
│  │  │  - Capture pen strokes on canvas               │  │  │
│  │  │  - Convert canvas to base64 PNG                │  │  │
│  │  │  - Send HTTP POST to /generate                 │  │  │
│  │  │  - Handle variations & perturbations           │  │  │
│  │  │  - Receive and display result(s)               │  │  │
│  │  │  - Model selection interface                   │  │  │
│  │  └─────────────────────────────────────────────────┘  │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ HTTP POST /generate
                            │ { sketch: base64, num_variations: 1-4,
                            │   use_dropout: bool, use_perturbation: bool }
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    FLASK WEB SERVER                          │
│                    (app/web_app.py)                          │
│  ┌───────────────────────────────────────────────────────┐  │
│  │                 Flask Application                      │  │
│  │                                                        │  │
│  │  Routes:                                              │  │
│  │    POST /generate    - Generate image from sketch    │  │
│  │    GET  /models      - List available models         │  │
│  │    POST /models/select - Switch active model         │  │
│  │    GET  /health      - Health check endpoint         │  │
│  │    GET  /            - Serve frontend HTML           │  │
│  └───────────────────────────────────────────────────────┘  │
│                            │                                 │
│                            ▼                                 │
│  ┌───────────────────────────────────────────────────────┐  │
│  │            Model Management & Inference                │  │
│  │                                                        │  │
│  │  loaded_models = {}  # All loaded .pth models        │  │
│  │  current_model_name  # Active model selection        │  │
│  │                                                        │  │
│  │  initialize_all_models():                            │  │
│  │    - Scan model_dir for .pth files                   │  │
│  │    - Load all models into memory                     │  │
│  │    - Set first model as active                       │  │
│  │                                                        │  │
│  │  preprocess_sketch():                                │  │
│  │    - Decode base64 → PIL Image                       │  │
│  │    - Convert to grayscale (L)                        │  │
│  │    - Resize to 256x256 (LANCZOS)                     │  │
│  │    - Apply perturbations (optional)                  │  │
│  │      • Random rotation (±2-10°)                      │  │
│  │      • Random translation (±2-5px)                   │  │
│  │      • Brightness/contrast adjustments               │  │
│  │    - ToTensor() + Normalize to [-1, 1]              │  │
│  │    - Add batch dimension                             │  │
│  │    - Create batch for multiple variations           │  │
│  │                                                        │  │
│  │  model.netG.forward():                               │  │
│  │    - Generator architecture (U-Net or ResNet)       │  │
│  │    - Input: [N, 1, 256, 256] (grayscale batch)      │  │
│  │    - Output: [N, 3, 256, 256] (RGB batch)           │  │
│  │    - Supports dropout for variation (train mode)    │  │
│  │                                                        │  │
│  │  postprocess_output():                               │  │
│  │    - Denormalize [-1,1] → [0,1]                      │  │
│  │    - Clamp and scale to [0, 255]                     │  │
│  │    - Convert CHW → HWC (PyTorch → PIL format)        │  │
│  │    - Convert to PIL Image (RGB)                      │  │
│  │    - Encode to base64 PNG                            │  │
│  └───────────────────────────────────────────────────────┘  │
│                            │                                 │
│                            ▼                                 │
│  ┌───────────────────────────────────────────────────────┐  │
│  │              Pix2Pix Model (PyTorch)                   │  │
│  │                                                        │  │
│  │  Components:                                          │  │
│  │    - netG: Generator (auto-detected from filename)  │  │
│  │      Supported: unet_256, unet_128,                 │  │
│  │                 resnet_9blocks, resnet_6blocks      │  │
│  │    - Weights: *.pth files in pretrained_models/     │  │
│  │    - Device: CUDA (if available) or CPU              │  │
│  │    - init_type: normal (Gaussian initialization)     │  │
│  │    - Detection: Filename prefix (U256_, R9_, etc.)  │  │
│  │                                                        │  │
│  │  Architecture Examples:                              │  │
│  │                                                        │  │
│  │  U-Net 256:                                          │  │
│  │    Input Layer: 1 channel (grayscale)                │  │
│  │    Encoder: 8 Conv layers (downsample)               │  │
│  │    Bottleneck: Dense representation                  │  │
│  │    Decoder: 8 DeConv layers (upsample)               │  │
│  │    Skip Connections: U-Net style concatenation       │  │
│  │    Output Layer: 3 channels (RGB)                    │  │
│  │    Activation: Tanh (output normalized to [-1,1])    │  │
│  │                                                        │  │
│  │  ResNet (9 blocks):                                  │  │
│  │    Input Layer: 1 channel (grayscale)                │  │
│  │    Downsampling: 2 Conv layers (stride 2)           │  │
│  │    Residual Blocks: 9 ResNet blocks                  │  │
│  │    Upsampling: 2 Transposed Conv layers (stride 2)  │  │
│  │    Output Layer: 3 channels (RGB)                    │  │
│  │    Activation: Tanh (output normalized to [-1,1])    │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘

## Data Flow

### Single Image Generation (Basic Flow)
1. User draws on HTML5 canvas (256×256)
   ↓
2. JavaScript captures drawing as PNG
   ↓
3. Canvas converted to base64 encoded image string
   ↓
4. HTTP POST to `/generate` endpoint with JSON payload:
   ```json
   {
     "sketch": "data:image/png;base64,...",
     "num_variations": 1,
     "use_dropout": false,
     "use_perturbation": false
   }
   ```
   ↓
5. Flask receives and validates request
   ↓
6. Preprocessing pipeline:
   - Decode base64 → PIL Image
   - Convert to grayscale (1 channel)
   - Resize to 256×256 (LANCZOS interpolation)
   - Normalize to [-1, 1] range
   - Convert to PyTorch tensor [1, 1, 256, 256]
   ↓
7. Model inference:
   - Load current active model (from loaded_models dict)
   - Forward pass through generator (U-Net or ResNet)
   - Output tensor [1, 3, 256, 256] in [-1, 1] range
   ↓
8. Postprocessing pipeline:
   - Denormalize [-1, 1] → [0, 1]
   - Clamp values and scale to [0, 255]
   - Convert CHW → HWC format
   - Convert to PIL RGB Image
   - Encode to base64 PNG
   ↓
9. JSON response sent to client:
   ```json
   {
     "result": "data:image/png;base64,..."
   }
   ```
   ↓
10. JavaScript decodes and displays result on result canvas

### Multiple Variations (Advanced Flow)
When `num_variations > 1`:
- Creates batch of N preprocessed tensors [N, 1, 256, 256]
- If `use_perturbation=true`: applies random transformations to inputs 2-N
  (rotation, translation, brightness/contrast) while keeping input 1 clean
- If `use_dropout=true`: sets model to train mode to enable dropout randomness
- Processes entire batch in one forward pass
- Returns array of results:
  ```json
  {
    "results": [
      "data:image/png;base64,...",
      "data:image/png;base64,...",
      "data:image/png;base64,...",
      "data:image/png;base64,..."
    ]
  }
  ```

### Model Switching Flow
1. GET `/models` → Returns list of available models and current selection
2. User selects model from dropdown
3. POST `/models/select` with `{"model": "model_name.pth"}`
4. Server updates `current_model_name` and `opt` global variables
5. Subsequent `/generate` requests use the newly selected model

## File Structure

```
draw2pix/
├── app/
│   ├── index.html               # Frontend UI with drawing canvas
│   ├── web_app.py               # Flask backend server
│   └── test_setup.py            # Setup verification script
├── pretrained_models/
│   └── *.pth                    # Trained model weights (downloaded from releases)
├── pix2pix/                     # Original pix2pix framework
│   ├── models/
│   │   ├── __init__.py
│   │   ├── pix2pix_model.py     # Pix2Pix model wrapper
│   │   ├── base_model.py        # Base model class
│   │   └── networks.py          # Network architectures (U-Net, etc.)
│   ├── options/
│   │   ├── __init__.py
│   │   ├── base_options.py      # Base configuration options
│   │   └── test_options.py      # Test/inference options
│   ├── util/
│   │   ├── __init__.py
│   │   └── util.py              # Utility functions
│   └── data/
│       └── __init__.py          # Data loading utilities
├── docs/
│   ├── WEB_APP_README.md        # Web app documentation
│   ├── ARCHITECTURE.md          # This file - system architecture
│   └── RELEASE_GUIDE.md         # Guide for creating releases
├── requirements.txt             # Python dependencies
└── start.bat                    # Quick start script (Windows)
```

### Key Files Description

**app/web_app.py**
- Main Flask application server
- Handles HTTP routes and API endpoints
- Manages model loading and inference
- Implements preprocessing/postprocessing pipelines
- Supports multiple model management

**app/index.html**
- Single-page web interface
- HTML5 canvas for drawing
- JavaScript for interaction and API calls
- CSS for styling and responsive design
- No external frontend frameworks

**pix2pix/models/networks.py**
- Defines U-Net generator architecture
- Implements network initialization
- Provides building blocks for model construction

**start.bat**
- Windows quick start script
- Checks for Flask installation
- Downloads models from GitHub releases if missing
- Auto-opens browser to http://127.0.0.1:5000
- Starts Flask development server

## Technology Stack

### Frontend
- **HTML5 Canvas**: Drawing interface
- **Vanilla JavaScript**: No frameworks, pure JS
- **CSS3**: Styling and responsive design
- **Fetch API**: HTTP communication

### Backend
- **Flask**: Web framework
- **PyTorch**: Deep learning framework
- **PIL (Pillow)**: Image processing
- **NumPy**: Numerical operations

### Model
- **Architecture**: U-Net 256
- **Framework**: PyTorch
- **Type**: Pix2Pix (conditional GAN)
- **Input**: 256x256 grayscale sketch
- **Output**: 256x256 RGB photo

## Performance Considerations

### Latency Breakdown
1. **Canvas encoding**: ~10-20ms (client-side)
2. **HTTP transfer (request)**: ~10-50ms (local network)
3. **Image preprocessing**: ~30-50ms
4. **Model inference**:
   - GPU (CUDA): ~50-100ms
   - CPU: ~500-2000ms (varies by processor)
5. **Postprocessing**: ~20-30ms
6. **HTTP transfer (response)**: ~10-50ms
7. **Canvas rendering**: ~10-20ms

**Total Latency**: 
- GPU: ~150-350ms
- CPU: ~600-2200ms

### Batch Processing (Multiple Variations)
- Processing 4 variations together (~400-600ms GPU) is much faster than
  processing them individually (4 × 100ms = ~400ms + overhead)
- Batch processing leverages GPU parallelism efficiently
- Only minimal overhead added for batch operations

### Optimization Opportunities
- **Model Optimization**:
  - TorchScript compilation for faster inference
  - ONNX conversion for cross-platform deployment
  - Model quantization (INT8) for 2-4× speedup on CPU
  - Half-precision (FP16) inference on GPU

- **Network Optimization**:
  - WebSockets instead of HTTP for lower latency
  - Progressive rendering during inference
  - Client-side caching of generated images

- **Application Optimization**:
  - Request debouncing/throttling
  - Background worker threads for inference
  - GPU memory pooling
  - Preloading models at startup (already implemented)

### Memory Usage
- **Model weights**: ~200-300MB per .pth file (loaded into RAM/VRAM)
- **Runtime memory**:
  - GPU: ~500MB-1GB VRAM per model
  - CPU: ~300-500MB RAM per model
- **Multiple models**: All models loaded in memory for instant switching
- **Recommendation**: 8GB+ RAM, 4GB+ VRAM (if using GPU)

## Security Considerations

### Current Implementation (Development)
- **Local deployment only**: Binds to 127.0.0.1 (localhost)
- **No authentication**: Single-user, trusted environment
- **Debug mode**: Flask debug server for development
- **No input validation**: Trusts client input
- **No rate limiting**: Unlimited requests

### For Production Deployment

#### Essential Security Measures
1. **HTTPS/TLS**:
   - Use production WSGI server (Gunicorn, uWSGI)
   - Configure SSL/TLS certificates
   - Enforce HTTPS-only connections

2. **Authentication & Authorization**:
   - Implement user authentication
   - Add API key validation
   - Session management
   - Role-based access control (if multi-user)

3. **Input Validation**:
   - Validate image format and size
   - Limit file upload size (e.g., 5MB max)
   - Sanitize base64 input
   - Validate request parameters (num_variations, etc.)

4. **Rate Limiting**:
   - Limit requests per IP/user
   - Throttle expensive operations
   - Implement request queuing
   - Add CAPTCHA for public access

5. **Security Headers**:
   - CORS configuration (proper origin whitelist)
   - Content Security Policy
   - X-Frame-Options
   - X-Content-Type-Options

6. **Resource Protection**:
   - Request timeouts (prevent hanging)
   - Memory limits per request
   - GPU resource allocation limits
   - Error handling without information leakage

7. **Monitoring & Logging**:
   - Request logging
   - Error tracking
   - Performance monitoring
   - Security audit logs

### Deployment Architecture Example
```
Internet → Load Balancer (HTTPS) → Reverse Proxy (Nginx)
           ↓
       Gunicorn/uWSGI Workers
           ↓
       Flask Application
           ↓
       PyTorch Model (GPU/CPU)
```
```
