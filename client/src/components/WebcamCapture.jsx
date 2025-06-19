import Webcam from 'react-webcam';
import { useRef, useState } from 'react';
import axios from 'axios';

function WebcamCapture() {
  const webcamRef = useRef(null);
  const [name, setName] = useState("");

  const capture = async () => {
    const imageSrc = webcamRef.current.getScreenshot();
    await axios.post("http://localhost:8000/register", {
      name,
      image: imageSrc,
    });
    alert("Face registered!");
  };

  return (
    <div className="box">
      <h2>Register Your Face</h2>
      <input
        type="text"
        placeholder="Enter your name"
        value={name}
        onChange={e => setName(e.target.value)}
      />
      <Webcam ref={webcamRef} screenshotFormat="image/jpeg" />
      <button onClick={capture}>Register</button>
    </div>
  );
}

export default WebcamCapture;
