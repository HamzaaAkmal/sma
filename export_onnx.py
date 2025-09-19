"""
Export YOLO model to ONNX format for browser deployment
"""

from ultralytics import YOLO
import os
import torch

def export_model_to_onnx():
    """Export the trained YOLO model to ONNX format"""

    model_path = "best.pt"
    onnx_path = "best.onnx"

    print(f"Checking for model file: {model_path}")
    if not os.path.exists(model_path):
        print(f"Error: Model file {model_path} not found")
        return False

    try:
        print("PyTorch version:", torch.__version__)
        print("Loading YOLO model...")
        model = YOLO(model_path)
        print("Model loaded successfully")

        # Export to ONNX
        print("Exporting to ONNX...")
        success = model.export(format='onnx', opset=11, verbose=True)

        print(f"Export result: {success}")

        if os.path.exists(onnx_path):
            print(f"✅ Model exported successfully to {onnx_path}")
            print(f"File size: {os.path.getsize(onnx_path)} bytes")
            return True
        else:
            print("❌ Export failed - ONNX file not found")
            return False

    except Exception as e:
        print(f"❌ Export failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    export_model_to_onnx()
