from fastapi import FastAPI, Depends, WebSocket, WebSocketDisconnect, HTTPException, Query
from sqlalchemy.orm import Session
from database import Base, engine, SessionLocal
from models import User, Notification
from auth import create_access_token, verify_token
from websocket_manager import manager
from worker import notification_worker
from notification_queue import notification_queue
import asyncio

app = FastAPI()

# ---------------------------
# Create Tables
# ---------------------------
Base.metadata.create_all(bind=engine)

# ---------------------------
# Database Dependency
# ---------------------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ---------------------------
# Start Background Worker
# ---------------------------
@app.on_event("startup")
async def startup_event():
    asyncio.create_task(notification_worker())

# ---------------------------
# Root Endpoint
# ---------------------------
@app.get("/")
def root():
    return {"message": "Notification System Backend is Running 🚀"}

# ---------------------------
# Register User
# ---------------------------
@app.post("/register")
def register(username: str, password: str, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.username == username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists")

    user = User(username=username, password=password)
    db.add(user)
    db.commit()
    db.refresh(user)

    return {"message": "User created successfully"}

# ---------------------------
# Login
# ---------------------------
@app.post("/login")
def login(username: str, password: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == username).first()

    if not user or user.password != password:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token({"sub": str(user.id)})

    return {"access_token": token}

# ---------------------------
# Create Notification (Event Simulation)
# ---------------------------
@app.post("/notify")
async def notify(user_id: int, message: str):
    await notification_queue.put({
        "user_id": user_id,
        "message": message
    })

    return {"message": "Notification added to queue"}

# ---------------------------
# Get Notifications (Pagination)
# ---------------------------
@app.get("/notifications")
def get_notifications(
    user_id: int,
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1),
    db: Session = Depends(get_db)
):
    offset = (page - 1) * limit

    notifications = db.query(Notification)\
        .filter(Notification.user_id == user_id)\
        .order_by(Notification.id.desc())\
        .offset(offset)\
        .limit(limit)\
        .all()

    return notifications

# ---------------------------
# Mark Notification as Read + Real-time Update
# ---------------------------
@app.put("/notifications/{notification_id}/read")
async def mark_read(notification_id: int, db: Session = Depends(get_db)):
    notification = db.query(Notification)\
        .filter(Notification.id == notification_id)\
        .first()

    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")

    notification.read = True
    db.commit()
    db.refresh(notification)

    # 🔥 Send real-time update
    await manager.send_notification(
        notification.user_id,
        {
            "id": notification.id,
            "message": notification.message,
            "read": True
        }
    )

    return {"message": "Notification marked as read"}

# ---------------------------
# Secure WebSocket
# ---------------------------
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, token: str):
    user_id = None  # important to prevent crash

    try:
        payload = verify_token(token)
        user_id = int(payload["sub"])

        await manager.connect(user_id, websocket)

        while True:
            # Keep connection alive
            await websocket.receive_text()

    except WebSocketDisconnect:
        if user_id is not None:
            manager.disconnect(user_id, websocket)

    except Exception:
        if user_id is not None:
            manager.disconnect(user_id, websocket)
        await websocket.close()
