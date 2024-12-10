from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
from pymongo import MongoClient
from bson import ObjectId
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI()

# MongoDB connection
MONGO_URI = os.getenv("MONGO_URI")
if not MONGO_URI:
    raise ValueError("MONGO_URI not found in environment variables")

client = MongoClient(MONGO_URI)
db = client["taskdb"]  # Database name

# Task model
class Task(BaseModel):
    title: str
    description: Optional[str] = None
    status: str

@app.get("/")
async def root():
    return {"message": "Connected to MongoDB Atlas!"}

# Create a Task
@app.post("/tasks")
async def create_task(task: Task):
    result = db.tasks.insert_one(task.dict())
    return {"message": "Task created", "task_id": str(result.inserted_id)}

# Get All Tasks
@app.get("/tasks")
async def get_tasks():
    tasks = list(db.tasks.find({}, {"_id": 0}))  # Exclude MongoDB ObjectId
    return {"tasks": tasks}

# Update a Task
@app.put("/tasks/{task_id}")
async def update_task(task_id: str, task: Task):
    if not ObjectId.is_valid(task_id):
        raise HTTPException(status_code=400, detail="Invalid task ID")
    result = db.tasks.update_one(
        {"_id": ObjectId(task_id)},
        {"$set": task.dict()}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"message": "Task updated"}

# Delete a Task
@app.delete("/tasks/{task_id}")
async def delete_task(task_id: str):
    if not ObjectId.is_valid(task_id):
        raise HTTPException(status_code=400, detail="Invalid task ID")
    result = db.tasks.delete_one({"_id": ObjectId(task_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"message": "Task deleted"}
