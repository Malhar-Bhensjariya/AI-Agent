import { useState } from 'react';

/**
 * Hook for uploading files to the file_service backend
 * Returns file_id and metadata after upload
 */
export const useFileUpload = (apiBaseUrl = 'http://localhost:5010') => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [fileId, setFileId] = useState(null);

  const uploadFile = async (file) => {
    setLoading(true);
    setError(null);
    setFileId(null);

    try {
      const formData = new FormData();
      formData.append('file', file);

      const response = await fetch(`${apiBaseUrl}/upload`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Upload failed');
      }

      const data = await response.json();
      if (data.success) {
        setFileId(data.file_id);
        return data.file_id;
      } else {
        throw new Error(data.error || 'Upload failed');
      }
    } catch (err) {
      setError(err.message);
      console.error('File upload error:', err);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  return { uploadFile, loading, error, fileId };
};

/**
 * Fetch signed URL for downloading a file
 */
export const getSignedUrl = async (fileId, apiBaseUrl = 'http://localhost:5010') => {
  try {
    const response = await fetch(`${apiBaseUrl}/file/${fileId}`);
    if (!response.ok) {
      throw new Error('Failed to fetch file metadata');
    }
    const data = await response.json();
    return data.signed_url; // Client can download using this URL
  } catch (err) {
    console.error('Error fetching signed URL:', err);
    throw err;
  }
};
