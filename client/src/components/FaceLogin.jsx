import Webcam from 'react-webcam';
import { useRef } from 'react';
import axios from 'axios';

function FaceLogin() {
  const webcamRef = useRef(null);

  const login = async () => {
    const imageSrc = webcamRef.current.getScreenshot();
    const res = await axios.post("http://localhost:8000/login", {
      image: imageSrc,
    });

    alert(res.data.message);
    if (res.data.success) {
      window.open("/secret-folder/index.html", "_blank");
    }
  };

  return (
    <div className="box">
      <h2>Login With Face</h2>
      <Webcam ref={webcamRef} screenshotFormat="image/jpeg" />
      <button onClick={login}>Login</button>
    </div>
  );
}

export default FaceLogin;
