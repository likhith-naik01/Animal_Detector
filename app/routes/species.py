from fastapi import APIRouter
from typing import List, Dict

router = APIRouter()


@router.get("/species")
async def list_species() -> List[Dict]:
    return []

