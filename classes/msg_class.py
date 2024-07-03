from typing import Literal
from pydantic import BaseModel
import json

class Message(BaseModel):
    message: str
    sender: str
    kind: Literal["message", "image" , "video" , "audio"] = "message"
