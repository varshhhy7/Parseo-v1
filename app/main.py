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


# --- Configuration Management ---
# Loads application settings from environment variables or .env file.
# Provides type-safe access to config values like `debug` and `echo_active`.
class Settings(BaseSettings):
    debug: bool = False          # Enables debug mode if set to True
    echo_active: bool = True     # Controls whether image echo endpoint is active

    model_config = {
        "env_file": ".env"       # Specifies the .env file to load settings from
    }


# Caches the settings instance to avoid reloading on every request.
@lru_cache
def get_settings():
    return Settings()


# Initialize global settings
settings = get_settings()
DEBUG = settings.debug


# --- Path Setup ---
# Define base and upload directories. Ensure upload directory exists.
BASE_DIR = pathlib.Path(__file__).parent
UPLOAD_DIR = BASE_DIR / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)


# --- FastAPI App & Templates ---
# Initialize FastAPI app and Jinja2 template engine for HTML rendering.
app = FastAPI()
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


# --- Routes ---

# Home page route — renders an HTML template.
@app.get("/", response_class=HTMLResponse)
def home_view(request: Request, settings: Settings = Depends(get_settings)):
    print(settings.debug)  # Log debug status for visibility
    return templates.TemplateResponse(
        request=request,
        name="home.html",
        context={"abc": 123}   # Pass data to template
    )


# POST fallback for home — returns JSON response.
@app.post("/")
def home_detail_view():
    return {"hello": "world"}


# Image echo endpoint — accepts an image upload and returns the saved file.
@app.post("/img-echo/", response_class=FileResponse)
async def img_echo_view(
    file: UploadFile = File(...),
    settings: Settings = Depends(get_settings)
):
    # Block access if echo is disabled in settings
    if not settings.echo_active:
        raise HTTPException(status_code=403, detail="Endpoint disabled")

    # Read uploaded file contents
    contents = await file.read()

    # Generate unique filename using UUID and original file extension
    fname = pathlib.Path(file.filename)
    fext = fname.suffix
    dest = UPLOAD_DIR / f"{uuid.uuid4()}{fext}"

    # Save file to disk
    with open(str(dest), 'wb') as out:
        out.write(contents)

    # Return file as downloadable response
    return dest