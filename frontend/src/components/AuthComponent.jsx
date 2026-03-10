import React, { useState } from 'react';
import { useAuthContext } from '../context/AuthContext';
import { useAuthenticatedCSVUpload } from '../hooks/useFirebaseCSVUpload';

/**
 * Auth Component - Example showing all Firebase authentication features
 * Demonstrates: Email/Password signup, login, Google OAuth, logout, CSV upload
 */
export const AuthComponent = () => {
  const { user, authentication, methods, error: authContextError } = useAuthContext();
  const { uploadAuthenticatedCSV, loading: uploadLoading, error: uploadError, uploadProgress, isAuthenticated } = useAuthenticatedCSVUpload(user);

  const [authMode, setAuthMode] = useState('login'); // 'login' | 'signup'
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [displayName, setDisplayName] = useState('');
  const [uploadedFiles, setUploadedFiles] = useState([]);

  // ===== Email/Password Signup =====
  const handleSignup = async (e) => {
    e.preventDefault();
    try {
      await methods.signup.fn(email, password, displayName);
      setEmail('');
      setPassword('');
      setDisplayName('');
      setAuthMode('login');
    } catch (err) {
      console.error('Signup failed:', err);
    }
  };

  // ===== Email/Password Login =====
  const handleLogin = async (e) => {
    e.preventDefault();
    try {
      await methods.login.fn(email, password);
      setEmail('');
      setPassword('');
    } catch (err) {
      console.error('Login failed:', err);
    }
  };

  // ===== Google OAuth =====
  const handleGoogleSignIn = async () => {
    try {
      await methods.signInWithGoogle.fn();
    } catch (err) {
      console.error('Google sign-in failed:', err);
    }
  };

  // ===== Logout =====
  const handleLogout = async () => {
    try {
      await methods.logout.fn();
    } catch (err) {
      console.error('Logout failed:', err);
    }
  };

  // ===== CSV Upload =====
  const handleCSVUpload = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;

    try {
      const result = await uploadAuthenticatedCSV(file);
      setUploadedFiles(prev => [...prev, result]);
      e.target.value = ''; // Reset file input
    } catch (err) {
      console.error('Upload failed:', err);
    }
  };

  // ===== If authenticated: Show user info and upload section =====
  if (authentication.isAuthenticated) {
    return (
      <div style={{ maxWidth: '600px', margin: '0 auto', padding: '20px' }}>
        <div style={{ border: '1px solid #ccc', padding: '20px', marginBottom: '20px' }}>
          <h2>Welcome, {user?.displayName || user?.email}!</h2>
          <p>Email: {user?.email}</p>
          {user?.photoURL && <img src={user.photoURL} alt="Profile" style={{ width: '50px', borderRadius: '50%' }} />}

          <button
            onClick={handleLogout}
            disabled={methods.logout.loading}
            style={{
              backgroundColor: '#dc3545',
              color: 'white',
              padding: '10px 20px',
              border: 'none',
              borderRadius: '5px',
              cursor: 'pointer',
              marginTop: '10px'
            }}
          >
            {methods.logout.loading ? 'Logging out...' : 'Logout'}
          </button>
        </div>

        {/* CSV Upload Section */}
        <div style={{ border: '1px solid #4CAF50', padding: '20px' }}>
          <h3>Upload CSV File</h3>
          <input
            type="file"
            accept=".csv"
            onChange={handleCSVUpload}
            disabled={uploadLoading || !isAuthenticated}
            style={{ marginBottom: '10px' }}
          />

          {uploadLoading && (
            <div>
              <p>Uploading... {uploadProgress}%</p>
              <div style={{
                width: '100%',
                backgroundColor: '#e0e0e0',
                borderRadius: '5px',
                overflow: 'hidden'
              }}>
                <div style={{
                  width: `${uploadProgress}%`,
                  backgroundColor: '#4CAF50',
                  height: '20px',
                  transition: 'width 0.3s'
                }} />
              </div>
            </div>
          )}

          {uploadError && <p style={{ color: 'red' }}>Error: {uploadError}</p>}

          {/* Show uploaded files */}
          {uploadedFiles.length > 0 && (
            <div style={{ marginTop: '20px' }}>
              <h4>Uploaded Files:</h4>
              <ul>
                {uploadedFiles.map((file, idx) => (
                  <li key={idx}>
                    <strong>{file.name}</strong> ({Math.round(file.size / 1024)}KB)
                    <br />
                    <small>Path: {file.storagePath}</small>
                    <br />
                    <small>Uploaded: {new Date(file.uploadedAt).toLocaleString()}</small>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      </div>
    );
  }

  // ===== If NOT authenticated: Show login/signup form =====
  return (
    <div style={{ maxWidth: '400px', margin: '0 auto', padding: '20px' }}>
      <div style={{ border: '1px solid #ccc', padding: '20px', borderRadius: '8px' }}>
        <h2>{authMode === 'login' ? 'Login' : 'Sign Up'}</h2>

        {/* Error messages */}
        {(authContextError || methods.login.error || methods.signup.error) && (
          <div style={{ backgroundColor: '#f8d7da', color: '#721c24', padding: '10px', borderRadius: '5px', marginBottom: '10px' }}>
            {authContextError || methods.login.error || methods.signup.error}
          </div>
        )}

        {/* Email/Password Form */}
        <form onSubmit={authMode === 'login' ? handleLogin : handleSignup}>
          {authMode === 'signup' && (
            <div style={{ marginBottom: '15px' }}>
              <label>
                Display Name:
                <input
                  type="text"
                  value={displayName}
                  onChange={(e) => setDisplayName(e.target.value)}
                  placeholder="Your Name"
                  style={{ width: '100%', padding: '8px', marginTop: '5px', boxSizing: 'border-box' }}
                />
              </label>
            </div>
          )}

          <div style={{ marginBottom: '15px' }}>
            <label>
              Email:
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="email@example.com"
                required
                style={{ width: '100%', padding: '8px', marginTop: '5px', boxSizing: 'border-box' }}
              />
            </label>
          </div>

          <div style={{ marginBottom: '15px' }}>
            <label>
              Password:
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••"
                required
                style={{ width: '100%', padding: '8px', marginTop: '5px', boxSizing: 'border-box' }}
              />
            </label>
          </div>

          <button
            type="submit"
            disabled={authMode === 'login' ? methods.login.loading : methods.signup.loading}
            style={{
              width: '100%',
              padding: '10px',
              backgroundColor: '#007bff',
              color: 'white',
              border: 'none',
              borderRadius: '5px',
              cursor: 'pointer',
              marginBottom: '10px'
            }}
          >
            {authMode === 'login' ? (methods.login.loading ? 'Logging in...' : 'Login') : (methods.signup.loading ? 'Signing up...' : 'Sign Up')}
          </button>
        </form>

        {/* Toggle between login and signup */}
        <p style={{ textAlign: 'center', marginBottom: '15px' }}>
          {authMode === 'login' ? "Don't have an account?" : 'Already have an account?'}{' '}
          <button
            onClick={() => setAuthMode(authMode === 'login' ? 'signup' : 'login')}
            style={{ background: 'none', border: 'none', color: '#007bff', cursor: 'pointer', textDecoration: 'underline' }}
          >
            {authMode === 'login' ? 'Sign Up' : 'Login'}
          </button>
        </p>

        {/* Google OAuth Button */}
        <button
          onClick={handleGoogleSignIn}
          disabled={methods.signInWithGoogle.loading}
          style={{
            width: '100%',
            padding: '10px',
            backgroundColor: '#db4437',
            color: 'white',
            border: 'none',
            borderRadius: '5px',
            cursor: 'pointer'
          }}
        >
          {methods.signInWithGoogle.loading ? 'Signing in...' : 'Sign in with Google'}
        </button>
      </div>
    </div>
  );
};

export default AuthComponent;
