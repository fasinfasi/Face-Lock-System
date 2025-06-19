import React from 'react';
import { Button, Container, Typography, Box } from '@mui/material';
import { useNavigate } from 'react-router-dom';

const Home = () => {
  const navigate = useNavigate();

  return (
    <Container maxWidth="sm">
      <Box
        sx={{
          marginTop: 8,
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          gap: 4,
        }}
      >
        <Typography variant="h3" component="h1" gutterBottom>
          Facial Password App
        </Typography>
        <Box sx={{ display: 'flex', gap: 2 }}>
          <Button
            variant="contained"
            color="primary"
            size="large"
            onClick={() => navigate('/register')}
          >
            Create Folder
          </Button>
          <Button
            variant="contained"
            color="secondary"
            size="large"
            onClick={() => navigate('/login')}
          >
            Login
          </Button>
        </Box>
      </Box>
    </Container>
  );
};

export default Home; 