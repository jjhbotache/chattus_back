from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from conecction_manager_class import RoomConnectionManager
from typing import List, Dict
import json

from helpers import client_from_websocket, generate_room_code
from classes.requests_classes import CreateRoomRequest
from classes.msg_class import Message

app = FastAPI()

# Almacenamiento en memoria de las conexiones activas
roomConnectionManager = RoomConnectionManager()



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
    await roomConnectionManager.connect(
        websocket=websocket,
        room=room_code,
    )
    try:
        while True:
            data = await websocket.receive_text()
            parsed_data = json.loads(data)
                
            
            try: extension = parsed_data["extension"]
            except KeyError: extension = None
            
            await roomConnectionManager.broadcast(
                message=Message(
                    message=parsed_data["message"],
                    kind=parsed_data["kind"],
                    sender=websocket.id,
                    extension=extension
                    ),
                room=room_code,
            )
    except WebSocketDisconnect:
        await roomConnectionManager.disconnect(
            websocket=websocket,
            room=room_code,
        )

@app.post("/create_room")
async def create_room(createRoomData:CreateRoomRequest):
    # clean all rooms that are empty
    await roomConnectionManager.clean_rooms()
    
    room_code = generate_room_code()
    while room_code in roomConnectionManager.rooms:
        room_code = generate_room_code()
        
    roomConnectionManager.create_room(
        room_code=room_code,
        configGiven=createRoomData.__dict__
    )
        
    return JSONResponse(content={"room_code": room_code})

@app.get("/verify_room/{room_code}")
async def verify_room(room_code: str):
    if room_code in roomConnectionManager.rooms:
        room = roomConnectionManager.rooms[room_code]
        print("room")
        print(room.__dict__)
        return JSONResponse(content={
            "room_exists": True,
            "room_data": room.config
        })
    else:
        return JSONResponse(content={"room_exists": False})