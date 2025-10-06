# app/pipeline/image_processor.py
from ultralytics import YOLO
import cv2
import os


class ImageProcessor:
    def __init__(self):
        """Initialize both detection and classification models"""
        # Stage 1: Detection model
        detector_path = 'models/animal_detector.pt'
        if not os.path.exists(detector_path):
            raise FileNotFoundError(f"Animal detector not found at {detector_path}")
        
        self.animal_detector = YOLO(detector_path)
        print("✅ Animal detector loaded")
        
        # Stage 2: Classification model
        classifier_path = 'models/species_classifier.pt'
        if not os.path.exists(classifier_path):
            print("⚠️ Species classifier not found, using detection only")
            self.species_classifier = None
        else:
            self.species_classifier = YOLO(classifier_path)
            print("✅ Species classifier loaded")
    
    async def process_image(self, image_path: str) -> dict:
        """Two-stage detection: detect then classify"""
        try:
            # Stage 1: Detect animals
            detection_results = self.animal_detector(image_path, conf=0.25)
            
            detections = []
            
            for result in detection_results:
                boxes = result.boxes
                
                if len(boxes) == 0:
                    return {
                        "status": "no_animal_detected",
                        "animals_detected": 0,
                        "detections": []
                    }
                
                # Read original image for cropping
                img = cv2.imread(image_path)
                
                for box in boxes:
                    x1, y1, x2, y2 = map(int, box.xyxy[0].cpu().numpy())
                    detection_confidence = float(box.conf[0])
                    
                    # Stage 2: Classify the cropped region
                    species_name = "unknown"
                    classification_confidence = 0.0
                    
                    if self.species_classifier is not None:
                        # Crop the detected animal
                        cropped = img[y1:y2, x1:x2]
                        
                        if cropped.size > 0:  # Valid crop
                            # Save crop temporarily
                            temp_crop = f"/tmp/crop_{os.path.basename(image_path)}"
                            cv2.imwrite(temp_crop, cropped)
                            
                            # Classify
                            classify_results = self.species_classifier(temp_crop)
                            
                            # Get top prediction from classification
                            if len(classify_results) > 0:
                                probs = classify_results[0].probs
                                if probs is not None:
                                    top_class_id = probs.top1
                                    species_name = classify_results[0].names[top_class_id]
                                    classification_confidence = float(probs.top1conf)
                            
                            # Clean up
                            if os.path.exists(temp_crop):
                                os.remove(temp_crop)
                    else:
                        # Fallback: use detection class
                        class_id = int(box.cls[0])
                        species_name = result.names[class_id]
                        classification_confidence = detection_confidence
                    
                    detections.append({
                        "species": species_name,
                        "detection_confidence": detection_confidence,
                        "classification_confidence": classification_confidence,
                        "bounding_box": {
                            "x1": float(x1),
                            "y1": float(y1),
                            "x2": float(x2),
                            "y2": float(y2)
                        }
                    })
            
            return {
                "status": "animal_detected",
                "animals_detected": len(detections),
                "detections": detections
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "animals_detected": 0,
                "detections": []
            }


# Singleton
_image_processor_instance = None

def image_processor_singleton():
    global _image_processor_instance
    if _image_processor_instance is None:
        _image_processor_instance = ImageProcessor()
    return _image_processor_instance