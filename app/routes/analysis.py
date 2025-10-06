from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import List
import os
import uuid
from PIL import Image

from app.pipeline.image_processor import image_processor_singleton

router = APIRouter()

# Allowed image formats
ALLOWED_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.webp', '.bmp', '.tiff', '.gif'}


@router.post("/analyze/single")
async def analyze_single_image(file: UploadFile = File(...)):
    """
    Analyze single image - supports PNG, JPG, JPEG, WEBP, BMP, TIFF
    Automatically converts to JPG for YOLO processing
    """
    # Validate file extension
    file_ext = os.path.splitext(file.filename)[1].lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file format. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"
        )
    
    temp_dir = "/tmp"
    os.makedirs(temp_dir, exist_ok=True)
    
    # Generate unique filename with original extension
    unique_filename = f"{uuid.uuid4()}_{file.filename}"
    temp_path = os.path.join(temp_dir, unique_filename)
    
    try:
        # Save uploaded file
        with open(temp_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Convert to JPG if needed (YOLO works best with JPG)
        processing_path = temp_path
        if file_ext != '.jpg' and file_ext != '.jpeg':
            try:
                img = Image.open(temp_path)
                # Convert RGBA to RGB (for PNG with transparency)
                if img.mode in ('RGBA', 'LA', 'P'):
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                    img = background
                elif img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # Save as JPG
                jpg_filename = f"{uuid.uuid4()}_converted.jpg"
                processing_path = os.path.join(temp_dir, jpg_filename)
                img.save(processing_path, 'JPEG', quality=95)
            except Exception as e:
                raise HTTPException(
                    status_code=400,
                    detail=f"Failed to process image: {str(e)}"
                )
        
        # Process image with YOLO
        processor = image_processor_singleton()
        result = await processor.process_image(processing_path)
        
        return {
            "success": True,
            "data": result,
            "filename": file.filename,
            "original_format": file_ext,
            "file_size": len(content)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        return {"success": False, "error": str(e)}
    finally:
        # Cleanup temporary files
        for path in [temp_path, processing_path]:
            if path and os.path.exists(path) and path != temp_path:
                try:
                    os.remove(path)
                except Exception:
                    pass
        if os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except Exception:
                pass


@router.post("/analyze/batch")
async def analyze_batch_images(files: List[UploadFile] = File(...)):
    """
    Analyze multiple images - supports all image formats
    Returns processing results for each image
    """
    results = []
    
    for file in files:
        # Validate format
        file_ext = os.path.splitext(file.filename)[1].lower()
        if file_ext not in ALLOWED_EXTENSIONS:
            results.append({
                "filename": file.filename,
                "success": False,
                "error": f"Invalid format: {file_ext}"
            })
            continue
        
        temp_dir = "/tmp"
        os.makedirs(temp_dir, exist_ok=True)
        
        unique_filename = f"{uuid.uuid4()}_{file.filename}"
        temp_path = os.path.join(temp_dir, unique_filename)
        processing_path = temp_path
        
        try:
            # Save file
            with open(temp_path, "wb") as buffer:
                content = await file.read()
                buffer.write(content)
            
            # Convert if needed
            if file_ext != '.jpg' and file_ext != '.jpeg':
                img = Image.open(temp_path)
                if img.mode in ('RGBA', 'LA', 'P'):
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                    img = background
                elif img.mode != 'RGB':
                    img = img.convert('RGB')
                
                jpg_filename = f"{uuid.uuid4()}_converted.jpg"
                processing_path = os.path.join(temp_dir, jpg_filename)
                img.save(processing_path, 'JPEG', quality=95)
            
            # Process
            processor = image_processor_singleton()
            result = await processor.process_image(processing_path)
            
            results.append({
                "filename": file.filename,
                "success": True,
                "data": result,
                "original_format": file_ext
            })
            
        except Exception as e:
            results.append({
                "filename": file.filename,
                "success": False,
                "error": str(e)
            })
        finally:
            # Cleanup
            for path in [temp_path, processing_path]:
                if path and os.path.exists(path):
                    try:
                        os.remove(path)
                    except Exception:
                        pass
    
    # Summary statistics
    total = len(results)
    successful = sum(1 for r in results if r.get("success"))
    
    return {
        "success": True,
        "total_files": total,
        "processed": successful,
        "failed": total - successful,
        "results": results
    }