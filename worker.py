from database import SessionLocal
from models import Notification
from websocket_manager import manager
from notification_queue import notification_queue

async def notification_worker():
    print("🔥 Worker started")

    while True:
        data = await notification_queue.get()
        print("📥 Worker received:", data)

        db = SessionLocal()

        notification = Notification(
            user_id=data["user_id"],
            message=data["message"],
            read=False
        )

        db.add(notification)
        db.commit()
        db.refresh(notification)

        print("📤 Sending to WebSocket for user:", data["user_id"])

        await manager.send_notification(
            data["user_id"],
            {
                "id": notification.id,
                "message": notification.message,
                "read": notification.read
            }
        )

        db.close()
