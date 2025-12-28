"""
YOLOv5 Installation and Verification Script
Run this to ensure YOLOv5 is properly installed and models are working
"""

import subprocess
import sys
import os

def install_yolov5():
    """Install YOLOv5 package"""
    print("=" * 60)
    print("Installing YOLOv5...")
    print("=" * 60)
    
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'yolov5'])
        print("✓ YOLOv5 installed successfully")
        return True
    except Exception as e:
        print(f"✗ Failed to install YOLOv5: {e}")
        return False

def verify_torch():
    """Verify PyTorch is installed"""
    print("\nVerifying PyTorch installation...")
    try:
        import torch
        print(f"✓ PyTorch version: {torch.__version__}")
        print(f"✓ CUDA available: {torch.cuda.is_available()}")
        return True
    except ImportError:
        print("✗ PyTorch not installed. Installing...")
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'torch', 'torchvision'])
            return True
        except:
            return False

def verify_models():
    """Check if model files exist"""
    print("\nVerifying model files...")
    models = {
        'accident': 'models/ACCIDENT.pt',
        'pothole': 'models/pathole_hump.pt'
    }
    
    all_exist = True
    for name, path in models.items():
        if os.path.exists(path):
            size_mb = os.path.getsize(path) / (1024 * 1024)
            print(f"✓ {name} model found: {path} ({size_mb:.2f} MB)")
        else:
            print(f"✗ {name} model NOT FOUND: {path}")
            all_exist = False
    
    return all_exist

def test_model_loading():
    """Test loading a model"""
    print("\nTesting model loading...")
    
    try:
        import torch
        model_path = 'models/ACCIDENT.pt'
        
        if not os.path.exists(model_path):
            print(f"✗ Cannot test: model file not found")
            return False
        
        print(f"Loading model: {model_path}")
        
        # Try torch hub method
        try:
            model = torch.hub.load('ultralytics/yolov5', 'custom', 
                                  path=model_path, force_reload=False, trust_repo=True)
            print("✓ Model loaded via torch.hub")
            return True
        except Exception as e:
            print(f"  Torch hub failed: {e}")
        
        # Try direct yolov5 import
        try:
            import yolov5
            model = yolov5.load(model_path)
            print("✓ Model loaded via yolov5 package")
            return True
        except Exception as e:
            print(f"  YOLOv5 package failed: {e}")
            return False
            
    except Exception as e:
        print(f"✗ Model loading test failed: {e}")
        return False

def main():
    print("\n" + "=" * 60)
    print("YOLOv5 Setup and Verification for Sanchar AI")
    print("=" * 60 + "\n")
    
    # Step 1: Verify PyTorch
    if not verify_torch():
        print("\n✗ PyTorch installation failed. Please install manually:")
        print("  pip install torch torchvision")
        return False
    
    # Step 2: Install YOLOv5
    if not install_yolov5():
        print("\n✗ YOLOv5 installation failed")
        return False
    
    # Step 3: Verify models exist
    if not verify_models():
        print("\n⚠ Warning: Some model files are missing!")
        print("  Please ensure .pt model files are in the 'models/' directory")
    
    # Step 4: Test model loading
    if test_model_loading():
        print("\n" + "=" * 60)
        print("✓ ALL CHECKS PASSED - YOLOv5 is ready!")
        print("=" * 60)
        print("\nYou can now run the application:")
        print("  python app.py")
        return True
    else:
        print("\n" + "=" * 60)
        print("⚠ Model loading test failed")
        print("=" * 60)
        print("\nTroubleshooting:")
        print("1. Ensure you have internet connection (first run downloads YOLOv5)")
        print("2. Check that model files (.pt) exist in models/ directory")
        print("3. Try running: pip install --upgrade yolov5")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
