import random
import string

problematic_characters = [
    " ",  # Espacio
    "<",  # Menor que
    ">",  # Mayor que
    "#",  # Almohadilla, inicio de fragmento URL
    "%",  # Símbolo de porcentaje, inicio de codificación URL
    "{",  # Llave abierta
    "}",  # Llave cerrada
    "|",  # Barra vertical
    "\\", # Barra invertida
    "^",  # Circunflejo
    "~",  # Tilde
    "[",  # Corchete abierto
    "]",  # Corchete cerrado
    "`",  # Acento grave
    ";",  # Punto y coma, separador de parámetros en URL
    "/",  # Barra inclinada, separador de segmentos de ruta
    "?",  # Signo de interrogación, inicio de cadena de consulta
    ":",  # Dos puntos, separador de esquema y host
    "@",  # Arroba, separador de usuario y dominio
    "=",  # Signo igual, separador de pares clave-valor en cadena de consulta
    "&",  # Ampersand, separador de parámetros en cadena de consulta
    "$",  # Signo de dólar, carácter reservado
    "+",  # Más, puede ser interpretado como espacio en algunas codificaciones
    ",",  # Coma, separador de valores
]
def generate_room_code(length: int = 6):
    characters = string.ascii_letters + string.digits + string.punctuation
    code = ''.join(random.choices(characters, k=length))
    for char in code:
        while char in problematic_characters:
            code = code.replace(char, random.choice(characters))
            char = code[-1]
    return code

def client_from_websocket(websocket):
    host, port = websocket.client
    host = host.replace(".", "")
    return "".join([host, str(port)])