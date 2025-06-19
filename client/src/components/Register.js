import React, { useRef, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Container,
  Box,
  Typography,
  Button,
  TextField,
  CircularProgress,
  IconButton,
  useTheme,
  useMediaQuery,
} from '@mui/material';
import { Home as HomeIcon } from '@mui/icons-material';
import Webcam from 'react-webcam';
import { toast } from 'react-toastify';
import axios from 'axios';
import FaceDetection from './FaceDetection';

const Register = () => {
  const navigate = useNavigate();
  const webcamRef = useRef(null);
  const [name, setName] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [cameraError, setCameraError] = useState(false);
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));

  const videoConstraints = {
    width: isMobile ? 320 : 640,
    height: isMobile ? 240 : 480,
    facingMode: 'user',
  };

  const handleRegister = async () => {
    if (!name.trim()) {
      toast.error('Please enter your name');
      return;
    }

    if (!webcamRef.current) {
      toast.error('Camera not initialized');
      return;
    }

    setIsLoading(true);
    try {
      const imageSrc = webcamRef.current.getScreenshot();
      if (!imageSrc) {
        toast.error('Failed to capture image. Please try again.');
        setIsLoading(false);
        return;
      }

      console.log('Sending registration request...');
      const response = await axios.post('http://localhost:8000/register', {
        name: name.trim(),
        image: imageSrc,
      });

      console.log('Registration response:', response.data);

      if (response.data.success) {
        toast.success('Registration successful!');
        navigate('/folders', { state: { username: name.trim() } });
      } else {
        // Handle different types of errors
        switch (response.data.type) {
          case 'face_exists':
            toast.warning(
              <div>
                <p>{response.data.message}</p>
                <p>Please login instead.</p>
                <Button 
                  variant="contained" 
                  size="small" 
                  onClick={() => navigate('/login')}
                  sx={{ mt: 1 }}
                >
                  Go to Login
                </Button>
              </div>,
              {
                autoClose: false,
                closeOnClick: false,
                position: "top-center",
                style: { 
                  width: 'auto',
                  maxWidth: '90%',
                  textAlign: 'center'
                }
              }
            );
            break;
          case 'user_exists':
            toast.error('This username is already taken. Please choose another name.');
            break;
          case 'face_error':
            toast.error(
              <div>
                <p>{response.data.message}</p>
                <p>Please ensure:</p>
                <ul style={{ textAlign: 'left', margin: '8px 0' }}>
                  <li>Your face is clearly visible</li>
                  <li>You are in a well-lit area</li>
                  <li>You are looking directly at the camera</li>
                  <li>There is no glare or shadows on your face</li>
                  <li>You are not wearing sunglasses or face coverings</li>
                </ul>
                <p>Try adjusting your position or lighting and try again.</p>
              </div>,
              {
                autoClose: 8000,
                position: "top-center",
                style: { 
                  width: 'auto',
                  maxWidth: '90%',
                  textAlign: 'center'
                }
              }
            );
            break;
          case 'image_error':
            toast.error(
              <div>
                <p>{response.data.message}</p>
                <p>Please try again with a clearer image.</p>
              </div>
            );
            break;
          case 'validation_error':
            toast.error(response.data.message);
            break;
          case 'database_error':
            toast.error(
              <div>
                <p>{response.data.message}</p>
                <p>Please try again or contact support if the problem persists.</p>
              </div>
            );
            break;
          default:
            toast.error(
              <div>
                <p>{response.data.message || 'Registration failed'}</p>
                <p>Please try again or contact support if the problem persists.</p>
              </div>
            );
        }
      }
    } catch (error) {
      console.error('Registration error:', error);
      const errorMessage = error.response?.data?.message || 'Registration failed';
      toast.error(
        <div>
          <p>{errorMessage}</p>
          <p>Please try again or contact support if the problem persists.</p>
        </div>
      );
    } finally {
      setIsLoading(false);
    }
  };

  const handleCameraError = () => {
    setCameraError(true);
    toast.error('Failed to access camera. Please check permissions.');
  };

  return (
    <Container maxWidth="sm" sx={{ height: '100vh', display: 'flex', flexDirection: 'column' }}>
      <Box sx={{ 
        my: 4, 
        textAlign: 'center',
        flex: 1,
        display: 'flex',
        flexDirection: 'column',
        gap: 2,
      }}>
        <Box sx={{ 
          display: 'flex', 
          justifyContent: 'space-between', 
          alignItems: 'center', 
          mb: 2,
          px: isMobile ? 1 : 2,
        }}>
          <Typography variant={isMobile ? "h5" : "h4"} component="h1" gutterBottom>
            Face Registration
          </Typography>
          <IconButton onClick={() => navigate('/')} size={isMobile ? "small" : "medium"}>
            <HomeIcon />
          </IconButton>
        </Box>

        <Box sx={{ 
          position: 'relative', 
          width: '100%', 
          mb: 2,
          flex: 1,
          minHeight: isMobile ? 240 : 480,
        }}>
          {!cameraError ? (
            <>
              <Webcam
                ref={webcamRef}
                audio={false}
                screenshotFormat="image/jpeg"
                videoConstraints={videoConstraints}
                onUserMediaError={handleCameraError}
                style={{ 
                  width: '100%', 
                  height: '100%',
                  objectFit: 'cover',
                  borderRadius: '8px',
                }}
              />
              <FaceDetection webcamRef={webcamRef} mode="register" />
            </>
          ) : (
            <Box
              sx={{
                width: '100%',
                height: '100%',
                bgcolor: 'grey.200',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                borderRadius: '8px',
              }}
            >
              <Typography color="error">Camera access failed</Typography>
            </Box>
          )}
        </Box>

        <Box sx={{ px: isMobile ? 1 : 2 }}>
          <TextField
            fullWidth
            label="Enter your name"
            value={name}
            onChange={(e) => setName(e.target.value)}
            margin="normal"
            disabled={isLoading}
            size={isMobile ? "small" : "medium"}
          />

          <Button
            variant="contained"
            onClick={handleRegister}
            disabled={isLoading || !name.trim() || cameraError}
            sx={{ 
              mt: 2,
              width: isMobile ? '100%' : 'auto',
              minWidth: isMobile ? 'auto' : 200,
            }}
          >
            {isLoading ? <CircularProgress size={24} /> : 'Register Face'}
          </Button>
        </Box>
      </Box>
    </Container>
  );
};

export default Register; 