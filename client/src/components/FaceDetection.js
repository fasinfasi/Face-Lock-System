import React, { useRef, useEffect } from 'react';
import { Box } from '@mui/material';

const FaceDetection = ({ webcamRef, mode = 'login' }) => {
  const canvasRef = useRef(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    const context = canvas.getContext('2d');
    let animationFrameId;

    const drawFaceBox = (face) => {
      const { top, right, bottom, left } = face;
      context.strokeStyle = '#00ff00';
      context.lineWidth = 2;
      context.strokeRect(left, top, right - left, bottom - top);
    };

    const drawFaceLandmarks = (landmarks) => {
      context.strokeStyle = '#00ff00';
      context.lineWidth = 1;
      context.fillStyle = '#00ff00';

      // Draw facial landmarks
      landmarks.forEach((point) => {
        context.beginPath();
        context.arc(point[0], point[1], 2, 0, 2 * Math.PI);
        context.fill();
      });
    };

    const detectFace = async () => {
      if (webcamRef.current && webcamRef.current.video) {
        const video = webcamRef.current.video;
        const { videoWidth, videoHeight } = video;

        // Set canvas size to match video
        canvas.width = videoWidth;
        canvas.height = videoHeight;

        // Clear previous drawings
        context.clearRect(0, 0, canvas.width, canvas.height);

        // Draw video frame
        context.drawImage(video, 0, 0, videoWidth, videoHeight);

        try {
          // Get face detection data from the server
          const imageSrc = webcamRef.current.getScreenshot();
          if (!imageSrc) return;

          // Ensure the image data is properly formatted
          const imageData = {
            image: imageSrc,
            mode: mode
          };

          const response = await fetch('http://localhost:8000/detect-face', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify(imageData),
          });

          if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
          }

          const data = await response.json();
          if (data.success) {
            if (mode === 'login' && data.face) {
              drawFaceBox(data.face);
            } else if (mode === 'register' && data.landmarks) {
              drawFaceLandmarks(data.landmarks);
            }
          }
        } catch (error) {
          console.error('Face detection error:', error);
        }
      }

      animationFrameId = requestAnimationFrame(detectFace);
    };

    detectFace();

    return () => {
      if (animationFrameId) {
        cancelAnimationFrame(animationFrameId);
      }
    };
  }, [webcamRef, mode]);

  return (
    <Box sx={{ position: 'relative', width: '100%' }}>
      <canvas
        ref={canvasRef}
        style={{
          position: 'absolute',
          top: 0,
          left: 0,
          width: '100%',
          height: '100%',
          zIndex: 1,
        }}
      />
    </Box>
  );
};

export default FaceDetection; 