import React, { useRef, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Container,
  Box,
  Typography,
  Button,
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

const Login = () => {
  const navigate = useNavigate();
  const webcamRef = useRef(null);
  const [isLoading, setIsLoading] = useState(false);
  const [cameraError, setCameraError] = useState(false);
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));

  const videoConstraints = {
    width: isMobile ? 320 : 640,
    height: isMobile ? 240 : 480,
    facingMode: 'user',
  };

  const handleLogin = async () => {
    if (!webcamRef.current) {
      toast.error('Camera not initialized');
      return;
    }

    setIsLoading(true);
    try {
      const imageSrc = webcamRef.current.getScreenshot();
      const response = await axios.post('http://localhost:8000/login', {
        image: imageSrc,
      });

      if (response.data.success) {
        toast.success('Login successful!');
        navigate('/folders', { state: { username: response.data.username } });
      } else {
        toast.error(response.data.detail || 'Login failed');
      }
    } catch (error) {
      console.error('Login error:', error);
      toast.error(error.response?.data?.detail || 'Login failed');
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
            Face Login
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
              <FaceDetection webcamRef={webcamRef} mode="login" />
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
          <Button
            variant="contained"
            onClick={handleLogin}
            disabled={isLoading || cameraError}
            sx={{ 
              mt: 2,
              width: isMobile ? '100%' : 'auto',
              minWidth: isMobile ? 'auto' : 200,
            }}
          >
            {isLoading ? <CircularProgress size={24} /> : 'Login with Face'}
          </Button>
        </Box>
      </Box>
    </Container>
  );
};

export default Login; 