from fastapi import Request, APIRouter, templating
from starlette.responses import HTMLResponse


router = APIRouter()
templates = templating.Jinja2Templates(directory="app/views/templates")


@router.get("/index", response_class=HTMLResponse)
async def read_item(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})