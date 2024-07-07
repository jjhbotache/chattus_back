
from typing import List, Dict
from fastapi import WebSocket
import json
from classes.msg_class import Message
from helpers import client_from_websocket, generate_unique_id

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
        assert room in self.rooms.keys()
        await websocket.accept()
        print("rooms: ", self.rooms)
        websocket.id = generate_unique_id()
        print("User connected")
        print("ws id: ", websocket.id)
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
            

    async def disconnect(self, websocket: WebSocket, room: str):
        try:
            self.rooms[room].users_websockets.remove(websocket)
            # tell the other users that the user has left the room
            print("telling users that the user has left the room")            
            await self.broadcast(
                message=Message(
                    message="A user has left the room",
                    sender="System",
                    kind="message"
                ),
                room=room
            )
        except ValueError:
            print("User not found in the room")
        
        if len(self.rooms[room].users_websockets) < 1:
            del self.rooms[room]
            
    async def broadcast(self, message: Message, room: str):
        print("broadcasting message")
        assert room in self.rooms.keys()
        current_room = self.rooms[room]
        
        # if the message is the first message and its sender is the system, do not send it
        if len(current_room._msgs) == 0\
            and message.sender == "System"\
            and len(current_room.users_websockets) < 2 : return
        
        current_room._msgs.append(message)
        msgs_dict_list = [msg.__dict__ for msg in current_room._msgs]
        
        print("msgs_dict_list: ", msgs_dict_list)
        
        for connection in current_room.users_websockets:
            # for each websocket in the room, transform the messages to , if the message sender is the same as the websocket, change the sender to "you
            connection_sender = connection.id
            
            await connection.send_json({
                "msgs":[
                    {
                        "message":msg["message"],
                        "sender":"You" if msg["sender"] == connection_sender else msg["sender"],
                        "kind":msg["kind"],
                        "extension":msg["extension"] if "extension" in msg else ""
                    } for msg in msgs_dict_list
                ]
            })
        
        next_file_id = 0
        # once the messages have been sent, for each message that is not a text msg, turn it direction to FILE(ID) 
        for msg in current_room._msgs:
            if msg.kind != "message":
                msg.message = f"FILE({str(next_file_id)})"
                next_file_id += 1
                
        
    async def clean_rooms(self):
        rooms_to_delete = []
        for room in self.rooms.keys():
            if len(self.rooms[room].users_websockets) < 1:
                rooms_to_delete.append(room)
        
        for room in rooms_to_delete:
            del self.rooms[room]