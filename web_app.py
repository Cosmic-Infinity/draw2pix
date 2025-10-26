"""
Flask web application for real-time draw2pix conversion using pix2pix model.
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

# Import the model infrastructure
from pix2pix.models.pix2pix_model import Pix2PixModel
from pix2pix.options.test_options import TestOptions
import torchvision.transforms as transforms

app = Flask(__name__, template_folder='app')

# Global variables to hold models
loaded_models = {}  # Dictionary to store all loaded models
current_model_name = None
opt = None


def find_model_files(directory='.'):
    """Find all .pth model files in the specified directory."""
    model_files = glob.glob(str(Path(directory) / '*.pth'))
    return sorted([Path(f).name for f in model_files])


def load_single_model(model_path, input_nc=1, output_nc=3):
    """Load a single pix2pix model with the trained weights."""
    
    # Verify model file exists first
    if not Path(model_path).exists():
        raise FileNotFoundError(f'Model file not found: {model_path}\nPlease ensure the model file exists in the specified location.')
    
    # Create a minimal options object
    parser = argparse.ArgumentParser()
    model_opt = TestOptions().initialize(parser)
    
    # Set the required parameters
    args = [
        '--dataroot', '.',  # dummy value
        '--name', 'sketch2photo',
        '--model', 'pix2pix',
        '--netG', 'unet_256',
        '--direction', 'AtoB',
        '--dataset_mode', 'single',
        '--norm', 'batch',
        '--input_nc', str(input_nc),
        '--output_nc', str(output_nc),
        '--no_dropout',
        '--load_size', '256',
        '--crop_size', '256',
        '--preprocess', 'none',  # No preprocessing for real-time
        '--epoch', 'none',  # Don't load from checkpoints
    ]
    
    model_opt = model_opt.parse_args(args)
    model_opt.num_threads = 0
    model_opt.batch_size = 1
    model_opt.serial_batches = True
    model_opt.no_flip = True
    model_opt.display_id = -1
    model_opt.isTrain = False
    model_opt.device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    
    # Create model (but don't call setup which tries to load from checkpoints)
    model = Pix2PixModel(model_opt)
    
    # Initialize the network architecture manually
    from pix2pix.models import networks
    model.netG = networks.init_net(model.netG, model_opt.init_type, model_opt.init_gain)
    
    # Load the trained weights directly
    print(f'Loading model from {model_path}')
    state_dict = torch.load(model_path, map_location=model_opt.device, weights_only=False)
    
    # Handle different state dict formats
    if hasattr(state_dict, '_metadata'):
        del state_dict._metadata
    
    model.netG.load_state_dict(state_dict)
    model.netG.eval()
    
    print(f'Model loaded successfully on device: {model_opt.device}')
    return model, model_opt


def initialize_all_models(model_dir='.', input_nc=1, output_nc=3):
    """Initialize all pix2pix models found in the directory."""
    global loaded_models, current_model_name, opt
    
    # Find all .pth files
    model_files = find_model_files(model_dir)
    
    if not model_files:
        raise FileNotFoundError(f'No .pth model files found in {model_dir}')
    
    print(f'Found {len(model_files)} model(s): {", ".join(model_files)}')
    print('Loading all models into memory...')
    
    # Load all models
    for model_file in model_files:
        model_path = Path(model_dir) / model_file
        try:
            model, model_opt = load_single_model(str(model_path), input_nc, output_nc)
            loaded_models[model_file] = {
                'model': model,
                'opt': model_opt
            }
            print(f'✓ Loaded: {model_file}')
        except Exception as e:
            print(f'✗ Failed to load {model_file}: {str(e)}')
    
    if not loaded_models:
        raise RuntimeError('No models could be loaded successfully')
    
    # Set the first model as current
    current_model_name = list(loaded_models.keys())[0]
    opt = loaded_models[current_model_name]['opt']
    
    print(f'\nAll models loaded! Current model: {current_model_name}')
    print(f'Available models: {list(loaded_models.keys())}')
    return loaded_models
    return model, opt


def preprocess_sketch(image_data, target_size=256, add_perturbation=False, perturbation_strength='medium'):
    """Convert base64 image data to tensor suitable for the model with optional perturbations."""
    # Decode base64 image
    img_bytes = base64.b64decode(image_data.split(',')[1])
    img = Image.open(io.BytesIO(img_bytes)).convert('L')  # Convert to grayscale
    
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
    transform = transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize((0.5,), (0.5,))
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
        print("Received generation request")
        data = request.json
        sketch_data = data.get('sketch')
        num_variations = data.get('num_variations', 1)  # Default to 1 for backward compatibility
        use_dropout = data.get('use_dropout', False)  # Enable dropout for variations
        use_perturbation = data.get('use_perturbation', False)  # Enable input perturbations
        perturbation_strength = data.get('perturbation_strength', 'medium')  # low/medium/high
        
        if not sketch_data:
            print("Error: No sketch data provided")
            return jsonify({'error': 'No sketch data provided'}), 400
        
        # Get current model
        if not current_model_name or current_model_name not in loaded_models:
            return jsonify({'error': 'No model selected'}), 400
        
        current_model = loaded_models[current_model_name]['model']
        current_opt = loaded_models[current_model_name]['opt']
        
        print(f"Using model: {current_model_name}")
        print(f"Generating {num_variations} variation(s)...")
        print(f"Dropout: {use_dropout}, Perturbation: {use_perturbation} ({perturbation_strength})")
        
        # Set model mode based on dropout flag
        if use_dropout:
            current_model.netG.train()  # Enable dropout
            print("Model set to train mode (dropout enabled)")
        else:
            current_model.netG.eval()  # Disable dropout
            print("Model set to eval mode (dropout disabled)")
        
        # Generate multiple variations with different preprocessing if requested
        if num_variations > 1:
            input_tensors = []
            for i in range(num_variations):
                # First variation (index 0) is always clean/unperturbed
                # Perturbation is only applied to variations 2, 3, 4... (indices 1, 2, 3...)
                apply_perturb = use_perturbation and i > 0
                tensor = preprocess_sketch(
                    sketch_data, 
                    target_size=current_opt.crop_size,
                    add_perturbation=apply_perturb,
                    perturbation_strength=perturbation_strength
                )
                input_tensors.append(tensor)
            input_batch = torch.cat(input_tensors, dim=0).to(current_opt.device)
        else:
            input_batch = preprocess_sketch(
                sketch_data, 
                target_size=current_opt.crop_size,
                add_perturbation=use_perturbation,
                perturbation_strength=perturbation_strength
            ).to(current_opt.device)
        
        print(f"Input batch shape: {input_batch.shape}")
        print(f"Running model inference (batch size: {num_variations})...")
        # Generate images directly using the generator network
        with torch.no_grad():
            output_batch = current_model.netG(input_batch)
        print(f"Output batch shape: {output_batch.shape}")
        
        print("Postprocessing outputs...")
        # Postprocess and return all results
        if num_variations > 1:
            results = []
            for i in range(num_variations):
                output_base64 = postprocess_output(output_batch[i:i+1])
                results.append(output_base64)
            
            print(f"Generation successful! ({num_variations} variations)")
            return jsonify({'results': results})
        else:
            output_base64 = postprocess_output(output_batch)
            print("Generation successful!")
            return jsonify({'result': output_base64})
    
    except Exception as e:
        import traceback
        print(f'Error during generation: {str(e)}')
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
    
    print(f'Switched to model: {current_model_name}')
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
    parser.add_argument('--input_nc', type=int, default=1,
                        help='Number of input channels (1 for grayscale sketch, 3 for RGB)')
    parser.add_argument('--output_nc', type=int, default=3,
                        help='Number of output channels (3 for RGB photo)')
    parser.add_argument('--port', type=int, default=5000,
                        help='Port to run the server on')
    parser.add_argument('--host', type=str, default='127.0.0.1',
                        help='Host to run the server on')
    
    args = parser.parse_args()
    
    # Initialize all models
    print('Initializing models...')
    try:
        initialize_all_models(args.model_dir, args.input_nc, args.output_nc)
        print('All models initialized successfully!')
    except Exception as e:
        print(f'Error initializing models: {str(e)}')
        print('Make sure you have .pth model files in the specified directory')
        exit(1)
    
    # Run the Flask app
    print(f'Starting server on http://{args.host}:{args.port}')
    app.run(host=args.host, port=args.port, debug=True, use_reloader=False)
