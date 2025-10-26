"""
Test script to verify the web app setup is correct.
Run this before starting the web application.
"""

import sys
from pathlib import Path

def check_dependencies():
    """Check if all required packages are installed."""
    print("Checking dependencies...")
    
    missing = []
    
    try:
        import torch
        print(f"✓ PyTorch {torch.__version__}")
    except ImportError:
        missing.append("torch")
        print("✗ PyTorch not found")
    
    try:
        import flask
        print(f"✓ Flask {flask.__version__}")
    except ImportError:
        missing.append("flask")
        print("✗ Flask not found")
    
    try:
        import PIL
        print(f"✓ Pillow (PIL) {PIL.__version__}")
    except ImportError:
        missing.append("Pillow")
        print("✗ Pillow not found")
    
    try:
        import torchvision
        print(f"✓ torchvision {torchvision.__version__}")
    except ImportError:
        missing.append("torchvision")
        print("✗ torchvision not found")
    
    if missing:
        print(f"\n❌ Missing packages: {', '.join(missing)}")
        print(f"Install with: pip install {' '.join(missing)}")
        return False
    else:
        print("\n✅ All dependencies installed!")
        return True


def check_files():
    """Check if required files exist."""
    print("\nChecking files...")
    
    required_files = [
        'web_app.py',
        'app/index.html',
        'pix2pix/models/pix2pix_model.py',
        'pix2pix/options/test_options.py',
    ]
    
    missing = []
    for file in required_files:
        if Path(file).exists():
            print(f"✓ {file}")
        else:
            print(f"✗ {file}")
            missing.append(file)
    
    # Check model file (optional but recommended)
    if Path('latest_net_G.pth').exists():
        print(f"✓ latest_net_G.pth")
    else:
        print(f"⚠ latest_net_G.pth not found (optional, but needed for inference)")
    
    if missing:
        print(f"\n❌ Missing required files: {', '.join(missing)}")
        return False
    else:
        print("\n✅ All required files present!")
        return True


def check_cuda():
    """Check CUDA availability."""
    print("\nChecking CUDA...")
    
    try:
        import torch
        if torch.cuda.is_available():
            print(f"✅ CUDA available! Device: {torch.cuda.get_device_name(0)}")
            print(f"   CUDA version: {torch.version.cuda}")
            return True
        else:
            print("⚠ CUDA not available. Will use CPU (slower)")
            return True
    except:
        print("❌ Cannot check CUDA")
        return False


def main():
    """Run all checks."""
    print("="*50)
    print("  draw2pix Web App - Setup Verification")
    print("="*50)
    print()
    
    deps_ok = check_dependencies()
    files_ok = check_files()
    cuda_ok = check_cuda()
    
    print("\n" + "="*50)
    
    if deps_ok and files_ok:
        print("✅ Setup verification PASSED!")
        print("\nYou can now start the web application:")
        print("  python web_app.py --model_path latest_net_G.pth")
        print("\nOr use the quick start script:")
        print("  start_webapp.bat")
        return 0
    else:
        print("❌ Setup verification FAILED!")
        print("\nPlease fix the issues above before starting the app.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
