import os
import warnings
from fastapi import FastAPI
from app.routers import interview, websockets
from dotenv import load_dotenv

warnings.filterwarnings("ignore", message="FP16 is not supported on CPU; using FP32 instead")

from fastapi.staticfiles import StaticFiles

app = FastAPI()

app.mount("/static", StaticFiles(directory="app/templates"), name="static")

app.include_router(interview.router)
app.include_router(websockets.router)
