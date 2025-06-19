import React, { useState, useEffect, useCallback } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import {
  Container,
  Box,
  Typography,
  Button,
  TextField,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Grid,
  Card,
  CardContent,
  CardActions,
} from '@mui/material';
import {
  Delete as DeleteIcon,
  Add as AddIcon,
  Home as HomeIcon,
  Visibility as VisibilityIcon,
  Download as DownloadIcon,
} from '@mui/icons-material';
import { toast } from 'react-toastify';
import axios from 'axios';

const Folders = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const [folders, setFolders] = useState([]);
  const [newFolderName, setNewFolderName] = useState('');
  const [openDialog, setOpenDialog] = useState(false);
  const [selectedFolder, setSelectedFolder] = useState(null);
  const [files, setFiles] = useState([]);
  const [previewFile, setPreviewFile] = useState(null);

  const username = location.state?.username;

  const fetchFolders = useCallback(async () => {
    if (!username) {
      navigate('/');
      return;
    }
    try {
      const response = await axios.get(`http://localhost:8000/folders/${username}`);
      if (response.data.success) {
        setFolders(response.data.folders || []);
      }
    } catch (error) {
      console.error('Failed to fetch folders:', error);
      // Initialize empty folders for new users
      setFolders([]);
    }
  }, [username, navigate]);

  useEffect(() => {
    fetchFolders();
  }, [fetchFolders]);

  const createFolder = async () => {
    if (!newFolderName.trim()) {
      toast.error('Please enter a folder name');
      return;
    }
    try {
      const response = await axios.post('http://localhost:8000/folder/create', {
        name: username,
        folder_name: newFolderName.trim(),
      });
      if (response.data.success) {
        toast.success('Folder created successfully');
        setNewFolderName('');
        setOpenDialog(false);
        fetchFolders();
      }
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to create folder');
    }
  };

  const deleteFolder = async (folderName) => {
    try {
      const response = await axios.delete('http://localhost:8000/folder/delete', {
        data: {
          name: username,
          folder_name: folderName,
        },
      });
      if (response.data.success) {
        toast.success('Folder deleted successfully');
        if (selectedFolder === folderName) {
          setSelectedFolder(null);
          setFiles([]);
        }
        fetchFolders();
      }
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to delete folder');
    }
  };

  const handleFolderClick = async (folderName) => {
    try {
      setSelectedFolder(folderName);
      const response = await axios.get(
        `http://localhost:8000/files/${username}/${folderName}`
      );
      if (response.data.success) {
        setFiles(response.data.files || []);
      } else {
        toast.error('Failed to fetch files');
        setFiles([]);
      }
    } catch (error) {
      console.error('Error fetching files:', error);
      toast.error('Failed to fetch files');
      setFiles([]);
    }
  };

  const handleFileUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await axios.post(
        `http://localhost:8000/upload/${username}/${selectedFolder}`,
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        }
      );
      if (response.data.success) {
        toast.success('File uploaded successfully');
        handleFolderClick(selectedFolder);
      }
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to upload file');
    }
  };

  const handleFileDelete = async (fileName) => {
    try {
      const response = await axios.delete(
        `http://localhost:8000/files/${username}/${selectedFolder}/${fileName}`
      );
      if (response.data.success) {
        toast.success('File deleted successfully');
        handleFolderClick(selectedFolder);
      }
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to delete file');
    }
  };

  const handleFilePreview = async (fileName) => {
    try {
      const response = await axios.get(
        `http://localhost:8000/files/${username}/${selectedFolder}/${fileName}`,
        { responseType: 'blob' }
      );
      const url = window.URL.createObjectURL(new Blob([response.data]));
      setPreviewFile({ url, name: fileName });
    } catch (error) {
      toast.error('Failed to preview file');
    }
  };

  const handleFileDownload = async (fileName) => {
    try {
      const response = await axios.get(
        `http://localhost:8000/files/${username}/${selectedFolder}/${fileName}`,
        { responseType: 'blob' }
      );
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', fileName);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (error) {
      toast.error('Failed to download file');
    }
  };

  const isImageFile = (fileName) => {
    const imageExtensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'];
    return imageExtensions.some(ext => fileName.toLowerCase().endsWith(ext));
  };

  return (
    <Container maxWidth="lg">
      <Box sx={{ my: 4 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
          <Typography variant="h4" component="h1" gutterBottom>
            Folders
          </Typography>
          <Box>
            <IconButton onClick={() => navigate('/')} sx={{ mr: 2 }}>
              <HomeIcon />
            </IconButton>
            <Button
              variant="contained"
              startIcon={<AddIcon />}
              onClick={() => setOpenDialog(true)}
            >
              Create Folder
            </Button>
          </Box>
        </Box>

        <Grid container spacing={3}>
          {folders.map((folder) => (
            <Grid item xs={12} sm={6} md={4} key={folder}>
              <Card>
                <CardContent>
                  <Typography variant="h6">{folder}</Typography>
                </CardContent>
                <CardActions>
                  <Button
                    size="small"
                    onClick={() => handleFolderClick(folder)}
                    variant={selectedFolder === folder ? "contained" : "text"}
                  >
                    {selectedFolder === folder ? "Viewing Files" : "View Files"}
                  </Button>
                  <Button
                    size="small"
                    color="error"
                    variant="text"
                    onClick={() => deleteFolder(folder)}
                  >
                    Delete
                  </Button>
                </CardActions>
              </Card>
            </Grid>
          ))}
        </Grid>

        {selectedFolder && (
          <Box sx={{ mt: 4 }}>
            <Typography variant="h5" gutterBottom>
              Files in {selectedFolder}
            </Typography>
            <Box sx={{ mb: 2 }}>
              <input
                type="file"
                id="file-upload"
                style={{ display: 'none' }}
                onChange={handleFileUpload}
              />
              <label htmlFor="file-upload">
                <Button
                  variant="contained"
                  component="span"
                  startIcon={<AddIcon />}
                >
                  Upload File
                </Button>
              </label>
            </Box>
            <List>
              {files.map((file) => (
                <ListItem key={file}>
                  <ListItemText primary={file} />
                  <ListItemSecondaryAction>
                    <IconButton
                      edge="end"
                      onClick={() => handleFilePreview(file)}
                      sx={{ mr: 1 }}
                    >
                      <VisibilityIcon />
                    </IconButton>
                    <IconButton
                      edge="end"
                      onClick={() => handleFileDownload(file)}
                      sx={{ mr: 1 }}
                    >
                      <DownloadIcon />
                    </IconButton>
                    <IconButton
                      edge="end"
                      onClick={() => handleFileDelete(file)}
                    >
                      <DeleteIcon />
                    </IconButton>
                  </ListItemSecondaryAction>
                </ListItem>
              ))}
            </List>
          </Box>
        )}

        <Dialog open={openDialog} onClose={() => setOpenDialog(false)}>
          <DialogTitle>Create New Folder</DialogTitle>
          <DialogContent>
            <TextField
              autoFocus
              margin="dense"
              label="Folder Name"
              type="text"
              fullWidth
              value={newFolderName}
              onChange={(e) => setNewFolderName(e.target.value)}
            />
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setOpenDialog(false)}>Cancel</Button>
            <Button onClick={createFolder} variant="contained">
              Create
            </Button>
          </DialogActions>
        </Dialog>

        <Dialog
          open={!!previewFile}
          onClose={() => setPreviewFile(null)}
          maxWidth="md"
          fullWidth
        >
          <DialogTitle>{previewFile?.name}</DialogTitle>
          <DialogContent>
            {previewFile && isImageFile(previewFile.name) ? (
              <img
                src={previewFile.url}
                alt={previewFile.name}
                style={{ width: '100%', height: 'auto' }}
              />
            ) : (
              <Typography>
                Preview not available for this file type. Please download to view.
              </Typography>
            )}
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setPreviewFile(null)}>Close</Button>
            {previewFile && (
              <Button
                onClick={() => handleFileDownload(previewFile.name)}
                variant="contained"
              >
                Download
              </Button>
            )}
          </DialogActions>
        </Dialog>
      </Box>
    </Container>
  );
};

export default Folders; 