from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from PIL import Image
import base64
from io import BytesIO
import face_recognition
import cv2
import numpy as np
from auth import register_user, verify_user, delete_user, decode_base64_image, get_face_encoding
import os
from dotenv import load_dotenv
from typing import List, Optional
import shutil
import mimetypes

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

# Create base directories if they don't exist
BASE_DIR = "user_data"
if not os.path.exists(BASE_DIR):
    os.makedirs(BASE_DIR)

class UserRegistration(BaseModel):
    name: str
    image: str

class UserLogin(BaseModel):
    image: str

class FolderCreate(BaseModel):
    name: str
    folder_name: str

class FolderDelete(BaseModel):
    name: str
    folder_name: str

class FaceDetectionRequest(BaseModel):
    image: str
    mode: str

@app.post("/detect-face")
async def detect_face(request: FaceDetectionRequest):
    try:
        # Decode and preprocess image
        if not request.image or not request.mode:
            raise HTTPException(status_code=400, detail="Missing image or mode data")

        # Remove the data URL prefix if present
        image_data = request.image
        if ',' in image_data:
            image_data = image_data.split(',')[1]

        try:
            # Decode base64 image
            image_bytes = base64.b64decode(image_data)
            image = cv2.imdecode(np.frombuffer(image_bytes, np.uint8), cv2.IMREAD_COLOR)
            
            if image is None:
                raise HTTPException(status_code=400, detail="Invalid image data")
            
            # Convert BGR to RGB
            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            # Detect face locations
            face_locations = face_recognition.face_locations(rgb_image)
            
            if not face_locations:
                return {"success": False, "message": "No face detected"}
            
            if request.mode == 'login':
                # For login, return face box coordinates
                face = face_locations[0]
                return {
                    "success": True,
                    "face": {
                        "top": face[0],
                        "right": face[1],
                        "bottom": face[2],
                        "left": face[3]
                    }
                }
            else:
                # For registration, return facial landmarks
                face_landmarks_list = face_recognition.face_landmarks(rgb_image, face_locations)
                if not face_landmarks_list:
                    return {"success": False, "message": "Could not detect facial landmarks"}
                
                # Convert landmarks to list format
                landmarks = []
                for landmark in face_landmarks_list[0].values():
                    landmarks.extend(landmark)
                
                return {
                    "success": True,
                    "landmarks": landmarks
                }
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Error processing image: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def get_user_folder_path(username: str, folder_name: str) -> str:
    return os.path.join(BASE_DIR, username, folder_name)

@app.post("/register")
async def register(user: UserRegistration):
    try:
        result = register_user(user.name, user.image)
        if result["success"]:
            # Create user directory
            user_dir = os.path.join(BASE_DIR, user.name)
            if not os.path.exists(user_dir):
                os.makedirs(user_dir)
            return {"success": True, "message": "User registered successfully"}
        return {"success": False, "detail": result["message"]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/login")
async def login(user: UserLogin):
    try:
        result = verify_user(user.image)
        if result["success"]:
            return {
                "success": True,
                "message": "Login successful",
                "username": result["username"]
            }
        return {"success": False, "detail": result["message"]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/folders/{username}")
async def get_folders(username: str):
    try:
        user_dir = os.path.join(BASE_DIR, username)
        if not os.path.exists(user_dir):
            os.makedirs(user_dir)
            return {"success": True, "folders": []}
        
        folders = [f for f in os.listdir(user_dir) if os.path.isdir(os.path.join(user_dir, f))]
        return {"success": True, "folders": folders}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/folder/create")
async def create_folder(folder: FolderCreate):
    try:
        user_dir = os.path.join(BASE_DIR, folder.name)
        if not os.path.exists(user_dir):
            os.makedirs(user_dir)
        
        folder_path = os.path.join(user_dir, folder.folder_name)
        if os.path.exists(folder_path):
            raise HTTPException(status_code=400, detail="Folder already exists")
        
        os.makedirs(folder_path)
        return {"success": True, "message": "Folder created successfully"}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/folder/delete")
async def delete_folder(folder: FolderDelete):
    try:
        folder_path = os.path.join(BASE_DIR, folder.name, folder.folder_name)
        if not os.path.exists(folder_path):
            raise HTTPException(status_code=404, detail="Folder not found")
        
        shutil.rmtree(folder_path)
        return {"success": True, "message": "Folder deleted successfully"}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/files/{username}/{folder_name}")
async def get_files(username: str, folder_name: str):
    try:
        folder_path = os.path.join(BASE_DIR, username, folder_name)
        if not os.path.exists(folder_path):
            raise HTTPException(status_code=404, detail="Folder not found")
        
        files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
        return {"success": True, "files": files}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/upload/{username}/{folder_name}")
async def upload_file(
    username: str,
    folder_name: str,
    file: UploadFile = File(...)
):
    try:
        folder_path = os.path.join(BASE_DIR, username, folder_name)
        if not os.path.exists(folder_path):
            raise HTTPException(status_code=404, detail="Folder not found")
        
        file_path = os.path.join(folder_path, file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        return {"success": True, "message": "File uploaded successfully"}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/files/{username}/{folder_name}/{file_name}")
async def get_file(username: str, folder_name: str, file_name: str):
    try:
        file_path = os.path.join(BASE_DIR, username, folder_name, file_name)
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="File not found")
        
        return FileResponse(file_path)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/files/{username}/{folder_name}/{file_name}")
async def delete_file(username: str, folder_name: str, file_name: str):
    try:
        file_path = os.path.join(BASE_DIR, username, folder_name, file_name)
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="File not found")
        
        os.remove(file_path)
        return {"success": True, "message": "File deleted successfully"}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.get("/check-db")
async def check_database():
    try:
        # Get all users without face encodings
        users = list(db.users.find({}, {"name": 1, "registration_date": 1, "_id": 0}))
        return {
            "success": True,
            "user_count": len(users),
            "users": users
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
