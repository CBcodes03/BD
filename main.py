from fastapi import FastAPI, HTTPException, Query, Path
from uuid import uuid4
from pydantic import BaseModel, Field
from typing import Optional, List
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.collection import ObjectId
import os

app = FastAPI()
class Task(BaseModel):
        id: str = Field(default_factory=lambda: uuid4().hex)
        title: str
        description : str
        status : str = Field(default='pending')