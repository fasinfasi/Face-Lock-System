# 🔐 Facial Lock System – Face Authentication 📂
A secure cloud-like file storage system that uses **facial recognition** as the authentication method. Users can register and login using their unique **facial patterns**, and store their files and folders securely. This system ensures that **only the registered face** can access the protected files.

## 🚀 Features

- 🔐 **Facial Authentication**: Register/login with your face using face recognition (via webcam).
- 📂 **Secure File Management**: Create, delete folders and upload, retrieve, and delete files within them.
- 🖥️ **React Frontend + FastAPI Backend**
- ☁️ **MongoDB Integration**: Store face encodings securely.
- 🧪 Enhanced face detection with image preprocessing and validation techniques.

---

## 📸 Demo
**video**: [Click Here](https://www.dropbox.com/scl/fi/1yfdntdnmrhlvfdzu0pvs/Facial_Lock_System.mp4?rlkey=g8e2yh0nayvbj1uvh930d8iav&st=6oir7027&dl=0)

---

## 🛠️ Tech Stack

| Layer         | Technology                     |
|--------------|---------------------------------|
| Frontend     | React JS                        |
| Backend      | FastAPI                         |
| Face Auth    | OpenCV      |
| Database     | MongoDB         |
| Image Utils  | PIL (Pillow), NumPy             |
| Communication| REST API with CORS              |

---

## 📁 Project Structure
```
facial-lock-system/
├── app/
│ ├── main.py # FastAPI backend entry
│ ├── auth.py # Face registration & verification logic
│ ├── face_detection.py # Face detection and encoding
│ └── requirements.txt # All required Python packages
├── client/ # React frontend
└── .env # Environment variables (Mongo URI, etc.)
```
---
## ✅ Prerequisites

- Python 3.9+
- MongoDB running locally or via cloud (Atlas)
- Node.js (for frontend)
- Virtual environment (recommended)

---

## ⚙️ Backend Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/fasinfasi/Face-Lock-System.git
   cd facial-lock-system
   ```
2. **Create .env file:**
   ```env
   MONGODB_URI=mongodb://localhost:27017/
   CLIENT_URL=http://localhost:3000
   ```

3. Install dependencies:
   ```
   python -m venv venv
   venv\Scripts\activate  # On MacOS:  source venv/bin/activate  
   pip install -r requirements.txt
   ```
4. Run the server:
  ```
  python main.py
  uvicorn main:app --reload
  ```

## 💻 Frontend Setup (React)
1. Open another terminal and navigate to client:
```
cd client
```
2. Install dependencies and run:
 ```
  npm install
  npms start
```
**Make sure the React app is running on http://localhost:3000**

## 🧠 How It Works
1. Registration:
- Click registration button
- Enter user name
- Give the face to the activily opened webcam and take picture (⚠️Make sure face is clear and in light condition)
- Then create folders and keep files
2. Login
- Click Login button
- Take picture of user face
- Compared against stored encodings using cosine similarity
- If similarity > 0.6, user is authenticated

## 🔒Security Notes
- Facial features are not stored as images, but as numerical encodings.
- Face matching threshold (> 0.6) ensures strict authentication.
- Facial landmarks and preprocessing improve spoof prevention.

## ✨ Author
Created by Fasin, you can call me Fasi😉

🤝Connect with me on LinkedIn [fasinfasi](https://www.linkedin.com/in/fasinfasi/)
