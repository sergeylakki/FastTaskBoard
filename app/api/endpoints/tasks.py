from typing import Annotated
from fastapi import APIRouter, Depends, Query, HTTPException
from starlette import status
from starlette.responses import HTMLResponse
from app.core.security import get_user_by_token
from app.api.schemas.task import TaskResponse, TaskCreate, TaskUpdate
from app.db.models.task import TaskRepository
from app.db.models.user import UserRepository
from fastapi.websockets import WebSocket, WebSocketDisconnect
from sqlalchemy.exc import IntegrityError

router = APIRouter()
active_connections: list[WebSocket] = []

html = """
<!DOCTYPE html>
<html>
    <head>
        <title>Chat</title>
    </head>
    <body>
        <h1>WebSocket Chat</h1>
        <form action="" onsubmit="sendMessage(event)">
            <input type="text" id="messageText" autocomplete="off"/>
            <button>Send</button>
        </form>
        <ul id='messages'>
        </ul>
        <script>
            var ws = new WebSocket("ws://localhost:8000/api/v1/ws/tasks/1");
            ws.onmessage = function(event) {
                var messages = document.getElementById('messages')
                var message = document.createElement('li')
                var content = document.createTextNode(event.data)
                message.appendChild(content)
                messages.appendChild(message)
            };
            function sendMessage(event) {
                var input = document.getElementById("messageText")
                ws.send(input.value)
                input.value = ''
                event.preventDefault()
            }
        </script>
    </body>
</html>
"""


@router.get("/")
async def get():
    return HTMLResponse(html)


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        await websocket.send_text(f"Message text was 1: {data}")


@router.websocket("/ws/tasks/{client_id}")
async def websocket_endpoint(client_id: int, websocket: WebSocket) -> None:
    await websocket.accept()
    active_connections.append(websocket)
    try:
        while True:
            message = await websocket.receive_text()
            for connection in active_connections:
                await connection.send_text(f"Client: {client_id} Message: {message}!")

    except WebSocketDisconnect:
        active_connections.remove(websocket)


@router.post("/tasks", response_model=TaskResponse)
async def create_task(task: TaskCreate,
                      username: str = Depends(get_user_by_token),
                      ) -> TaskResponse:
    user_db = await UserRepository.get_user_by_username(username)
    new_task = await TaskRepository.create_user_task(user_db.id, task.model_dump())
    try:
        for connection in active_connections:
            await connection.send_text(f"New task created: {new_task.title}")
        return new_task

    except IntegrityError:
        pass


@router.get('/tasks', response_model=list[TaskResponse])
async def tasks_list(skip: Annotated[int, Query(ge=0)] = 0,
                     limit: Annotated[int, Query(ge=0)] = 10,
                     ) -> list[TaskResponse]:
    tasks = await TaskRepository.find_some(offset=skip, limit=limit)
    return tasks


@router.get('/tasks/{task_id}', response_model=TaskResponse)
async def get_task(task_id: int) -> TaskResponse:
    task = await TaskRepository.find_one(id=task_id)
    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Task not found"
        )
    return task


@router.put('/tasks/{id}', response_model=TaskResponse)
async def update_task(id: int,
                      task_update: TaskUpdate,
                      username: str = Depends(get_user_by_token)
                      ) -> TaskResponse:
    task = await TaskRepository.edit_one_by_id(id, task_update.model_dump())
    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Task not found"
        )
    return task


@router.delete('/tasks/{id}', response_model=TaskResponse)
async def delete_task(id: int,
                      username: str = Depends(get_user_by_token)
                      ) -> str:
    task = await TaskRepository.delete_one(id)

    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Task not found"
        )

    try:
        for connection in active_connections:
            await connection.send_text(f"Task {task.id} deleted")
        return task

    except IntegrityError:
        pass
