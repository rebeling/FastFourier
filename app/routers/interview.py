from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from app.analysis import get_interview_question

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/", response_class=HTMLResponse)
async def get_home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@router.post("/start-interview", response_class=HTMLResponse)
async def start_interview(job_title: str = Form(...), topic: str = Form(None)):
    question = await get_interview_question(job_title, topic)
    return HTMLResponse(content=question)
