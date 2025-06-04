import cv2
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import face_recognition
from typing import Tuple, List, Optional

class FaceDetector:
    def __init__(self):
        # Load OpenCV's pre-trained face detection model
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

    def detect_face(self, image: np.ndarray) -> Tuple[bool, Optional[np.ndarray]]:
        """
        Detect face in the image using OpenCV's cascade classifier
        Returns: (success, face_image)
        """
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Detect faces
        faces = self.face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(30, 30)
        )

        if len(faces) == 0:
            return False, None

        # Get the largest face
        largest_face = max(faces, key=lambda x: x[2] * x[3])
        x, y, w, h = largest_face

        # Extract face region
        face_image = image[y:y+h, x:x+w]
        return True, face_image

    def get_face_encoding(self, image: np.ndarray) -> Optional[np.ndarray]:
        """
        Get face encoding using face_recognition library
        """
        # Convert BGR to RGB
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # Get face encodings
        encodings = face_recognition.face_encodings(rgb_image)
        
        if not encodings:
            return None
            
        return encodings[0]

    def compare_faces(self, known_encoding: np.ndarray, unknown_encoding: np.ndarray, tolerance: float = 0.6) -> bool:
        """
        Compare two face encodings using cosine similarity
        """
        # Reshape for cosine similarity
        known_encoding = known_encoding.reshape(1, -1)
        unknown_encoding = unknown_encoding.reshape(1, -1)
        
        # Calculate cosine similarity
        similarity = cosine_similarity(known_encoding, unknown_encoding)[0][0]
        
        return similarity > (1 - tolerance)

    def verify_face(self, image: np.ndarray, known_encodings: List[np.ndarray]) -> Tuple[bool, float]:
        """
        Verify if the face in the image matches any of the known encodings
        Returns: (is_match, confidence)
        """
        # Detect face
        success, face_image = self.detect_face(image)
        if not success:
            return False, 0.0

        # Get face encoding
        unknown_encoding = self.get_face_encoding(face_image)
        if unknown_encoding is None:
            return False, 0.0

        # Compare with known encodings
        best_similarity = 0.0
        for known_encoding in known_encodings:
            known_encoding = np.array(known_encoding)
            similarity = cosine_similarity(
                unknown_encoding.reshape(1, -1),
                known_encoding.reshape(1, -1)
            )[0][0]
            best_similarity = max(best_similarity, similarity)

        return best_similarity > 0.6, best_similarity

    def preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """
        Preprocess image for better face detection
        """
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Apply histogram equalization
        equalized = cv2.equalizeHist(gray)
        
        # Apply Gaussian blur to reduce noise
        blurred = cv2.GaussianBlur(equalized, (5, 5), 0)
        
        return blurred

# Create a singleton instance
face_detector = FaceDetector() 