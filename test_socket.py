import socketio
import asyncio

sio = socketio.AsyncClient()

@sio.event
async def connect():
    print("Connected to server")
    await sio.emit("join-room", {"meetingId": "D8AD-ACC5-495C"})
    print("Emitted join-room")

@sio.event
async def connect_error(data):
    print("Connection failed:", data)

@sio.event
async def disconnect():
    print("Disconnected from server")

@sio.on("room-joined")
async def on_room_joined(data):
    print("ROOM JOINED!", data)
    await sio.disconnect()

async def main():
    # Use dummy token from env or something, but wait, we don't have a token!
    # I can generate one!
    import jwt
    import datetime
    token = jwt.encode({"sub": "1", "exp": datetime.datetime.utcnow() + datetime.timedelta(days=1)}, "supersecret_pymeet_key_123_456_789_xyz", algorithm="HS256")
    
    await sio.connect("https://pymeet-backend.onrender.com", transports=["websocket"], socketio_path="/socket.io", auth={"token": "Bearer " + token})
    await sio.wait()

if __name__ == "__main__":
    asyncio.run(main())
