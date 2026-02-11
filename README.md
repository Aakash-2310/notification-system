Real-Time Notification System (FastAPI)
Overview

This project is a Real-Time Notification System built using FastAPI. It supports:

JWT Authentication

REST APIs

Secure WebSocket connections

Async background workers

In-memory event queue

Notification persistence (read/unread)

Pagination support

It simulates real-world notification systems used in task management and collaboration platforms.

Architecture
Components

FastAPI – API framework

SQLite / SQLAlchemy – Database

JWT – Authentication

WebSocket – Real-time notification delivery

Async Queue – Event handling

Background Worker – Notification dispatcher

System Flow

User registers and logs in

Server generates JWT token

User connects via WebSocket using token

An event (e.g., task created) triggers /notify

Event is added to async queue

Background worker:

Stores notification in DB

Sends real-time notification via WebSocket

User can:

Fetch notifications (with pagination)

Mark notification as read

Authentication

JWT-based authentication

Secure WebSocket using token validation

Token contains user_id inside sub

API Endpoints
Register
POST /register

Login
POST /login


Returns:

{
  "access_token": "JWT_TOKEN"
}

Create Notification (Event Simulation)
POST /notify

Get Notifications (Pagination)
GET /notifications?user_id=1&page=1&limit=10

Mark Notification as Read
PUT /notifications/{notification_id}/read

WebSocket
ws://localhost:8000/ws?token=YOUR_JWT_TOKEN


Authenticated via JWT

Sends real-time notification JSON:

{
  "id": 5,
  "message": "Task created",
  "read": false
}

Features Implemented

JWT Authentication

REST + WebSocket APIs

Async Background Worker

In-Memory Queue

Notification Storage (Database)

Read / Unread Status

Pagination

Secure WebSocket

Bonus (If Implemented)

Notification Preferences per user

Retry mechanism for failed notifications

Push notification mock (FCM simulation)

Unit tests

Installation
1. Clone Repository
git clone https://github.com/YOUR_USERNAME/notification-system.git
cd notification-system

2. Create Virtual Environment
python -m venv venv
venv\Scripts\activate

3. Install Dependencies
pip install -r requirements.txt

4. Run Server
uvicorn main:app --reload

Testing

Swagger UI:

http://localhost:8000/docs

Project Structure
notification-system/

main.py
models.py
database.py
auth.py
websocket_manager.py
worker.py
notification_queue.py
requirements.txt
README.md

