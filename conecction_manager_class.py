
from typing import List, Dict
from fastapi import WebSocket
import json
from classes.msg_class import Message

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[int, List[WebSocket]] = {}
        # each key in the dictionary will be a room code and the value will be a list of WebSocket connections
        

    async def connect(self, websocket: WebSocket, room: int, msgs: Dict[int, Message]):
        await websocket.accept()
        if room not in self.active_connections:
            self.active_connections[room] = []
            msgs[room] = []
        self.active_connections[room].append(websocket)

    def disconnect(self, websocket: WebSocket, room: int, msgs: Dict[int, Message]):
        self.active_connections[room].remove(websocket)
        if not self.active_connections[room]:
            del self.active_connections[room]
            del msgs[room]
            

    async def broadcast(self, message: Message, room: int,msgs: Dict[int, Message]):
        if room in self.active_connections:
            msgs[room].append(message)
            msgs_json_str = json.dumps([msg.__dict__ for msg in msgs[room]])
            print(msgs_json_str)
            for connection in self.active_connections[room]:
                await connection.send_text(msgs_json_str)
