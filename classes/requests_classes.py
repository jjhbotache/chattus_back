from pydantic import BaseModel


class CreateRoomRequest(BaseModel):
  fast_chat: bool
  once_view_photos_and_videos: bool
  mandatory_focus: bool