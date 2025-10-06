import asyncio
import time
from typing import List
import os

from app.pipeline.image_processor import image_processor_singleton


class BatchProcessor:
    def __init__(self):
        self.image_processor = None
    
    async def _get_processor(self):
        """Lazy load image processor"""
        if self.image_processor is None:
            self.image_processor = image_processor_singleton()
        return self.image_processor
    
    async def process_batch(self, image_paths: List[str], project_id: str) -> dict:
        """Process multiple images in batch"""
        results = {
            "total_images": len(image_paths),
            "animals_detected": 0,
            "empty_images": 0,
            "low_quality": 0,
            "species_count": {},
            "processing_time": None
        }
        
        start_time = time.time()
        
        processor = await self._get_processor()
        
        # Process images concurrently
        tasks = [self._process_single_image(img_path, project_id, processor) 
                for img_path in image_paths]
        batch_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Aggregate results
        for result in batch_results:
            if isinstance(result, Exception):
                results["low_quality"] += 1
                continue
                
            if result.get("status") == "animal_detected":
                results["animals_detected"] += 1
                species = result.get("species", {}).get("name", "Unknown")
                results["species_count"][species] = results["species_count"].get(species, 0) + 1
            elif result.get("status") == "no_animal":
                results["empty_images"] += 1
            else:
                results["low_quality"] += 1
        
        results["processing_time"] = time.time() - start_time
        
        return results
    
    async def _process_single_image(self, img_path: str, project_id: str, processor) -> dict:
        """Process a single image"""
        try:
            result = await processor.process_image(img_path)
            return result
        except Exception as e:
            return {"status": "error", "error": str(e)}


# Singleton instance
_batch_processor_instance = None


def batch_processor_singleton():
    """Get or create batch processor singleton"""
    global _batch_processor_instance
    if _batch_processor_instance is None:
        _batch_processor_instance = BatchProcessor()
    return _batch_processor_instance