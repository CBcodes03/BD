from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel
from typing import Optional, List

# --------------------------
# Database Setup
# --------------------------
DATABASE_URL = "sqlite:///./todo.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# --------------------------
# SQLAlchemy Model
# --------------------------
class Task(Base):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True, nullable=False)
    description = Column(String, nullable=True)
    status = Column(String, default="pending")

# --------------------------
# Pydantic Schemas
# --------------------------
class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None

class TaskResponse(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    status: str

    class Config:
        orm_mode = True

class TaskUpdate(BaseModel):
    status: str

# --------------------------
# FastAPI App and DB Dependency
# --------------------------
app = FastAPI()

# Create the database tables
Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --------------------------
# Endpoints
# --------------------------

# 🚀 1. POST /tasks - Create a new task
@app.post("/tasks", response_model=TaskResponse)
def create_task(task: TaskCreate, db: Session = Depends(get_db)):
    new_task = Task(title=task.title, description=task.description)
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    return new_task

# 🚀 2. GET /tasks - Get all tasks
@app.get("/tasks", response_model=List[TaskResponse])
def get_tasks(db: Session = Depends(get_db)):
    tasks = db.query(Task).all()
    return tasks

# 🚀 3. GET /tasks/{id} - Get a task by ID
@app.get("/tasks/{id}", response_model=TaskResponse)
def get_task(id: int, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == id).first()
    if task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return task

# 🚀 4. PUT /tasks/{id} - Update a task's status
@app.put("/tasks/{id}", response_model=TaskResponse)
def update_task(id: int, task_update: TaskUpdate, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == id).first()
    if task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

    if task_update.status not in ["pending", "in-progress", "completed"]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid status")

    task.status = task_update.status
    db.commit()
    db.refresh(task)
    return task

# 🚀 5. DELETE /tasks/{id} - Delete a task by ID
@app.delete("/tasks/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(id: int, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == id).first()
    if task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

    db.delete(task)
    db.commit()
    return None
