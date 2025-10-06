from fastapi import APIRouter, Query
from typing import Dict, List
from app.db.session import get_db_session
from app.db.models import Project, Image, Session
from app.utils.cache import cached_json, invalidate_pattern
from sqlalchemy import func, case, desc

router = APIRouter()


@router.get("/projects")
async def list_projects():
    """List all projects"""
    def _load_projects():
        with get_db_session() as db:
            projects = db.query(Project).order_by(desc(Project.created_at)).all()
            return [
                {
                    "id": p.id,
                    "name": p.name,
                    "description": p.description,
                    "created_at": p.created_at.isoformat() if p.created_at else None,
                    "session_count": len(p.sessions)
                }
                for p in projects
            ]
    
    return cached_json("projects:list", 300, _load_projects)  # Cache for 5 minutes


@router.post("/projects")
async def create_project(name: str, description: str = None):
    """Create a new project"""
    with get_db_session() as db:
        project = Project(name=name, description=description)
        db.add(project)
        db.flush()
        
        # Invalidate cache
        invalidate_pattern("projects:*")
        
        return {
            "id": project.id,
            "name": project.name,
            "description": project.description,
            "created_at": project.created_at.isoformat()
        }


@router.get("/projects/{project_id}/results")
async def get_project_results(
    project_id: str, 
    page: int = Query(1, ge=1), 
    limit: int = Query(50, ge=1, le=100)
):
    """Get paginated results for a project with caching"""
    cache_key = f"project:{project_id}:results:page:{page}:limit:{limit}"
    
    def _load_results():
        with get_db_session() as db:
            skip = (page - 1) * limit
            
            # Get images with animals
            animal_images = db.query(Image).join(Session).filter(
                Session.project_id == project_id,
                Image.has_animal == True
            ).order_by(desc(Image.created_at)).offset(skip).limit(limit).all()
            
            # Get statistics
            stats = db.query(
                func.count(Image.id).label('total_images'),
                func.count(case((Image.has_animal == True, 1))).label('animal_images'),
                func.count(func.distinct(Image.species_detected)).label('unique_species')
            ).join(Session).filter(Session.project_id == project_id).first()
            
            # Get species breakdown
            species_query = db.query(
                func.json_extract(Image.species_detected, '$.name').label('species'),
                func.count(Image.id).label('count')
            ).join(Session).filter(
                Session.project_id == project_id,
                Image.has_animal == True,
                Image.species_detected.isnot(None)
            ).group_by('species').all()
            
            species_count = {row.species: row.count for row in species_query if row.species}
            
            return {
                "images": [
                    {
                        "id": img.id,
                        "file_path": img.file_path,
                        "species": img.species_detected,
                        "quality_score": img.quality_score,
                        "animal_count": img.animal_count,
                        "created_at": img.created_at.isoformat() if img.created_at else None
                    }
                    for img in animal_images
                ],
                "pagination": {
                    "page": page,
                    "limit": limit,
                    "total": stats.total_images if stats else 0
                },
                "statistics": {
                    "total_processed": stats.total_images if stats else 0,
                    "animals_detected": stats.animal_images if stats else 0,
                    "unique_species": stats.unique_species if stats else 0,
                    "species_count": species_count
                }
            }
    
    return cached_json(cache_key, 60, _load_results)  # Cache for 1 minute


@router.get("/projects/{project_id}/sessions")
async def get_project_sessions(project_id: str):
    """Get all sessions for a project"""
    def _load_sessions():
        with get_db_session() as db:
            sessions = db.query(Session).filter(
                Session.project_id == project_id
            ).order_by(desc(Session.start_date)).all()
            
            return [
                {
                    "id": s.id,
                    "location": s.location,
                    "start_date": s.start_date.isoformat() if s.start_date else None,
                    "end_date": s.end_date.isoformat() if s.end_date else None,
                    "total_images": s.total_images
                }
                for s in sessions
            ]
    
    return cached_json(f"project:{project_id}:sessions", 300, _load_sessions)

