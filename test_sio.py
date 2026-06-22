import socketio
import asyncio
import jwt
import datetime

sio = socketio.AsyncClient()

@sio.event
async def connect():
    print("CONNECTED")
    await sio.emit("join-room", {"meetingId": "B643-06C3-72E9"})

@sio.event
async def connect_error(data):
    print("ERROR:", data)

@sio.on("room-joined")
async def on_room_joined(data):
    print("JOINED ROOM:", data)
    await sio.disconnect()

async def main():
    token = jwt.encode({"sub": "1"}, "supersecret_pymeet_key_123_456_789_xyz", algorithm="HS256")
    try:
        await sio.connect("https://pymeet-backend.onrender.com", transports=["websocket"], socketio_path="/socket.io", auth={"token": "Bearer " + token})
        await sio.wait()
    except Exception as e:
        print("EXCEPTION:", e)

if __name__ == "__main__":
    asyncio.run(main())
