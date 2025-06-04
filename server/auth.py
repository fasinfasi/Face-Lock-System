import cv2
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import face_recognition
import os
import json
from pymongo import MongoClient
from bson.objectid import ObjectId
import base64
from io import BytesIO
from PIL import Image
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()

# Initialize MongoDB client
client = MongoClient(os.getenv("MONGODB_URI", "mongodb://localhost:27017/"))
db = client.facial_auth
users = db.users

def decode_base64_image(data: str) -> np.ndarray:
    """Decode base64 image data to numpy array"""
    try:
        # Remove the data URL prefix if present
        if ',' in data:
            data = data.split(',')[1]
        
        # Decode base64
        image_bytes = base64.b64decode(data)
        
        # Convert to numpy array
        image = cv2.imdecode(np.frombuffer(image_bytes, np.uint8), cv2.IMREAD_COLOR)
        
        return image
    except Exception as e:
        print(f"Error decoding image: {str(e)}")
        return None

def preprocess_image(image):
    """Enhance image quality for better face detection"""
    # Convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Apply histogram equalization
    equalized = cv2.equalizeHist(gray)
    
    # Apply bilateral filter to reduce noise while keeping edges sharp
    filtered = cv2.bilateralFilter(equalized, 9, 75, 75)
    
    # Convert back to BGR
    enhanced = cv2.cvtColor(filtered, cv2.COLOR_GRAY2BGR)
    
    return enhanced

def get_face_encoding(image):
    """Get face encoding with enhanced preprocessing"""
    # Preprocess the image
    enhanced_image = preprocess_image(image)
    
    # Convert BGR to RGB
    rgb_image = cv2.cvtColor(enhanced_image, cv2.COLOR_BGR2RGB)
    
    # Detect face locations with a smaller model for better performance
    face_locations = face_recognition.face_locations(rgb_image, model="hog")
    
    if not face_locations:
        return None
    
    # Get face encodings
    face_encodings = face_recognition.face_encodings(rgb_image, face_locations)
    
    if not face_encodings:
        return None
    
    return face_encodings[0]

def find_existing_face(face_encoding):
    """Check if face already exists in database."""
    try:
        all_users = list(users.find())
        for user in all_users:
            for stored_encoding in user["face_encodings"]:
                stored_encoding = np.array(stored_encoding)
                similarity = cosine_similarity([face_encoding], [stored_encoding])[0][0]
                if similarity > 0.6:  # Threshold for face matching
                    return user["name"]
        return None
    except Exception as e:
        print(f"Error finding existing face: {str(e)}")
        return None

def register_user(name: str, image_data: str) -> dict:
    """Register a new user with multiple face encodings"""
    try:
        # Check if user already exists
        if users.find_one({"name": name}):
            return {"success": False, "message": "User already exists"}

        # Decode and process image
        image = decode_base64_image(image_data)
        if image is None:
            return {"success": False, "message": "Invalid image data"}

        # Get face encoding
        face_encoding = get_face_encoding(image)
        if face_encoding is None:
            return {"success": False, "message": "No face detected in the image"}

        # Store user data with multiple encodings
        user_data = {
            "name": name,
            "face_encodings": [face_encoding.tolist()],  # Store as list for multiple encodings
            "registration_date": datetime.utcnow()
        }
        
        users.insert_one(user_data)
        return {"success": True, "message": "User registered successfully"}
    except Exception as e:
        return {"success": False, "message": str(e)}

def verify_user(image_data: str) -> dict:
    """Verify user with enhanced face matching"""
    try:
        # Decode and process image
        image = decode_base64_image(image_data)
        if image is None:
            return {"success": False, "message": "Invalid image data"}

        # Get face encoding
        face_encoding = get_face_encoding(image)
        if face_encoding is None:
            return {"success": False, "message": "No face detected in the image"}

        # Get all users
        all_users = list(users.find({}))
        if not all_users:
            return {"success": False, "message": "No registered users found"}

        best_match = None
        best_match_distance = float('inf')
        best_match_username = None

        # Compare with all users
        for user in all_users:
            for stored_encoding in user["face_encodings"]:
                # Convert stored encoding back to numpy array
                stored_encoding = np.array(stored_encoding)
                
                # Calculate face distance
                face_distance = face_recognition.face_distance([stored_encoding], face_encoding)[0]
                
                # Update best match if this is better
                if face_distance < best_match_distance:
                    best_match_distance = face_distance
                    best_match = stored_encoding
                    best_match_username = user["name"]

        # Use a more lenient threshold for better accuracy
        if best_match_distance <= 0.6:  # Increased threshold for better matching
            # Update user's face encodings with the new encoding if it's different enough
            if best_match_distance > 0.4:  # Only add if it's different enough
                users.update_one(
                    {"name": best_match_username},
                    {"$push": {"face_encodings": face_encoding.tolist()}}
                )
            
            return {
                "success": True,
                "message": "Login successful",
                "username": best_match_username,
                "confidence": 1 - best_match_distance
            }
        else:
            return {"success": False, "message": "Face not recognized"}

    except Exception as e:
        return {"success": False, "message": str(e)}

def delete_user(name: str) -> dict:
    """Delete a user from the database"""
    try:
        result = users.delete_one({"name": name})
        if result.deleted_count > 0:
            return {"success": False, "message": "User deleted successfully"}
        return {"success": False, "message": "User not found"}
    except Exception as e:
        return {"success": False, "message": str(e)}
