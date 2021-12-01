from fastapi import FastAPI
from pydantic import BaseMode

class movieList(BaseMode):
    ids: dict[float]
    ratings: dict[float]