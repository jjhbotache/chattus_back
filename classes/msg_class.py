from typing import Literal, Optional
from pydantic import BaseModel
import json

class Message(BaseModel):
    message: str
    sender: str
    kind: Literal["message", "image" , "video" , "audio", "file"] = "message"
    extension : Optional[str] = None
