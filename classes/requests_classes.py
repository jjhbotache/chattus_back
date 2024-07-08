from pydantic import BaseModel


class CreateRoomRequest(BaseModel):
  max_number_users_in_room : int
  max_secs_of_inactivity : int
  max_msgs_in_room : int
  mandatory_focus : bool