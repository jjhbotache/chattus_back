from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from conecction_manager_class import RoomConnectionManager
from typing import List, Dict
import json

from helpers import client_from_websocket, generate_room_code
from classes.msg_class import Message

app = FastAPI()

# Almacenamiento en memoria de las conexiones activas
manager = RoomConnectionManager()



# Configuración de CORS
origins = [
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def get():
    return JSONResponse(content={"message": "Hello World"})

@app.websocket("/ws/{room_code}")
async def websocket_endpoint(websocket: WebSocket, room_code: str):
    assert room_code is not None and len(room_code) > 5 
    await manager.connect(
        websocket=websocket,
        room=room_code,
    )
    await websocket.send_json({"message": "success"})
    try:
        while True:
            data = await websocket.receive_text()
            parsed_data = json.loads(data)
            await manager.broadcast(
                message=Message(
                    message=parsed_data["message"],
                    kind=parsed_data["kind"],
                    sender=client_from_websocket(websocket)
                    ),
                room=room_code,
            )
    except WebSocketDisconnect:
        manager.disconnect(
            websocket=websocket,
            room=room_code,
        )
        await manager.broadcast(
            message=Message(
                message="Se ha desconectado",
                sender="Servidor",
                kind="message"
            ),
            room=room_code,
        )

@app.get("/create_room")
async def create_room():
    room_code = generate_room_code()
    while room_code in manager.rooms:
        room_code = generate_room_code()
    return JSONResponse(content={"room_code": room_code})