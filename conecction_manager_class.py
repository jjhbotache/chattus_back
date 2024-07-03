
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
        self.msgs = msgs
        self.fast_chat = fast_chat
        self.once_view_photos_and_videos = once_view_photos_and_videos
        self.mandatory_focus = mandatory_focus
        
        

class RoomConnectionManager:
    def __init__(self):
        self.rooms: Dict[int, Room] = {}
        # each key in the dictionary will be a room 
        

    async def connect(self, websocket: WebSocket, room: str):
        await websocket.accept()
        existing_rooms = self.rooms.keys()
        if room not in existing_rooms:
            print("Creating new room", room)
            # creates a new room
            self.rooms[room] = Room(
                users_websockets=[websocket],
                msgs=[],
                fast_chat=False,
                once_view_photos_and_videos=False,
                mandatory_focus=False
            )
        else:
            print("Room already exists, connecting user to the room ", room)
            # if the room already exists, add the new user to the room
            self.rooms[room].users_websockets.append(websocket)
            print("User added to the room")
            # add a msg saying that a new user has joined the room
            self.rooms[room].msgs.append(
                Message(
                    message="A new user has joined the room",
                    sender="System",
                    kind="message"
                )
            )
            

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
        self.rooms[room].msgs.append(message)
        
        for connection in self.rooms[room].users_websockets:
            print("sending message to ", connection)
            await connection.send_json({
                "msgs":[msg.__dict__ for msg in self.rooms[room].msgs]
            })
        
