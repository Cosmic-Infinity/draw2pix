# draw2pix Web App Architecture

## System Overview

```
┌─────────────────────────────────────────────────────────────┐
│                         USER BROWSER                         │
│  ┌───────────────────────────────────────────────────────┐  │
│  │                 index.html (Frontend)                  │  │
│  │  ┌──────────────┐              ┌──────────────┐      │  │
│  │  │   Drawing    │              │   Result     │      │  │
│  │  │   Canvas     │    ──────>   │   Canvas     │      │  │
│  │  │  (256x256)   │              │  (256x256)   │      │  │
│  │  └──────────────┘              └──────────────┘      │  │
│  │         │                              ▲               │  │
│  │         │ User draws                   │ Display       │  │
│  │         ▼                              │               │  │
│  │  ┌─────────────────────────────────────────────────┐  │  │
│  │  │         JavaScript Controller                   │  │  │
│  │  │  - Capture pen strokes                         │  │  │
│  │  │  - Convert canvas to base64                    │  │  │
│  │  │  - Send HTTP POST to /generate                 │  │  │
│  │  │  - Receive and display result                  │  │  │
│  │  └─────────────────────────────────────────────────┘  │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ HTTP POST /generate
                            │ { sketch: "data:image/png;base64,..." }
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    FLASK WEB SERVER                          │
│                    (app/web_app.py)                          │
│  ┌───────────────────────────────────────────────────────┐  │
│  │                 Flask Application                      │  │
│  │                                                        │  │
│  │  Route: POST /generate                                │  │
│  │    1. Receive base64 sketch                           │  │
│  │    2. Decode image                                    │  │
│  │    3. Preprocess (resize, normalize)                  │  │
│  │    4. Run inference                                   │  │
│  │    5. Postprocess result                              │  │
│  │    6. Encode to base64                                │  │
│  │    7. Return JSON response                            │  │
│  └───────────────────────────────────────────────────────┘  │
│                            │                                 │
│                            ▼                                 │
│  ┌───────────────────────────────────────────────────────┐  │
│  │              Model Inference Pipeline                  │  │
│  │                                                        │  │
│  │  preprocess_sketch():                                 │  │
│  │    - Decode base64 → PIL Image                        │  │
│  │    - Convert to grayscale (L)                         │  │
│  │    - Resize to 256x256                                │  │
│  │    - ToTensor() + Normalize [-1, 1]                   │  │
│  │    - Add batch dimension                              │  │
│  │                                                        │  │
│  │  model.netG.forward():                                │  │
│  │    - U-Net 256 architecture                           │  │
│  │    - Input: [1, 1, 256, 256] (grayscale)             │  │
│  │    - Output: [1, 3, 256, 256] (RGB)                  │  │
│  │                                                        │  │
│  │  postprocess_output():                                │  │
│  │    - Denormalize [-1,1] → [0,1]                       │  │
│  │    - Scale to [0, 255]                                │  │
│  │    - Convert to PIL Image                             │  │
│  │    - Encode to base64 PNG                             │  │
│  └───────────────────────────────────────────────────────┘  │
│                            │                                 │
│                            ▼                                 │
│  ┌───────────────────────────────────────────────────────┐  │
│  │              Pix2Pix Model (PyTorch)                   │  │
│  │                                                        │  │
│  │  Components:                                          │  │
│  │    - netG: U-Net Generator (unet_256)                 │  │
│  │    - Weights: latest_net_G.pth                        │  │
│  │    - Device: CUDA (if available) or CPU               │  │
│  │                                                        │  │
│  │  Architecture:                                        │  │
│  │    Encoder: Conv layers (downsample)                  │  │
│  │    Bottleneck: Dense representation                   │  │
│  │    Decoder: DeConv layers (upsample)                  │  │
│  │    Skip Connections: U-Net style                      │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘

## Data Flow

1. USER DRAWS on canvas
   ↓
2. JavaScript captures drawing as PNG
   ↓
3. Canvas → base64 encoded image string
   ↓
4. HTTP POST to /generate endpoint
   ↓
5. Flask receives and decodes image
   ↓
6. Preprocessing: Grayscale + Resize + Normalize
   ↓
7. PyTorch Tensor [1, 1, 256, 256]
   ↓
8. Model Inference (GPU or CPU)
   ↓
9. Output Tensor [1, 3, 256, 256]
   ↓
10. Postprocessing: Denormalize + to PIL + to base64
    ↓
11. JSON response with base64 image
    ↓
12. JavaScript displays result on result canvas

## File Structure

```

draw2pix/
├── app/
│ ├── index.html # Frontend UI
│ ├── web_app.py # Flask backend server
│ └── test_setup.py # Setup verification
├── pretrained_models/
│ └── \*.pth # Trained model weights
├── docs/
│ ├── WEB_APP_README.md # Documentation
│ ├── ARCHITECTURE.md # This file
│ └── RELEASE_GUIDE.md # Release guide
├── pix2pix/
│ ├── models/
│ │ ├── pix2pix_model.py # Model definition
│ │ └── networks.py # Network architectures
│ ├── options/
│ │ ├── base_options.py # Base configuration
│ │ └── test_options.py # Test configuration
│ ├── util/
│ │ └── util.py # Utility functions
│ └── data/
│ └── **init**.py # Data loading utilities
├── requirements.txt # Python dependencies
└── start.bat # Quick start script

```

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

### Latency Sources
1. **Canvas encoding**: ~10ms (client-side)
2. **HTTP transfer**: ~50-100ms (depends on network)
3. **Image preprocessing**: ~50ms
4. **Model inference**:
   - GPU: ~50-100ms
   - CPU: ~500-2000ms
5. **Postprocessing**: ~50ms
6. **Response transfer**: ~50-100ms
7. **Canvas rendering**: ~10ms

**Total**: ~200-300ms (GPU) or ~1-2s (CPU)

### Optimization Opportunities
- Use WebSockets instead of HTTP for lower latency
- Implement request debouncing/throttling
- Add model quantization for faster CPU inference
- Use TorchScript or ONNX for optimized inference
- Implement client-side caching
- Add progressive rendering

## Security Considerations

### Current Implementation
- Local deployment (127.0.0.1)
- Single-user usage
- No authentication

### For Production Deployment
- Add HTTPS/SSL
- Implement rate limiting
- Add authentication
- Validate input sizes
- Sanitize file uploads
- Add CORS headers properly
- Implement request timeouts
```
