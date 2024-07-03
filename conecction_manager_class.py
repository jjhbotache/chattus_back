
from typing import List, Dict
from fastapi import WebSocket
import json
from classes.msg_class import Message

class Room:
    def __init__(self, 
                 users_websockets: List[WebSocket],
                 msgs: List[Message],
                 fast_chat:bool,
                 once_view_photos_and_videos:bool,
                 mandatory_focus:bool
                 ):
        self.users_websockets = users_websockets
        self._msgs = msgs
        self.fast_chat = fast_chat
        self.once_view_photos_and_videos = once_view_photos_and_videos
        self.mandatory_focus = mandatory_focus
        
        

class RoomConnectionManager:
    def __init__(self):
        self.rooms: Dict[str, Room] = {}
        # each key in the dictionary will be a room 
        
    def create_room(self, room_code: int, fast_chat:bool = False, once_view_photos_and_videos:bool = False, mandatory_focus:bool = False):
        # if the room does not exist, create it
        assert room_code not in self.rooms.keys()
        self.rooms[room_code] = Room(
            users_websockets=[],
            msgs=[],
            fast_chat=fast_chat,
            once_view_photos_and_videos=once_view_photos_and_videos,
            mandatory_focus=mandatory_focus
        )
        print("Room created")
        print(self.rooms)

    async def connect(self, websocket: WebSocket, room: str):
        await websocket.accept()
        existing_rooms = self.rooms.keys()
        if room in existing_rooms:
            self.rooms[room].users_websockets.append(websocket)
            print("User added to the room")
            # add a msg saying that a new user has joined the room
            await self.broadcast(
                message=Message(
                    message="A new user has joined the room",
                    sender="System",
                    kind="message"
                ),
                room=room
            )
        else:
            raise ValueError("Room does not exist")
            

    def disconnect(self, websocket: WebSocket, room: str):
        try:
            self.rooms[room].users_websockets.remove(websocket)
        except ValueError:
            print("User not found in the room")
        
        if len(self.rooms[room].users_websockets) < 1:
            del self.rooms[room]
            

    async def broadcast(self, message: Message, room: str):
        print("broadcasting message")
        assert room in self.rooms.keys()
        self.rooms[room]._msgs.append(message)
        
        for connection in self.rooms[room].users_websockets:
            print("sending message to ", connection)
            await connection.send_json({
                "msgs":[msg.__dict__ for msg in self.rooms[room]._msgs]
            })
        
    async def clean_rooms(self):
        rooms_to_delete = []
        for room in self.rooms.keys():
            if len(self.rooms[room].users_websockets) < 1:
                rooms_to_delete.append(room)
        
        for room in rooms_to_delete:
            del self.rooms[room]