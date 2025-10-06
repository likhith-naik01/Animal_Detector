# app/routes/batch.py
from fastapi import APIRouter, UploadFile, File
from typing import List
import os
import uuid

from app.pipeline.batch_processor import batch_processor_singleton  # This should work now

router = APIRouter()

@router.post("/analyze/batch")
async def analyze_batch_images(files: List[UploadFile] = File(...)):
    # Your batch processing code here
    pass