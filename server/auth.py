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
        print("Starting image decoding...")
        # Remove the data URL prefix if present
        if ',' in data:
            data = data.split(',')[1]
            print("Removed data URL prefix")
        
        # Decode base64
        print("Decoding base64 data...")
        image_bytes = base64.b64decode(data)
        print(f"Decoded {len(image_bytes)} bytes")
        
        # Convert to numpy array
        print("Converting to numpy array...")
        image = cv2.imdecode(np.frombuffer(image_bytes, np.uint8), cv2.IMREAD_COLOR)
        
        if image is None:
            print("Failed to decode image - image is None")
            return None
            
        print(f"Successfully decoded image with shape: {image.shape}")
        return image
    except Exception as e:
        print(f"Error decoding image: {str(e)}")
        return None

def preprocess_image(image):
    """Enhanced image preprocessing with multiple techniques"""
    try:
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Apply CLAHE (Contrast Limited Adaptive Histogram Equalization)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        equalized = clahe.apply(gray)
        
        # Apply bilateral filter to reduce noise while keeping edges sharp
        filtered = cv2.bilateralFilter(equalized, 9, 75, 75)
        
        # Apply adaptive thresholding
        thresh = cv2.adaptiveThreshold(filtered, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                     cv2.THRESH_BINARY, 11, 2)
        
        # Apply morphological operations to enhance features
        kernel = np.ones((3,3), np.uint8)
        morph = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
        
        # Convert back to BGR
        enhanced = cv2.cvtColor(morph, cv2.COLOR_GRAY2BGR)
        
        # Apply sharpening
        kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
        enhanced = cv2.filter2D(enhanced, -1, kernel)
        
        return enhanced
    except Exception as e:
        print(f"Error in preprocessing: {str(e)}")
        return image

def get_face_encoding(image):
    """Get multiple face encodings with enhanced preprocessing and validation"""
    try:
        print("\nStarting face encoding process...")
        # Preprocess the image
        print("Preprocessing image...")
        enhanced_image = preprocess_image(image)
        
        # Convert BGR to RGB
        print("Converting to RGB...")
        rgb_image = cv2.cvtColor(enhanced_image, cv2.COLOR_BGR2RGB)
        
        # Detect face locations
        print("Detecting face locations...")
        face_locations = face_recognition.face_locations(rgb_image, model="hog")
        
        if not face_locations:
            print("No face locations detected")
            return None
        
        print(f"Found {len(face_locations)} face(s)")
        
        # Get face encodings
        print("Getting face encodings...")
        face_encodings = face_recognition.face_encodings(rgb_image, face_locations)
        
        if not face_encodings:
            print("No face encodings generated")
            return None
        
        print(f"Generated {len(face_encodings)} face encoding(s)")
        
        # Get facial landmarks
        print("Getting facial landmarks...")
        face_landmarks = face_recognition.face_landmarks(rgb_image, face_locations)
        
        if not face_landmarks:
            print("No facial landmarks detected")
            return None
        
        print("Validating face landmarks...")
        if not validate_face_landmarks(face_landmarks[0]):
            print("Face landmarks validation failed")
            return None
        
        # Get multiple encodings
        print("Generating multiple encodings...")
        encodings = []
        for encoding in face_encodings:
            encodings.append(encoding)
            for factor in [0.95, 1.05]:
                modified = encoding * factor
                encodings.append(modified)
        
        print(f"Generated {len(encodings)} total encodings")
        return encodings
    except Exception as e:
        print(f"Error in face encoding: {str(e)}")
        return None

def validate_face_landmarks(landmarks):
    """Validate facial landmarks for better security"""
    try:
        required_features = ['left_eye', 'right_eye', 'nose_bridge', 'top_lip', 'bottom_lip']
        
        # Check if all required features are present
        if not all(feature in landmarks for feature in required_features):
            return False
        
        # Validate eye positions
        left_eye = landmarks['left_eye']
        right_eye = landmarks['right_eye']
        
        # Check if eyes are at reasonable positions
        if not validate_eye_positions(left_eye, right_eye):
            return False
        
        return True
    except Exception as e:
        print(f"Error validating landmarks: {str(e)}")
        return False

def validate_eye_positions(left_eye, right_eye):
    """Validate eye positions for better face detection"""
    try:
        # Calculate eye aspect ratios
        left_ear = calculate_eye_aspect_ratio(left_eye)
        right_ear = calculate_eye_aspect_ratio(right_eye)
        
        # Check if eyes are open
        if left_ear < 0.2 or right_ear < 0.2:
            return False
        
        # Check if eyes are at similar heights
        left_y = sum(point[1] for point in left_eye) / len(left_eye)
        right_y = sum(point[1] for point in right_eye) / len(right_eye)
        
        if abs(left_y - right_y) > 10:
            return False
        
        return True
    except Exception as e:
        print(f"Error validating eye positions: {str(e)}")
        return False

def calculate_eye_aspect_ratio(eye):
    """Calculate eye aspect ratio for validation"""
    try:
        # Compute the euclidean distances between the vertical eye landmarks
        A = np.linalg.norm(np.array(eye[1]) - np.array(eye[5]))
        B = np.linalg.norm(np.array(eye[2]) - np.array(eye[4]))
        
        # Compute the euclidean distance between the horizontal eye landmarks
        C = np.linalg.norm(np.array(eye[0]) - np.array(eye[3]))
        
        # Compute the eye aspect ratio
        ear = (A + B) / (2.0 * C)
        
        return ear
    except Exception as e:
        print(f"Error calculating eye aspect ratio: {str(e)}")
        return 0

def find_existing_face(face_encodings):
    """Enhanced face matching with multiple encodings and stricter verification"""
    try:
        user_count = users.count_documents({})
        print(f"Total users in database: {user_count}")
        
        if user_count == 0:
            print("Database is empty, no existing faces to compare")
            return None

        all_users = list(users.find())
        print(f"Found {len(all_users)} users to compare against")
        
        best_match = None
        best_match_score = 0.0
        
        for user in all_users:
            print(f"\nChecking against user: {user['name']}")
            user_scores = []
            
            for stored_encoding in user["face_encodings"]:
                stored_encoding = np.array(stored_encoding)
                
                # Compare with all provided encodings
                for encoding in face_encodings:
                    similarity = cosine_similarity([encoding], [stored_encoding])[0][0]
                    user_scores.append(similarity)
                    print(f"Similarity score: {similarity:.4f}")
            
            # Get the best score for this user
            if user_scores:
                max_score = max(user_scores)
                if max_score > best_match_score:
                    best_match_score = max_score
                    best_match = user["name"]
        
        # Use a much higher threshold for more security
        if best_match_score > 0.92:  # Increased threshold for better security
            print(f"Best match found: {best_match} with score: {best_match_score:.4f}")
            return best_match
        
        print("No matching faces found")
        return None
    except Exception as e:
        print(f"Error finding existing face: {str(e)}")
        return None

def register_user(name: str, image_data: str) -> dict:
    """Register a new user with enhanced face verification"""
    try:
        print(f"\n=== Starting registration for user: {name} ===")
        
        if not name or not name.strip():
            print("Name validation failed: empty name")
            return {
                "success": False,
                "message": "Name is required",
                "type": "validation_error"
            }

        if not image_data:
            print("Image data validation failed: empty image")
            return {
                "success": False,
                "message": "Image data is required",
                "type": "validation_error"
            }

        print("Checking for existing user...")
        existing_user = users.find_one({"name": name})
        if existing_user:
            print(f"User {name} already exists in database")
            return {
                "success": False,
                "message": "User already exists",
                "type": "user_exists"
            }

        print("Decoding image data...")
        try:
            image = decode_base64_image(image_data)
            if image is None:
                print("Failed to decode image")
                return {
                    "success": False,
                    "message": "Failed to process image data. Please try again.",
                    "type": "image_error"
                }
        except Exception as e:
            print(f"Image decoding error: {str(e)}")
            return {
                "success": False,
                "message": f"Invalid image format: {str(e)}",
                "type": "image_error"
            }

        print("Getting face encodings...")
        try:
            face_encodings = get_face_encoding(image)
            if face_encodings is None:
                print("No face detected in image")
                return {
                    "success": False,
                    "message": "No face detected in the image. Please ensure your face is clearly visible and well-lit.",
                    "type": "face_error"
                }
        except Exception as e:
            print(f"Face encoding error: {str(e)}")
            return {
                "success": False,
                "message": f"Failed to process face data: {str(e)}",
                "type": "face_error"
            }

        print("Checking for existing face matches...")
        try:
            existing_face = find_existing_face(face_encodings)
            if existing_face:
                print(f"Found existing face match: {existing_face}")
                return {
                    "success": False,
                    "message": f"This face is already registered as '{existing_face}'",
                    "type": "face_exists",
                    "existing_user": existing_face
                }
        except Exception as e:
            print(f"Face matching error: {str(e)}")
            return {
                "success": False,
                "message": f"Error checking for existing faces: {str(e)}",
                "type": "face_error"
            }

        print("Storing new user data...")
        try:
            user_data = {
                "name": name,
                "face_encodings": [encoding.tolist() for encoding in face_encodings],
                "registration_date": datetime.utcnow()
            }
            
            result = users.insert_one(user_data)
            print(f"Successfully registered user {name} with ID {result.inserted_id}")
            return {
                "success": True,
                "message": "User registered successfully",
                "type": "success"
            }
        except Exception as e:
            print(f"Database error: {str(e)}")
            return {
                "success": False,
                "message": f"Failed to save user data: {str(e)}",
                "type": "database_error"
            }
    except Exception as e:
        print(f"Registration error: {str(e)}")
        return {
            "success": False,
            "message": f"Registration failed: {str(e)}",
            "type": "error"
        }

def verify_user(image_data: str) -> dict:
    """Enhanced user verification with multiple face encodings and strict validation"""
    try:
        print("\nStarting user verification...")
        
        image = decode_base64_image(image_data)
        if image is None:
            return {"success": False, "message": "Invalid image data"}

        face_encodings = get_face_encoding(image)
        if face_encodings is None:
            return {"success": False, "message": "No face detected in the image"}

        all_users = list(users.find({}))
        if not all_users:
            return {"success": False, "message": "No registered users found"}

        best_match = None
        best_match_score = 0.0
        best_match_username = None

        for user in all_users:
            user_scores = []
            for stored_encoding in user["face_encodings"]:
                stored_encoding = np.array(stored_encoding)
                for encoding in face_encodings:
                    similarity = cosine_similarity([encoding], [stored_encoding])[0][0]
                    user_scores.append(similarity)
            
            if user_scores:
                max_score = max(user_scores)
                if max_score > best_match_score:
                    best_match_score = max_score
                    best_match_username = user["name"]

        # Use a much higher threshold for login verification
        if best_match_score > 0.92:  # Increased threshold for better security
            return {
                "success": True,
                "message": "Login successful",
                "username": best_match_username,
                "confidence": best_match_score
            }
        else:
            return {"success": False, "message": "Face not recognized"}

    except Exception as e:
        print(f"Verification error: {str(e)}")
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
