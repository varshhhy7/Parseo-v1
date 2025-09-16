import pathlib
from functools import lru_cache
from fastapi import FastAPI, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic_settings import BaseSettings  # 👈 updated import


class Settings(BaseSettings):
    debug: bool = False

    class Config:   # 👈 Capital C in Pydantic v2
        env_file = ".env"


@lru_cache
def get_settings():
    return Settings()


settings = get_settings()
DEBUG = settings.debug

BASE_DIR = pathlib.Path(__file__).parent

app = FastAPI()
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


@app.get("/", response_class=HTMLResponse)
def home_view(request: Request, settings: Settings = Depends(get_settings)):
    print(settings.debug)
    return templates.TemplateResponse(
        request, "home.html", {"abc": 123}
    )


@app.post("/")
def home_detail_view():
    return {"hello": "world"}
