"""Defines connection parameters and declarative base class for SQLAlchemy"""
from sqlalchemy import engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DB_PATH = "/db/statistic.db"
engine = engine.create_engine(f"sqlite:///{DB_PATH}", echo=True)
Session = sessionmaker(bind=engine)
Base = declarative_base()
