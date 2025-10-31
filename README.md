# draw2pix

> **Real-time draw2pix conversion** for flower drawings using pix2pix GAN  🎨 → 🌸

Transform rough sketches of flowers into photorealistic images through an interactive web interface. Built on the pix2pix architecture and trained on a custom dataset of 12k+ flower images.

![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)
![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)
![PyTorch](https://img.shields.io/badge/PyTorch-2.0+-red.svg)

---

## ✨ Features

- 🖌️ **Interactive Drawing Canvas** - Draw sketches directly in your browser
- ⚡ **Real-time Inference** - See results instantly (GPU: ~100ms, CPU: ~1-2s)
- 🎨 **Multiple Variations** - Generate up to 4 different outputs from one sketch
- 🔧 **Adjustable Perturbations** - Control output diversity with strength settings
- 🔄 **Model Switching** - Load and switch between multiple trained models

---

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/Cosmic-Infinity/draw2pix.git
   cd draw2pix
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the web application**
   ```bash
   # Windows
   start.bat
   
   # Linux/Mac
   python app/web_app.py --model_dir pretrained_models
   ```

4. **Open your browser**
   ```
   http://127.0.0.1:5000
   ```

---

## 🎯 Usage

### Web Interface

1. **Draw** your sketch on the left canvas using your mouse or stylus
2. **Click "Generate"** to convert your sketch to a photo
3. **Adjust settings** (optional):
   - Number of variations (1-4)
   - Perturbation strength (low/medium/high)
4. **Clear** the canvas to start over or save your results

### Command Line Options

```bash
python app/web_app.py [options]

Options:
  --model_dir       Directory containing .pth model files (default: pretrained_models)
  --input_nc        Input channels: 1 for grayscale, 3 for RGB (default: 1)
  --output_nc       Output channels: 3 for RGB (default: 3)
  --port            Port to run server on (default: 5000)
  --host            Host to run server on (default: 127.0.0.1)
```

---

## 🏗️ Project Structure

```
draw2pix/
├── app/
│   ├── index.html              # Frontend interface
│   ├── web_app.py              # Flask web application
│   └── test_setup.py           # Setup verification script
├── pretrained_models/          # Trained model weights
│   ├── G_100e_cleanT_L65_Lr25.pth
│   ├── G_250e_cleanT_L50_Lr10.pth
│   ├── G_250e_cleanT_L85_Lr22.pth
│   └── G_300e_dirtyT_L100_Lr20.pth
├── pix2pix/                    # Original pix2pix framework
│   ├── models/                 # Model architectures
│   ├── options/                # Configuration options
│   ├── data/                   # Data loading utilities
│   └── util/                   # Helper functions
├── docs/                       # Documentation files
│   ├── WEB_APP_README.md
│   ├── ARCHITECTURE.md
│   └── RELEASE_GUIDE.md
├── requirements.txt            # Python dependencies
└── start.bat                   # Quick start script (Windows)
```

---

## 🔬 Model Details

### Architecture
- **Base**: pix2pix (Conditional GAN)
- **Generator**: U-Net with 256x256 resolution
- **Training**: Custom flower dataset (~9.5k images)
- **Epochs**: Various models trained for 100-300 epochs

### Available Models
| Model | Epochs | Dataset | Lambda L1 | Learning Rate |
|-------|--------|---------|-----------|---------------|
| G_100e_cleanT_L65_Lr25 | 100 | Clean (9.5k+) | 65 | 0.00025 |
| G_250e_cleanT_L50_Lr10 | 250 | Clean (9.5k+) | 50 | 0.0001 |
| G_250e_cleanT_L85_Lr22 | 250 | Clean (9.5k+) | 85 | 0.00022 |
| G_300e_dirtyT_L100_Lr20 | 300 | Dirty (12.5k+) | 100 | 0.0002 |

---

## 🛠️ Technical Stack

### Backend
- **Flask** - Web framework
- **PyTorch** - Deep learning framework
- **torchvision** - Image transformations
- **Pillow** - Image processing
- **NumPy** - Numerical operations

### Frontend
- **HTML5 Canvas** - Drawing interface
- **Vanilla JavaScript** - No framework dependencies
- **CSS3** - Modern styling with gradients and animations

### Model
- **Input**: 256×256 grayscale sketch
- **Output**: 256×256 RGB photorealistic image
- **Inference Time**: ~100ms (GPU) / ~1-2s (CPU)

---

## 📖 Documentation

- **[docs/WEB_APP_README.md](docs/WEB_APP_README.md)** - Detailed web application guide
- **[docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)** - System architecture and data flow
- **[docs/RELEASE_GUIDE.md](docs/RELEASE_GUIDE.md)** - Guide for creating and publishing releases

---

## 🎓 Training Details

The models were trained on a custom dataset of flower images with the following characteristics:

- **Dataset Size**: ~9.5k manually curated image pairs
- **Resolution**: 256×256 pixels

- **Hardware**: NVIDIA A2000 12GB GPU
- **Training Time**: 100-300 epochs depending on model

**Note**: The dataset has a bias towards yellow/white flowers, which may affect color distribution in outputs.

---

## 🤝 Contributing

This is an academic project. For questions or suggestions:

1. Open an issue on GitHub
2. Check existing documentation
3. Review the Progress Tracker for known limitations

---

## 📝 License

- **Custom Code** (app/, docs/, etc.): [MIT License](LICENSE)
- **pix2pix Framework**: BSD License - See [pix2pix/THIRD_PARTY_LICENSES.txt](pix2pix/THIRD_PARTY_LICENSES.txt)
- **Trained Models**: Created by this project (MIT License)

---


## ⚠️ Known Limitations

- Output quality varies based on sketch complexity
- Model shows bias towards yellow/white flowers
- Texture details may appear stylized rather than photorealistic
- Best results with clear, simple flower sketches
- Requires good drawing to photo alignment in training data

---

## 🔮 Future Improvements?

- [ ] Expand dataset with more diverse flower colors
- [ ] Experiment with higher resolution models (512×512), and upscaling
- [ ] Add progressive rendering for better UX
- [ ] Implement model quantization for faster CPU inference
- [ ] Add mobile UI?

---

## 👥 Team

<div align="center">

This project was made in collaboration of:

<table>
<tr>
<td align="center" width="35%">
<a href="https://github.com/Cosmic-Infinity">
<img src="https://github.com/Cosmic-Infinity.png" width="100px" style="border-radius: 50%; border: 3px solid #667eea;" alt="Shubham"/>
</a>
<br />
<a href="https://github.com/Cosmic-Infinity"><b>Shubham</b></a>
<br />
<sub>🎓 Model Training<br/>🏗️ System Architecture<br/>📊 Dataset Curation</sub>
</td>
<td align="center" width="33%">
<a href="https://github.com/Sourasamanta">
<img src="https://github.com/Sourasamanta.png" width="100px" style="border-radius: 50%; border: 3px solid #764ba2;" alt="Sourajit"/>
</a>
<br />
<a href="https://github.com/Sourasamanta"><b>Sourajit</b></a>
<br />
<sub>💻 Web Application<br/>🎨 Frontend Design<br/>📊 Dataset Curation</sub>
</td>
<td align="center" width="33%">
<a href="https://github.com/Tanmandal">
<img src="https://github.com/Tanmandal.png" width="100px" style="border-radius: 50%; border: 3px solid #9333ea;" alt="Tanmay"/>
</a>
<br />
<a href="https://github.com/Tanmandal"><b>Tanmay</b></a>
<br />
<sub>🕷️ Web Scraping<br/>📊 Dataset Curation</sub>
</td>
</tr>
<tr>
<td align="center" width="33%">
<a href="https://github.com/Shiv14Shivam">
<img src="https://github.com/Shiv14Shivam.png" width="100px" style="border-radius: 50%; border: 3px solid #ec4899;" alt="Shivam"/>
</a>
<br />
<a href="https://github.com/Shiv14Shivam"><b>Shivam</b></a>
<br />
<sub>📊 Dataset Curation</sub>
</td>
<td align="center" width="33%">
<a href="https://github.com/alokkbhardwaj">
<img src="https://github.com/alokkbhardwaj.png" width="100px" style="border-radius: 50%; border: 3px solid #f59e0b;" alt="Alok"/>
</a>
<br />
<a href="https://github.com/alokkbhardwaj"><b>Alok</b></a>
<br />
<sub>📊 Dataset Curation</sub>
</td>
<td align="center" width="33%">
<a href="https://github.com/Snigdha7595">
<img src="https://github.com/Snigdha7595.png" width="100px" style="border-radius: 50%; border: 3px solid #06b6d4;" alt="Snigdha"/>
</a>
<br />
<a href="https://github.com/Snigdha7595"><b>Snigdha</b></a>
<br />
<sub>📊 Dataset Curation</sub>
</td>
</tr>
<tr>
<td align="center" width="33%">
<a href="https://github.com/upasana2202">
<img src="https://github.com/upasana2202.png" width="100px" style="border-radius: 50%; border: 3px solid #84cc16;" alt="Upasana"/>
</a>
<br />
<a href="https://github.com/upasana2202"><b>Upasana</b></a>
<br />
<sub>📊 Dataset Curation</sub>
</td>
<td align="center" width="33%">
<a href="https://github.com/urshita">
<img src="https://github.com/urshita.png" width="100px" style="border-radius: 50%; border: 3px solid #f97316;" alt="Urshita"/>
</a>
<br />
<a href="https://github.com/urshita"><b>Urshita</b></a>
<br />
<sub>📊 Dataset Curation</sub>
</td>
<td align="center" width="33%">
<a href="https://github.com/ankit9">
<img src="https://github.com/ankit9.png" width="100px" style="border-radius: 50%; border: 3px solid #ef4444;" alt="Ankit"/>
</a>
<br />
<a href="https://github.com/ankit9"><b>Ankit</b></a>
<br />
<sub></sub>
</td>
</tr>
<tr>
<td align="center" width="33%">
<a href="https://github.com/abhijeet841">
<img src="https://github.com/abhijeet841.png" width="100px" style="border-radius: 50%; border: 3px solid #8b5cf6;" alt="Abhijeet"/>
</a>
<br />
<a href="https://github.com/abhijeet841"><b>Abhijeet</b></a>
<br />
<sub></sub>
</td>
<td align="center" width="33%">
</td>
<td align="center" width="33%">
</td>
</tr>
</table>

</div>

---
