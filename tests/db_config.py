"""Configuration for temporary database used in tests"""
from sqlalchemy import create_engine

from data.models import Session

engine = create_engine("sqlite:///:memory:")
session = Session(bind=engine)
