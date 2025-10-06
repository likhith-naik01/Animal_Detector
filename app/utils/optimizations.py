import torch
from ultralytics import YOLO
from typing import Dict, Any
import os

_models: Dict[str, Any] = {}

def get_model(name: str, model_path: str) -> Any:
    """Lazy load YOLO models with device selection"""
    if name not in _models:
        device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"Loading {name} model on {device}")
        
        # Check if model file exists
        if not os.path.exists(model_path):
            print(f"Warning: Model file {model_path} not found, using placeholder")
            _models[name] = None
        else:
            _models[name] = YOLO(model_path).to(device)
    
    return _models[name]

def clear_model_cache():
    """Clear loaded models (useful for testing)"""
    global _models
    _models.clear()

def get_device_info() -> Dict[str, Any]:
    """Get device information"""
    return {
        "cuda_available": torch.cuda.is_available(),
        "device_count": torch.cuda.device_count() if torch.cuda.is_available() else 0,
        "current_device": torch.cuda.current_device() if torch.cuda.is_available() else None,
    }