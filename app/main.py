import pathlib
from functools import lru_cache
import io
import uuid
from fastapi import (
    FastAPI,
    HTTPException,
    Depends,
    Request,
    File,
    UploadFile,
)
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.templating import Jinja2Templates
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    debug: bool = False
    echo_active: bool = True  # 👈 Fixed: bool flag, not string

    model_config = {  # 👈 Pydantic V2 syntax
        "env_file": ".env"
    }


@lru_cache
def get_settings():
    return Settings()


settings = get_settings()
DEBUG = settings.debug

BASE_DIR = pathlib.Path(__file__).parent
UPLOAD_DIR = BASE_DIR / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)  # 👈 Ensure directory exists

app = FastAPI()
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


@app.get("/", response_class=HTMLResponse)
def home_view(request: Request, settings: Settings = Depends(get_settings)):  # 👈 Fixed type
    print(settings.debug)
    return templates.TemplateResponse(
        request, "home.html", {"abc": 123}
    )


@app.post("/")
def home_detail_view():
    return {"hello": "world"}


@app.post("/img-echo/", response_class=FileResponse)
async def img_echo_view(file: UploadFile = File(...), settings: Settings = Depends(get_settings)):
    if not settings.echo_active:
        raise HTTPException(status_code=403, detail="Invalid Endpoint")  # 👈 Fixed

    contents = await file.read()  # 👈 No BytesIO needed
    fname = pathlib.Path(file.filename)
    fext = fname.suffix
    dest = UPLOAD_DIR / f"{uuid.uuid4()}{fext}"

    with open(str(dest), 'wb') as out:
        out.write(contents)

    return dest