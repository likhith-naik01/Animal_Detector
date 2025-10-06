from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import String, Text, Date, Integer, Float, JSON, TIMESTAMP, ForeignKey, func, case
import uuid
from datetime import datetime

class Base(DeclarativeBase): 
    pass

def _uuid(): 
    return str(uuid.uuid4())

class Project(Base):
    __tablename__ = "projects"
    
    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, default=datetime.utcnow)
    user_id: Mapped[str | None] = mapped_column(String)  # For future user auth
    
    sessions: Mapped[list["Session"]] = relationship(back_populates="project", cascade="all, delete-orphan")

class Session(Base):
    __tablename__ = "sessions"
    
    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    project_id: Mapped[str] = mapped_column(ForeignKey("projects.id"), nullable=False)
    location: Mapped[str | None] = mapped_column(String(64))  # Store "lat,lng" or use PostGIS later
    start_date: Mapped[str | None] = mapped_column(Date)
    end_date: Mapped[str | None] = mapped_column(Date)
    total_images: Mapped[int] = mapped_column(Integer, default=0)
    
    project: Mapped[Project] = relationship(back_populates="sessions")
    images: Mapped[list["Image"]] = relationship(back_populates="session", cascade="all, delete-orphan")

class Image(Base):
    __tablename__ = "images"
    
    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    session_id: Mapped[str] = mapped_column(ForeignKey("sessions.id"), nullable=False)
    file_path: Mapped[str] = mapped_column(String(500), nullable=False)
    file_size: Mapped[int | None] = mapped_column(Integer)
    capture_time: Mapped[datetime | None] = mapped_column(TIMESTAMP)
    
    # AI Analysis Results
    has_animal: Mapped[bool] = mapped_column(default=False)
    animal_count: Mapped[int] = mapped_column(Integer, default=0)
    species_detected: Mapped[dict | None] = mapped_column(JSON)  # {species: confidence, bounding_boxes}
    quality_score: Mapped[float | None] = mapped_column(Float)
    
    processing_time: Mapped[float | None] = mapped_column(Float)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, default=datetime.utcnow)
    
    session: Mapped[Session] = relationship(back_populates="images")

class Species(Base):
    __tablename__ = "species"
    
    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    common_name: Mapped[str] = mapped_column(String(255), nullable=False)
    scientific_name: Mapped[str | None] = mapped_column(String(255))
    conservation_status: Mapped[str | None] = mapped_column(String(50))  # endangered, vulnerable, etc
    image_url: Mapped[str | None] = mapped_column(String(500))
