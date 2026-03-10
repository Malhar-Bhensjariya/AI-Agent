import { useState } from 'react';
import { ref, uploadBytes, getBytes } from 'firebase/storage';
import { storage } from '../services/firebase';

/**
 * Hook for uploading CSV files to Firebase Storage
 * Files are stored under: users/{uid}/csv/{timestamp-filename}
 */
export const useFirebaseCSVUpload = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [uploadProgress, setUploadProgress] = useState(0);

  const uploadCSV = async (file, uid) => {
    // Validate user is authenticated
    if (!uid) {
      const err = 'User must be authenticated to upload files';
      setError(err);
      throw new Error(err);
    }

    // Validate file type
    if (!file.name.toLowerCase().endsWith('.csv')) {
      const err = 'Only CSV files are allowed';
      setError(err);
      throw new Error(err);
    }

    // Validate file size (max 50MB)
    const maxSize = 50 * 1024 * 1024;
    if (file.size > maxSize) {
      const err = 'File size exceeds 50MB limit';
      setError(err);
      throw new Error(err);
    }

    setLoading(true);
    setError(null);
    setUploadProgress(0);

    try {
      // Generate storage path: users/{uid}/csv/{timestamp-filename}
      const timestamp = Date.now();
      const sanitizedName = file.name.replace(/\s+/g, '_');
      const storagePath = `users/${uid}/csv/${timestamp}-${sanitizedName}`;

      // Create reference to storage location
      const fileRef = ref(storage, storagePath);

      // Upload file to Firebase Storage
      // Note: uploadBytes doesn't provide progress events directly,
      // but we can simulate progress for UX
      setUploadProgress(50);
      const snapshot = await uploadBytes(fileRef, file);
      setUploadProgress(100);

      return {
        success: true,
        storagePath: storagePath,
        fullPath: snapshot.ref.fullPath,
        name: file.name,
        size: file.size,
        uploadedAt: new Date().toISOString()
      };
    } catch (err) {
      const errorMessage = mapStorageError(err.code || err.message);
      setError(errorMessage);
      throw new Error(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const downloadCSV = async (storagePath) => {
    try {
      const fileRef = ref(storage, storagePath);
      const bytes = await getBytes(fileRef);
      return bytes;
    } catch (err) {
      const errorMessage = mapStorageError(err.code || err.message);
      setError(errorMessage);
      throw new Error(errorMessage);
    }
  };

  return {
    uploadCSV,
    downloadCSV,
    loading,
    error,
    uploadProgress
  };
};

/**
 * Map Firebase storage error codes to user-friendly messages
 */
const mapStorageError = (code) => {
  const errorMap = {
    'storage/unknown': 'An unknown error occurred',
    'storage/object-not-found': 'File not found',
    'storage/bucket-not-found': 'Storage bucket not found',
    'storage/project-not-found': 'Project not found',
    'storage/quota-exceeded': 'Storage quota exceeded',
    'storage/unauthenticated': 'User must be authenticated',
    'storage/unauthorized': 'User does not have permission',
    'storage/retry-limit-exceeded': 'Upload failed after multiple retries',
    'storage/invalid-checksum': 'File checksum invalid',
    'storage/cancelled': 'Upload cancelled',
    'storage/invalid-event-name': 'Invalid event name',
    'storage/service-unavailable': 'Service temporarily unavailable',
    'storage/internal-error': 'Internal error occurred'
  };

  return errorMap[code] || 'Upload failed, please try again';
};

/**
 * Hook that combines authentication check + CSV upload
 * Ensures user is authenticated before allowing upload
 */
export const useAuthenticatedCSVUpload = (user) => {
  const { uploadCSV, downloadCSV, loading, error, uploadProgress } = useFirebaseCSVUpload();

  const uploadAuthenticatedCSV = async (file) => {
    if (!user || !user.uid) {
      throw new Error('User must be authenticated to upload files');
    }

    return uploadCSV(file, user.uid);
  };

  return {
    uploadAuthenticatedCSV,
    downloadCSV,
    loading,
    error,
    uploadProgress,
    isAuthenticated: !!user
  };
};
