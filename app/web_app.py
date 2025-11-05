"""
Flask web application for real-time draw2pix conversion using pix2pix model.

AUTO-DETECTED PARAMETERS (from model state_dict):
✅ --netG (architecture): Detected from filename prefix (U256_, U128_, R9_, R6_)
✅ --input_nc (input channels): Detected from model.1.weight shape [ngf, input_nc, k, k]
✅ --output_nc (output channels): Detected from final conv layer shape
✅ --norm (normalization): Detected from presence of num_batches_tracked
    - 'batch' or 'sync_batch' → detected as 'batch' (same behavior for inference)
    - 'instance' or 'sync_instance' → detected as 'instance' (same behavior for inference)
✅ --no_dropout (dropout flag): Detected from ResNet conv_block max layer index
✅ --ngf (generator filters): Detected from model.1.weight shape [ngf, input_nc, k, k]

NOT TRACKED (training-only parameters, don't affect inference):
❌ --lr, --beta1, --gan_mode, --lambda_L1, --n_epochs, --batch_size, etc.

NOT TRACKED (discriminator parameters, not used in inference):
❌ --ndf, --n_layers_D (discriminator not loaded during inference)

NOT TRACKED (initialization parameters, overridden by loaded weights):
❌ --init_type, --init_gain (weights loaded from file override initialization)
"""

from flask import Flask, render_template, request, jsonify
import torch
import numpy as np
from PIL import Image
import io
import base64
from pathlib import Path
import argparse
import glob
import sys
from pathlib import Path

# Add parent directory to path for pix2pix imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import the model infrastructure
from pix2pix.models.pix2pix_model import Pix2PixModel
from pix2pix.options.test_options import TestOptions
import torchvision.transforms as transforms

app = Flask(__name__, template_folder='.')

# Global variables to hold models
loaded_models = {}  # Dictionary to store all loaded models
current_model_name = None
opt = None


def find_model_files(directory='.'):
    """Find all .pth model files in the specified directory."""
    model_files = glob.glob(str(Path(directory) / '*.pth'))
    return sorted([Path(f).name for f in model_files])


def detect_architecture_from_filename(filename):
    """
    Detect the generator architecture from the model filename.
    
    Expected filename prefixes:
    - U256_* or u256_* → unet_256
    - U128_* or u128_* → unet_128
    - R9_* or r9_* → resnet_9blocks
    - R6_* or r6_* → resnet_6blocks
    
    Args:
        filename (str): Model filename (e.g., "U256_model.pth")
    
    Returns:
        str: One of 'unet_256', 'unet_128', 'resnet_9blocks', 'resnet_6blocks', or None if unable to detect
    """
    filename_lower = filename.lower()
    
    # Check for architecture prefixes
    if filename_lower.startswith('u256_'):
        return 'unet_256'
    elif filename_lower.startswith('u128_'):
        return 'unet_128'
    elif filename_lower.startswith('r9_'):
        return 'resnet_9blocks'
    elif filename_lower.startswith('r6_'):
        return 'resnet_6blocks'
    else:
        return None


def detect_model_config_from_state_dict(model_path):
    """
    Detect input/output channels, normalization type, dropout setting, ngf, and ndf from the model's state dictionary.
    
    Returns:
        dict: Configuration with 'input_nc', 'output_nc', 'norm', 'use_dropout', 'ngf', 'ndf' if detectable
    """
    try:
        state_dict = torch.load(model_path, map_location='cpu', weights_only=True)
        config = {}
        
        # Detect input_nc and ngf from first conv layer
        # Try multiple possible keys for different architectures:
        # - ResNet: model.1.weight shape is [ngf, input_nc, 7, 7]
        # - UNet: model.model.0.weight shape is [inner_nc, input_nc, 4, 4] (outermost downconv)
        # Some models might have additional prefixes like 'module.' for DataParallel
        first_conv_keys = [
            'model.model.0.weight',  # UNet
            'model.1.weight',         # ResNet
            'module.model.model.0.weight',  # UNet with DataParallel
            'module.model.1.weight',        # ResNet with DataParallel
        ]
        
        first_conv_key = None
        for key in first_conv_keys:
            if key in state_dict:
                first_conv_key = key
                break
        
        # If still not found, search for any key that looks like a first conv
        if first_conv_key is None:
            for key in state_dict.keys():
                if 'weight' in key and state_dict[key].dim() == 4:
                    # Found a conv layer, likely the first one
                    first_conv_key = key
                    break
        
        if first_conv_key:
            shape = state_dict[first_conv_key].shape
            config['input_nc'] = shape[1]  # Second dimension is input channels
            # For UNet, ngf is typically half of inner_nc (first layer), but we can infer from later layers
            # For ResNet, shape[0] is ngf directly
            if 'model.1.weight' in state_dict or 'module.model.1.weight' in state_dict:
                config['ngf'] = shape[0]
        
        # Detect output channels from last conv/transpose conv layer
        # For UNet: model.model.X.weight where X is the outermost upconv (ConvTranspose2d)
        # For ResNet: last conv layer before Tanh
        output_nc_key = None
        
        # Try to find the output layer more intelligently
        # UNet: Look for upconv in outermost layer (near beginning of state dict after downconv)
        # The outermost upconv is typically model.model.2.weight (after downconv at 0, submodule at 1)
        if 'model.model.2.weight' in state_dict:
            shape = state_dict['model.model.2.weight'].shape
            if shape[1] == 3 or shape[1] == 1:  # ConvTranspose2d: output is dim 1
                config['output_nc'] = shape[1]
                output_nc_key = 'model.model.2.weight'
        
        # Fallback: search from the end for likely output layer
        if 'output_nc' not in config:
            for key in reversed(list(state_dict.keys())):
                if 'weight' in key and len(state_dict[key].shape) == 4:
                    shape = state_dict[key].shape
                    # For Conv2d: output channels are dim 0
                    # For ConvTranspose2d: output channels are dim 1
                    if shape[0] == 3 or shape[0] == 1:
                        config['output_nc'] = shape[0]
                        break
                    elif shape[1] == 3 or shape[1] == 1:
                        config['output_nc'] = shape[1]
                        break
        
        # Detect normalization type by checking for num_batches_tracked
        # BatchNorm/SyncBatchNorm has num_batches_tracked, InstanceNorm/SyncInstanceNorm does not
        has_batch_tracked = any('num_batches_tracked' in key for key in state_dict.keys())
        
        if has_batch_tracked:
            config['norm'] = 'batch'
        else:
            config['norm'] = 'instance'
        
        # Detect dropout usage by checking the maximum layer index in residual blocks
        max_conv_block_index = -1
        for key in state_dict.keys():
            if 'conv_block.' in key:
                parts = key.split('.')
                try:
                    cb_idx = parts.index('conv_block')
                    if cb_idx + 1 < len(parts):
                        layer_idx = int(parts[cb_idx + 1])
                        max_conv_block_index = max(max_conv_block_index, layer_idx)
                except (ValueError, IndexError):
                    continue
        
        # Determine if dropout is used based on max index
        if max_conv_block_index >= 0:
            config['use_dropout'] = max_conv_block_index > 5
        
        return config
    except Exception as e:
        print(f'⚠️  Warning: Could not detect config from state dict: {str(e)}')
        import traceback
        traceback.print_exc()
        return {}
        return {}


def load_single_model(model_path, input_nc=None, output_nc=None, netG=None):
    """Load a single pix2pix model with the trained weights.
    
    Args:
        model_path: Path to the .pth model file
        input_nc: Number of input channels (None=auto-detect, 1=grayscale, 3=RGB)
        output_nc: Number of output channels (None=auto-detect, typically 3=RGB)
        netG: Generator architecture (None=auto-detect from filename)
    """
    
    # Verify model file exists first
    if not Path(model_path).exists():
        raise FileNotFoundError(f'Model file not found: {model_path}\nPlease ensure the model file exists in the specified location.')
    
    model_filename = Path(model_path).name
    
    # Auto-detect architecture if not specified
    if netG is None:
        netG = detect_architecture_from_filename(model_filename)
        if netG is None:
            print(f'⚠️  Could not auto-detect architecture from filename, using default: unet_256')
            netG = 'unet_256'
    
    # Detect input/output channels, normalization, ngf from the model file itself
    model_config = detect_model_config_from_state_dict(model_path)
    
    # Use auto-detected values if not explicitly specified
    if input_nc is None and 'input_nc' in model_config:
        input_nc = model_config['input_nc']
        print(f'   🔍 Auto-detected input_nc={input_nc}')
    elif input_nc is None:
        input_nc = 1  # Fallback default for sketch-to-photo
        print(f'   ⚠️  Could not detect input_nc, using default: {input_nc}')
    
    if output_nc is None and 'output_nc' in model_config:
        output_nc = model_config['output_nc']
        print(f'   🔍 Auto-detected output_nc={output_nc}')
    elif output_nc is None:
        output_nc = 3  # Fallback default for RGB output
        print(f'   ⚠️  Could not detect output_nc, using default: {output_nc}')
    
    # Use detected parameters with defaults
    norm = model_config.get('norm', 'instance')
    use_dropout = model_config.get('use_dropout', True)
    ngf = model_config.get('ngf', 64)
    
    # Print configuration summary
    config_parts = [
        f"arch={netG}",
        f"in={input_nc}",
        f"out={output_nc}",
        f"norm={norm}",
        f"ngf={ngf}" if ngf != 64 else None,
        "no_dropout" if not use_dropout else "dropout"
    ]
    config_str = ", ".join(part for part in config_parts if part is not None)
    print(f'   📋 Config: {config_str}')
    
    # Create a minimal options object
    parser = argparse.ArgumentParser()
    model_opt = TestOptions().initialize(parser)
    
    # Set the required parameters
    args = [
        '--dataroot', '.',
        '--name', 'sketch2photo',
        '--model', 'pix2pix',
        '--netG', netG,
        '--direction', 'AtoB',
        '--dataset_mode', 'single',
        '--norm', norm,
        '--input_nc', str(input_nc),
        '--output_nc', str(output_nc),
        '--ngf', str(ngf),
        '--load_size', '256',
        '--crop_size', '256',
        '--preprocess', 'none',
        '--epoch', 'none',
    ]
    
    if not use_dropout:
        args.append('--no_dropout')
    
    model_opt = model_opt.parse_args(args)
    model_opt.num_threads = 0
    model_opt.batch_size = 1
    model_opt.serial_batches = True
    model_opt.no_flip = True
    model_opt.display_id = -1
    model_opt.isTrain = False
    model_opt.device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    
    # Create model
    model = Pix2PixModel(model_opt)
    
    # Initialize the network architecture manually
    from pix2pix.models import networks
    model.netG = networks.init_net(model.netG, model_opt.init_type, model_opt.init_gain)
    
    # Load the trained weights
    state_dict = torch.load(model_path, map_location=model_opt.device, weights_only=False)
    
    if hasattr(state_dict, '_metadata'):
        del state_dict._metadata
    
    model.netG.load_state_dict(state_dict)
    model.netG.eval()
    
    return model, model_opt


def initialize_all_models(model_dir='.', input_nc=None, output_nc=None, netG=None):
    """Initialize all pix2pix models found in the directory.
    
    Args:
        model_dir: Directory containing .pth model files
        input_nc: Number of input channels (None=auto-detect per model)
        output_nc: Number of output channels (None=auto-detect per model)
        netG: Generator architecture (None=auto-detect per model)
    """
    global loaded_models, current_model_name, opt
    
    # Find all .pth files
    model_files = find_model_files(model_dir)
    
    if not model_files:
        raise FileNotFoundError(f'No .pth model files found in {model_dir}')
    
    print(f'\n📦 Found {len(model_files)} model(s) in {model_dir}')
    print('━' * 70)
    
    # Load all models - each will auto-detect its architecture if netG not specified
    for idx, model_file in enumerate(model_files, 1):
        model_path = Path(model_dir) / model_file
        print(f'\n[{idx}/{len(model_files)}] Loading: {model_file}')
        try:
            model, model_opt = load_single_model(str(model_path), input_nc, output_nc, netG)
            loaded_models[model_file] = {
                'model': model,
                'opt': model_opt
            }
            device_info = f"on {model_opt.device}"
            print(f'   ✅ Success {device_info}')
        except Exception as e:
            error_msg = str(e).split('\n')[0]  # First line only
            print(f'   ❌ Failed: {error_msg}')
    
    if not loaded_models:
        raise RuntimeError('No models could be loaded successfully')
    
    # Set the first model as current
    current_model_name = list(loaded_models.keys())[0]
    opt = loaded_models[current_model_name]['opt']
    
    print('\n' + '━' * 70)
    print(f'✅ Loaded {len(loaded_models)}/{len(model_files)} model(s) successfully')
    print(f'⚡ Active model: {current_model_name}')
    if len(loaded_models) > 1:
        print(f'📋 Available: {", ".join(loaded_models.keys())}')
    return loaded_models


def preprocess_sketch(image_data, target_size=256, add_perturbation=False, perturbation_strength='medium', input_nc=1):
    """Convert base64 image data to tensor suitable for the model with optional perturbations."""
    # Decode base64 image
    img_bytes = base64.b64decode(image_data.split(',')[1])
    img = Image.open(io.BytesIO(img_bytes))
    
    # Convert to appropriate format based on input channels
    if input_nc == 1:
        img = img.convert('L')  # Grayscale
    elif input_nc == 3:
        img = img.convert('RGB')  # RGB
    else:
        raise ValueError(f'Unsupported input_nc: {input_nc}')
    
    # Resize to model input size
    img = img.resize((target_size, target_size), Image.LANCZOS)
    
    # Apply perturbations if requested
    if add_perturbation:
        # Determine perturbation parameters based on strength
        strength_params = {
            'low': {'rotate': 2, 'translate': 2, 'brightness': 0.05, 'contrast': 0.05},
            'medium': {'rotate': 5, 'translate': 3, 'brightness': 0.1, 'contrast': 0.1},
            'high': {'rotate': 10, 'translate': 5, 'brightness': 0.15, 'contrast': 0.15}
        }
        params = strength_params.get(perturbation_strength, strength_params['medium'])
        
        # Random rotation
        angle = np.random.uniform(-params['rotate'], params['rotate'])
        img = img.rotate(angle, fillcolor=255)
        
        # Random translation
        dx = np.random.randint(-params['translate'], params['translate'] + 1)
        dy = np.random.randint(-params['translate'], params['translate'] + 1)
        img = Image.fromarray(np.roll(np.roll(np.array(img), dx, axis=1), dy, axis=0))
        
        # Random brightness/contrast
        from PIL import ImageEnhance
        brightness_factor = 1.0 + np.random.uniform(-params['brightness'], params['brightness'])
        contrast_factor = 1.0 + np.random.uniform(-params['contrast'], params['contrast'])
        
        enhancer = ImageEnhance.Brightness(img)
        img = enhancer.enhance(brightness_factor)
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(contrast_factor)
    
    # Convert to tensor and normalize to [-1, 1]
    if input_nc == 1:
        transform = transforms.Compose([
            transforms.ToTensor(),
            transforms.Normalize((0.5,), (0.5,))
        ])
    else:  # input_nc == 3
        transform = transforms.Compose([
            transforms.ToTensor(),
            transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))
        ])
    
    img_tensor = transform(img).unsqueeze(0)  # Add batch dimension
    return img_tensor


def postprocess_output(output_tensor):
    """Convert model output tensor to base64 image."""
    # Convert from [-1, 1] to [0, 255]
    output_tensor = (output_tensor + 1) / 2.0
    output_tensor = output_tensor.clamp(0, 1)
    
    # Convert to numpy array
    output_np = output_tensor.squeeze(0).cpu().detach().numpy()
    output_np = np.transpose(output_np, (1, 2, 0))  # CHW to HWC
    output_np = (output_np * 255).astype(np.uint8)
    
    # Convert to PIL Image
    img = Image.fromarray(output_np)
    
    # Convert to base64
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    img_base64 = base64.b64encode(buffer.getvalue()).decode()
    
    return f'data:image/png;base64,{img_base64}'


@app.route('/')
def index():
    """Serve the main page."""
    return render_template('index.html')


@app.route('/generate', methods=['POST'])
def generate():
    """Generate photorealistic image from sketch."""
    try:
        data = request.json
        sketch_data = data.get('sketch')
        num_variations = data.get('num_variations', 1)
        use_dropout = data.get('use_dropout', False)
        use_perturbation = data.get('use_perturbation', False)
        perturbation_strength = data.get('perturbation_strength', 'medium')
        
        if not sketch_data:
            print("❌ No sketch data provided")
            return jsonify({'error': 'No sketch data provided'}), 400
        
        # Get current model
        if not current_model_name or current_model_name not in loaded_models:
            return jsonify({'error': 'No model selected'}), 400
        
        current_model = loaded_models[current_model_name]['model']
        current_opt = loaded_models[current_model_name]['opt']
        model_input_nc = current_opt.input_nc
        
        # Compact status line
        mode_info = "dropout" if use_dropout else "no_dropout"
        perturb_info = f"perturb({perturbation_strength})" if use_perturbation else "perturb(none)"
        print(f"🎨 [{current_model_name}] {num_variations}x | {mode_info} | {perturb_info} | {model_input_nc}→{current_opt.output_nc}ch")
        
        # Set model mode
        if use_dropout:
            current_model.netG.train()
        else:
            current_model.netG.eval()
        
        # Generate multiple variations with different preprocessing if requested
        if num_variations > 1:
            input_tensors = []
            for i in range(num_variations):
                apply_perturb = use_perturbation and i > 0
                tensor = preprocess_sketch(
                    sketch_data, 
                    target_size=current_opt.crop_size,
                    add_perturbation=apply_perturb,
                    perturbation_strength=perturbation_strength,
                    input_nc=model_input_nc
                )
                input_tensors.append(tensor)
            input_batch = torch.cat(input_tensors, dim=0).to(current_opt.device)
        else:
            input_batch = preprocess_sketch(
                sketch_data, 
                target_size=current_opt.crop_size,
                add_perturbation=use_perturbation,
                perturbation_strength=perturbation_strength,
                input_nc=model_input_nc
            ).to(current_opt.device)
        
        # Generate images directly using the generator network
        with torch.no_grad():
            output_batch = current_model.netG(input_batch)
        
        # Postprocess and return all results
        if num_variations > 1:
            results = []
            for i in range(num_variations):
                output_base64 = postprocess_output(output_batch[i:i+1])
                results.append(output_base64)
            
            print(f"   ✅ Done ({num_variations} variations)")
            return jsonify({'results': results})
        else:
            output_base64 = postprocess_output(output_batch)
            print(f"   ✅ Done")
            return jsonify({'result': output_base64})
    
    except Exception as e:
        import traceback
        error_msg = str(e).split('\n')[0]
        print(f'   ❌ Error: {error_msg}')
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@app.route('/models', methods=['GET'])
def get_models():
    """Get list of available models."""
    return jsonify({
        'models': list(loaded_models.keys()),
        'current': current_model_name
    })


@app.route('/models/select', methods=['POST'])
def select_model():
    """Select a different model."""
    global current_model_name, opt
    
    data = request.json
    model_name = data.get('model')
    
    if not model_name:
        return jsonify({'error': 'No model name provided'}), 400
    
    if model_name not in loaded_models:
        return jsonify({'error': f'Model {model_name} not found'}), 404
    
    current_model_name = model_name
    opt = loaded_models[current_model_name]['opt']
    
    print(f'🔄 Switched to: {current_model_name}')
    return jsonify({
        'success': True,
        'current': current_model_name
    })


@app.route('/health')
def health():
    """Health check endpoint."""
    return jsonify({
        'status': 'ok',
        'models_loaded': len(loaded_models),
        'current_model': current_model_name,
        'available_models': list(loaded_models.keys()),
        'device': str(opt.device) if opt else 'not initialized'
    })


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='draw2pix Web App')
    parser.add_argument('--model_dir', type=str, default='pretrained_models',
                        help='Directory containing .pth model files (default: pretrained_models)')
    parser.add_argument('--input_nc', type=int, default=None,
                        help='Number of input channels (None=auto-detect, 1=grayscale, 3=RGB). Leave unspecified to auto-detect from model.')
    parser.add_argument('--output_nc', type=int, default=None,
                        help='Number of output channels (None=auto-detect, typically 3=RGB). Leave unspecified to auto-detect from model.')
    parser.add_argument('--netG', type=str, default=None,
                        help='Generator architecture: unet_256, unet_128, resnet_9blocks, resnet_6blocks. If not specified, will auto-detect from model file.')
    parser.add_argument('--port', type=int, default=5000,
                        help='Port to run the server on')
    parser.add_argument('--host', type=str, default='127.0.0.1',
                        help='Host to run the server on')
    
    args = parser.parse_args()
    
    # Initialize all models
    print('� Initializing draw2pix Web App...')
    try:
        initialize_all_models(args.model_dir, args.input_nc, args.output_nc, args.netG)
    except Exception as e:
        print(f'\n❌ Error: {str(e)}')
        print('💡 Make sure you have .pth model files in the specified directory')
        exit(1)
    
    # Run the Flask app
    print(f'\n🌐 Starting server at http://{args.host}:{args.port}')
    print('Press Ctrl+C to stop\n')
    app.run(host=args.host, port=args.port, debug=True, use_reloader=False)
