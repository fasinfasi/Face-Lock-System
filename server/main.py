from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from PIL import Image
import base64
from io import BytesIO
import face_recognition
from auth import register_user, verify_user, delete_user
import os
from dotenv import load_dotenv
from typing import List
import shutil

# Load environment variables
load_dotenv()

app = FastAPI(title="Facial Authentication API")

# Configure CORS
origins = [os.getenv("CLIENT_URL", "http://localhost:3000")]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create uploads directory if it doesn't exist
UPLOADS_DIR = "uploads"
os.makedirs(UPLOADS_DIR, exist_ok=True)

class RegisterRequest(BaseModel):
    name: str
    image: str

class LoginRequest(BaseModel):
    image: str

class DeleteRequest(BaseModel):
    name: str

class CreateFolderRequest(BaseModel):
    name: str
    folder_name: str

class DeleteFolderRequest(BaseModel):
    name: str
    folder_name: str

def decode_base64_image(data: str) -> Image.Image:
    try:
        header, encoded = data.split(",", 1)
        return face_recognition.load_image_file(BytesIO(base64.b64decode(encoded)))
    except Exception as e:
        raise HTTPException(status_code=400, detail="Invalid image data")

def get_user_folder_path(username: str, folder_name: str) -> str:
    return os.path.join(UPLOADS_DIR, username, folder_name)

@app.post("/register")
async def register(req: RegisterRequest):
    try:
        image = decode_base64_image(req.image)
        return register_user(req.name, image)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/login")
async def login(req: LoginRequest):
    try:
        image = decode_base64_image(req.image)
        return verify_user(image)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/user")
async def delete(req: DeleteRequest):
    try:
        return delete_user(req.name)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/folder/create")
async def create_folder(req: CreateFolderRequest):
    try:
        folder_path = get_user_folder_path(req.name, req.folder_name)
        if os.path.exists(folder_path):
            raise HTTPException(status_code=400, detail="Folder already exists")
        os.makedirs(folder_path)
        return {"success": True, "message": f"Folder {req.folder_name} created successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/folder/delete")
async def delete_folder(req: DeleteFolderRequest):
    try:
        folder_path = get_user_folder_path(req.name, req.folder_name)
        if not os.path.exists(folder_path):
            raise HTTPException(status_code=404, detail="Folder not found")
        shutil.rmtree(folder_path)
        return {"success": True, "message": f"Folder {req.folder_name} deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/folders/{username}")
async def list_folders(username: str):
    try:
        user_path = os.path.join(UPLOADS_DIR, username)
        if not os.path.exists(user_path):
            return {"success": True, "folders": []}
        folders = [f for f in os.listdir(user_path) if os.path.isdir(os.path.join(user_path, f))]
        return {"success": True, "folders": folders}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/upload/{username}/{folder_name}")
async def upload_file(
    username: str,
    folder_name: str,
    file: UploadFile = File(...)
):
    try:
        folder_path = get_user_folder_path(username, folder_name)
        if not os.path.exists(folder_path):
            raise HTTPException(status_code=404, detail="Folder not found")

        # Check folder size
        total_size = sum(os.path.getsize(os.path.join(folder_path, f)) for f in os.listdir(folder_path))
        if total_size + file.size > 5 * 1024 * 1024:  # 5MB limit
            raise HTTPException(status_code=400, detail="Folder size limit exceeded (5MB)")

        file_path = os.path.join(folder_path, file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        return {"success": True, "message": "File uploaded successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/files/{username}/{folder_name}")
async def list_files(username: str, folder_name: str):
    try:
        folder_path = get_user_folder_path(username, folder_name)
        if not os.path.exists(folder_path):
            raise HTTPException(status_code=404, detail="Folder not found")
        files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
        return {"success": True, "files": files}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/files/{username}/{folder_name}/{filename}")
async def delete_file(username: str, folder_name: str, filename: str):
    try:
        file_path = os.path.join(get_user_folder_path(username, folder_name), filename)
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="File not found")
        os.remove(file_path)
        return {"success": True, "message": "File deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
