"""
Database configuration and models
Supports both SQLite (development) and PostgreSQL (production)
"""
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Float, Text, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./aether_platform.db")

# Configure engine based on database type
if "sqlite" in DATABASE_URL.lower():
    # SQLite configuration (development)
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},
        echo=False
    )
else:
    # PostgreSQL configuration (production)
    # Handle connection pooling for production
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,  # Verify connections before using
        pool_recycle=300,    # Recycle connections after 5 minutes
        echo=False
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    role = Column(String, default="analyst")  # analyst, viewer
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    datasets = relationship("Dataset", back_populates="owner")
    model_runs = relationship("ModelRun", back_populates="user")


class Dataset(Base):
    __tablename__ = "datasets"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    filename = Column(String)
    file_path = Column(String)
    source_type = Column(String)  # upload, api
    api_url = Column(String, nullable=True)
    data_quality_score = Column(Float, nullable=True)
    data_integrity_score = Column(Float, nullable=True)
    row_count = Column(Integer, nullable=True)
    column_count = Column(Integer, nullable=True)
    owner_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    owner = relationship("User", back_populates="datasets")
    profiles = relationship("DataProfile", back_populates="dataset")
    model_runs = relationship("ModelRun", back_populates="dataset")


class DataProfile(Base):
    __tablename__ = "data_profiles"
    
    id = Column(Integer, primary_key=True, index=True)
    dataset_id = Column(Integer, ForeignKey("datasets.id"))
    column_name = Column(String)
    data_type = Column(String)
    missing_count = Column(Integer)
    missing_percentage = Column(Float)
    unique_count = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    dataset = relationship("Dataset", back_populates="profiles")


class ModelRun(Base):
    __tablename__ = "model_runs"
    
    id = Column(Integer, primary_key=True, index=True)
    dataset_id = Column(Integer, ForeignKey("datasets.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    model_name = Column(String)
    problem_type = Column(String)  # classification, regression
    target_column = Column(String)
    metrics = Column(Text)  # JSON string
    feature_importance = Column(Text, nullable=True)  # JSON string
    status = Column(String, default="pending")  # pending, running, completed, failed
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    
    dataset = relationship("Dataset", back_populates="model_runs")
    user = relationship("User", back_populates="model_runs")
    fairness_reports = relationship("FairnessReport", back_populates="model_run")


class FairnessReport(Base):
    __tablename__ = "fairness_reports"
    
    id = Column(Integer, primary_key=True, index=True)
    model_run_id = Column(Integer, ForeignKey("model_runs.id"))
    group_column = Column(String)
    metrics = Column(Text)  # JSON string
    bias_detected = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    model_run = relationship("ModelRun", back_populates="fairness_reports")


class AuditLog(Base):
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    action = Column(String)  # upload, model_run, view_dashboard
    resource_type = Column(String)  # dataset, model, dashboard
    resource_id = Column(Integer, nullable=True)
    details = Column(Text, nullable=True)  # JSON string
    created_at = Column(DateTime, default=datetime.utcnow)

