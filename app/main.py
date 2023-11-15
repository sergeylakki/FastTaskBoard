import logging
import logging.config
from urllib.request import Request
from fastapi import FastAPI, File, UploadFile, BackgroundTasks, Cookie, Response, Header, Depends, staticfiles
from datetime import datetime
from typing import Annotated
from fastapi import FastAPI
from starlette.responses import JSONResponse
from app.api.endpoints.users import router as users_router
from app.api.endpoints.tasks import router as tasks_router
from app.views.views import router as views
from app.db.database import init_db


class UnicornException(Exception):
    def __init__(self, name: str):
        self.name = name


app = FastAPI()
app.include_router(views, prefix="/views", tags=["Views"])
app.include_router(users_router, prefix="/api", tags=["Users"])
app.include_router(tasks_router, prefix="/api", tags=["Tasks"])  # dependencies=[Depends(get_user_by_token)])
feedbacks = []
# logging.config.fileConfig('logging_config.ini')

app.mount("/static", staticfiles.StaticFiles(directory="static"), name="static")


@app.on_event("startup")
async def on_startup() -> None:
    await init_db()


@app.exception_handler(UnicornException)
def global_exception_handler(request: Request, exc: UnicornException) -> JSONResponse:
    logger = logging.getLogger("uvicorn.error")
    logger.exception(f"Global Exception handler raised error: {exc.name}, url: {request.full_url}")
    return JSONResponse(status_code=500, content={"error": "Internal server error"})


# #########################       Фоновые задачи     ###############################
def write_notification1(email: str, message=""):
    with open("log.txt", mode="w") as email_file:
        content = f"notification for {email}: {message}"
        email_file.write(content)


# Фоновые задачи
@app.post("/send-notification/{email}")
async def send_notification1(email: str, background_tasks: BackgroundTasks):
    background_tasks.add_task(write_notification1, email, message="some notification")
    return {"message": "Notification sent in the background"}


# #########################       Обработка формы     ###############################
# @app.post("/login/")
# async def login1(username: Annotated[str, Form()], password: Annotated[str, Form()]):
#    return {"username": username}


# #########################       Загрузка файлов    ###############################
@app.post("/files/")
async def create_file1(file: Annotated[bytes, File()]):
    return {"file_size": len(file)}


@app.post("/uploadfile/")
async def create_upload_file1(file: UploadFile):
    return {"filename": file.filename}


# #########################      Cчитывание куки    ###############################
@app.get("/cookie")
def root1(last_visit=Cookie()):
    return {"last visit": last_visit}


# #########################      Установка куки    ###############################
@app.get("/")
def root2(response: Response):
    now = datetime.now().strftime('YYYY-MM-DD')    # получаем текущую дату и время
    response.set_cookie(key="last_visit", value=now)
    return {"message": "куки установлены"}


# #########################      Удаление куки    ###############################
@app.post("/logout", status_code=204)
async def logout_user2(response: Response):
    response.delete_cookie("example_access_token")


# #########################     получние Header    ###############################
@app.get("/items/")
async def read_items1(user_agent: Annotated[str | None, Header()] = None):
    return {"User-Agent": user_agent}


# #########################     получние Header    ###############################
@app.get("/")
def root4(user_agent: str = Header()):
    return {"User-Agent": user_agent}


# #########################     установка Header    ###############################
@app.get("/")
def root5(response: Response):
    response.headers["Secret-Code"] = "123459"
    return {"message": "Hello from my api"}