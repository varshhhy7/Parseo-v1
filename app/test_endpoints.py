import shutil
import time
from fastapi.testclient import TestClient
from app.main import app, BASE_DIR, UPLOAD_DIR  # ✅ Import UPLOAD_DIR

client = TestClient(app)


def test_get_home():
    response = client.get("/")
    assert response.text != "<h1>Hello World</h1>"  # Ensure template rendered
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]


def test_post_home():
    response = client.post("/")
    assert response.status_code == 200
    assert "application/json" in response.headers["content-type"]
    assert response.json() == {"hello": "world"}


def test_echo_upload():
    image_saved_path = BASE_DIR / "images"

    # MIME type mapping for common image extensions
    MIME_MAP = {
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg',
        '.png': 'image/png',
        '.gif': 'image/gif',
        '.webp': 'image/webp',
        '.bmp': 'image/bmp',
        '.tiff': 'image/tiff',
        '.svg': 'image/svg+xml',
    }

    # Ensure test directory exists and has files
    assert image_saved_path.exists(), f"Test image directory not found: {image_saved_path}"
    image_files = list(image_saved_path.glob("*"))
    assert len(image_files) > 0, "No test images found in 'images/' directory"

    for path in image_files:
        # Skip if extension not in MIME map
        if path.suffix.lower() not in MIME_MAP:
            continue

        with open(path, 'rb') as f:  # ✅ Safe file handling
            response = client.post("/img-echo/", files={"file": f})

        assert response.status_code == 200
        expected_mime = MIME_MAP[path.suffix.lower()]
        actual_mime = response.headers.get("content-type", "").split(';')[0].strip()  # Strip charset if present
        assert actual_mime == expected_mime, f"Expected {expected_mime}, got {actual_mime}"

    # Cleanup: remove all uploaded files after testing
    shutil.rmtree(UPLOAD_DIR)
    UPLOAD_DIR.mkdir(exist_ok=True)  # Recreate for next test run