import shutil
import time
import io
from fastapi.testclient import TestClient
from app.main import app, BASE_DIR, UPLOAD_DIR, get_settings
from PIL import Image, ImageChops

client = TestClient(app)


def test_get_home():
    response = client.get("/")
    assert response.text != "<h1>Hello world</h1>"
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]


def test_invalid_file_upload_error():
    response = client.post("/")
    assert response.status_code == 422
    assert "application/json" in response.headers["content-type"]


def test_prediction_upload_missing_headers():
    img_saved_path = BASE_DIR / "images"
    for path in img_saved_path.glob("*"):
        response = client.post("/", files={"file": open(path, "rb")})
        # should fail because skip_auth=false in .env
        assert response.status_code == 401


def test_prediction_upload():
    img_saved_path = BASE_DIR / "images"
    settings = get_settings()
    for path in img_saved_path.glob("*"):
        try:
            img = Image.open(path)
        except Exception:
            img = None
        response = client.post(
            "/",
            files={"file": open(path, "rb")},
            headers={"Authorization": f"Bearer {settings.app_auth_token}"},
        )
        if img is None:
            assert response.status_code == 400
        else:
            assert response.status_code == 200
            data = response.json()
            assert len(data.keys()) == 2


def test_echo_upload():
    img_saved_path = BASE_DIR / "images"
    for path in img_saved_path.glob("*"):
        with open(path, "rb") as f:
            response = client.post("/img-echo/", files={"file": f})
        assert response.status_code == 200
        # exact echo check
        with open(path, "rb") as f:
            original_bytes = f.read()
        assert response.content == original_bytes
    shutil.rmtree(UPLOAD_DIR, ignore_errors=True)
    UPLOAD_DIR.mkdir(exist_ok=True)
