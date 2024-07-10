# Chattus Backend
## Description
Chattus backend is a server application designed to support the Chattus frontend web application. It handles room creation, management, and real-time communication between users in chat rooms. The backend is built with FastAPI and utilizes WebSockets for efficient, real-time data exchange.

![chattus api img](/chattus_back.png)

## API Endpoints
- **POST /create_room:** Allows users to create a new chat room with customizable settings such as the maximum number of users, inactivity timeout, and message limits.
- **GET /verify_room/{room_code}:** Verifies if a room with the given code exists and is accessible.
- **WebSocket /ws/{room_code}:** Establishes a WebSocket connection for real-time messaging and updates within a room.

![chattus api gif](/chattus_back.gif)

## Features
- **Room Management:** Supports creating rooms with configurable settings and cleaning up empty rooms automatically.
- **Real-Time Communication:** Utilizes WebSockets for real-time messaging and updates, ensuring a seamless chat experience.
- **Configurable Room Settings:** Allows setting maximum users, inactivity timeout, and message limits for each room.

## Technologies Used
- **FastAPI:** A modern, fast (high-performance) web framework for building APIs with Python 3.7+ that's easy to learn and use.
- **WebSockets:** For real-time bi-directional communication between clients and the server.
- **Python:** As the primary programming language, offering simplicity and versatility for web server development.
![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![WebSocket](https://img.shields.io/badge/WebSockets-FFFFFF?style=for-the-badge&logo=websockets&logoColor=black)

## Getting Started
To run the Chattus backend locally:
1. Ensure Python 3.7+ is installed.
2. Install dependencies: `pip install -r requirements.txt`
3. Run the server: `uvicorn main:app --reload`end
