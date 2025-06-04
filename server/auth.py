from pymongo import MongoClient
import face_recognition
import numpy as np
import os
from dotenv import load_dotenv
from typing import Dict, Any

# Load environment variables
load_dotenv()

# MongoDB configuration
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME", "face_auth")
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "users")

# Face recognition configuration
FACE_DETECTION_CONFIDENCE = float(os.getenv("FACE_DETECTION_CONFIDENCE", "0.6"))

try:
    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]
    collection = db[COLLECTION_NAME]
except Exception as e:
    print(f"Failed to connect to MongoDB: {e}")
    raise

def register_user(name: str, image: np.ndarray) -> Dict[str, Any]:
    """Register a new user with their face encoding."""
    try:
        # Check if user already exists
        if collection.find_one({"name": name}):
            return {"success": False, "message": f"User {name} already exists!"}

        # Get face encodings
        encodings = face_recognition.face_encodings(image)
        if not encodings:
            return {"success": False, "message": "No face detected!"}

        # Get face locations for confidence check
        face_locations = face_recognition.face_locations(image)
        if not face_locations:
            return {"success": False, "message": "No face detected!"}

        # Check if multiple faces are detected
        if len(encodings) > 1:
            return {"success": False, "message": "Multiple faces detected! Please provide an image with only one face."}

        encoding = encodings[0].tolist()
        collection.insert_one({"name": name, "encoding": encoding})
        return {"success": True, "message": f"User {name} registered successfully."}
    except Exception as e:
        return {"success": False, "message": f"Registration failed: {str(e)}"}

def verify_user(image: np.ndarray) -> Dict[str, Any]:
    """Verify a user's face against registered faces."""
    try:
        unknown_encodings = face_recognition.face_encodings(image)
        if not unknown_encodings:
            return {"success": False, "message": "No face detected."}

        unknown = unknown_encodings[0]
        best_match = None
        best_distance = float('inf')

        for user in collection.find():
            known = np.array(user["encoding"])
            # Calculate face distance
            face_distance = face_recognition.face_distance([known], unknown)[0]
            
            if face_distance < best_distance:
                best_distance = face_distance
                best_match = user

        # Check if the best match meets the confidence threshold
        if best_match and best_distance <= (1 - FACE_DETECTION_CONFIDENCE):
            return {"success": True, "message": f"Welcome {best_match['name']}!"}
        
        return {"success": False, "message": "Face not recognized."}
    except Exception as e:
        return {"success": False, "message": f"Verification failed: {str(e)}"}

def delete_user(name: str) -> Dict[str, Any]:
    """Delete a registered user."""
    try:
        result = collection.delete_one({"name": name})
        if result.deleted_count > 0:
            return {"success": True, "message": f"User {name} deleted successfully."}
        return {"success": False, "message": f"User {name} not found."}
    except Exception as e:
        return {"success": False, "message": f"Deletion failed: {str(e)}"}
