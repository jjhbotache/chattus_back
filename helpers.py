import random
import string


def generate_room_code(length: int = 6):
    return int(''.join(random.choices(string.digits, k=length)))

def client_from_websocket(websocket):
    host, port = websocket.client
    host = host.replace(".", "")
    return "".join([host, str(port)])