
from typing import List, Dict
from fastapi import WebSocket
import json
import asyncio
from classes.msg_class import Message
from helpers import client_from_websocket, generate_unique_id

# max number users in room
# max secs of inactivity
# max msgs in room
# mandatory focus

class Room:
    def __init__(self, 
                 users_websockets: List[WebSocket],
                 msgs: List[Message],
                 config: Dict = None,
                 ):
        self.users_websockets = users_websockets
        self._msgs = msgs
        self.config = config if config is not None else {
            "max_number_users_in_room": 2,
            "max_secs_of_inactivity": 0,
            "max_msgs_in_room": 0,
            "mandatory_focus": False
        }
        
        

class RoomConnectionManager:
    def __init__(self):
        self.rooms: Dict[str, Room] = {}
        self.timers = {} # if needed, add a timer for a room
        
        # each key in the dictionary will be a room 
        
    def create_room(self, room_code: int, configGiven: Dict = None):
        # verify max and mins
        assert configGiven["max_number_users_in_room"] > 1 and configGiven["max_number_users_in_room"] < 10
        assert configGiven["max_secs_of_inactivity"] >= 0
        assert configGiven["max_msgs_in_room"] >= 0 and configGiven["max_msgs_in_room"] < 100
        
        
        # if the room does not exist, create it
        assert room_code not in self.rooms.keys()
        self.rooms[room_code] = Room(
            users_websockets=[],
            msgs=[],
            config=configGiven
        )
        print("Room created")
        print(self.rooms)
        
        
    async def programed_delete_room(self, room_code: str,timeout: int):
        await asyncio.sleep(timeout)
        # if the room exists, close the connections and delete the room
        if room_code in self.rooms.keys():
            for ws in self.rooms[room_code].users_websockets:
                await ws.close()
                
                
        print("deleted room: ", room_code)
        print(self.rooms[room_code].users_websockets)

    async def connect(self, websocket: WebSocket, room: str):
        assert room in self.rooms.keys()
        current_room = self.rooms[room]        
        assert len(current_room.users_websockets) < current_room.config["max_number_users_in_room"]
        
        
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
        print("disconnecting user")
        try:
            # delete its timer
            if room in self.timers.keys():
                self.timers[room].cancel()
                del self.timers[room]
                
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
            # if only one user is left in the room, tell they
            if len(self.rooms[room].users_websockets) == 1:
                await self.broadcast(
                    message=Message(
                        message="You are the only one left in the room",
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
        
        
        # first msgs parser
        # if the message is the first message and its sender is the system, do not send it
        if len(current_room._msgs) == 0  and message.sender == "System" and len(current_room.users_websockets) < 2 : return
        if len(current_room.users_websockets) > 1 and len([msg for msg in current_room._msgs if msg.sender != "System"]) < 1:
            current_room._msgs = []
        
        
        
        
        # timer reseter
        if current_room.config["max_secs_of_inactivity"] > 0 and message.sender != "System":
            # look for the timer in the timers dictionary
            if room in self.timers.keys():
                # if the timer exists, cancel it
                self.timers[room].cancel()
            
            self.timers[room] = asyncio.create_task(self.programed_delete_room(room, current_room.config["max_secs_of_inactivity"]))
        
        
        # len verification
        current_room._msgs.append(message)    
        current_room._msgs = current_room._msgs[-current_room.config["max_msgs_in_room"]:]
        
        
        
        
        #send msgs it to all users in the room
        msgs_dict_list = [msg.__dict__ for msg in current_room._msgs]
        for ws in current_room.users_websockets:
            connection_sender = ws.id
            await ws.send_json({
                "msgs":[
                    {
                        "message":msg["message"],
                        "sender":"You" if msg["sender"] == connection_sender else msg["sender"],
                        "kind":msg["kind"],
                        "extension":msg["extension"] if "extension" in msg else ""
                    } for msg in msgs_dict_list
                ]
            })
        
        
        # turn files into links
        next_file_id = 0
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