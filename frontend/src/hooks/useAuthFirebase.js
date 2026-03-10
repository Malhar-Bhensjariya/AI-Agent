import { useState, useEffect } from 'react';
import {
  createUserWithEmailAndPassword,
  signInWithEmailAndPassword,
  signOut,
  onAuthStateChanged,
  signInWithPopup,
  GoogleAuthProvider,
  updateProfile,
  getIdToken
} from 'firebase/auth';
import { auth } from '../services/firebase';

/**
 * Hook for managing Firebase authentication state
 */
export const useAuth = () => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [idToken, setIdToken] = useState(null);

  useEffect(() => {
    // Listen to auth state changes
    const unsubscribe = onAuthStateChanged(auth, async (currentUser) => {
      try {
        if (currentUser) {
          setUser({
            uid: currentUser.uid,
            email: currentUser.email,
            displayName: currentUser.displayName || '',
            photoURL: currentUser.photoURL || '',
            emailVerified: currentUser.emailVerified,
            metadata: currentUser.metadata
          });
          // Get ID token for backend requests
          const token = await getIdToken(currentUser);
          setIdToken(token);
        } else {
          setUser(null);
          setIdToken(null);
        }
        setError(null);
      } catch (err) {
        console.error('Auth state error:', err);
        setError(err.message);
      } finally {
        setLoading(false);
      }
    });

    return () => unsubscribe();
  }, []);

  return { user, loading, error, idToken };
};

/**
 * Hook for email/password signup
 */
export const useSignUp = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const signup = async (email, password, displayName = '') => {
    setLoading(true);
    setError(null);

    try {
      // Create user account
      const userCredential = await createUserWithEmailAndPassword(auth, email, password);

      // Update profile with display name if provided
      if (displayName) {
        await updateProfile(userCredential.user, {
          displayName: displayName
        });
      }

      return userCredential.user;
    } catch (err) {
      const errorMessage = mapAuthError(err.code);
      setError(errorMessage);
      throw new Error(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  return { signup, loading, error };
};

/**
 * Hook for email/password login
 */
export const useLogin = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const login = async (email, password) => {
    setLoading(true);
    setError(null);

    try {
      const userCredential = await signInWithEmailAndPassword(auth, email, password);
      return userCredential.user;
    } catch (err) {
      const errorMessage = mapAuthError(err.code);
      setError(errorMessage);
      throw new Error(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  return { login, loading, error };
};

/**
 * Hook for Google OAuth signin
 */
export const useGoogleSignIn = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const signInWithGoogle = async () => {
    setLoading(true);
    setError(null);

    try {
      const provider = new GoogleAuthProvider();
      // Request additional scopes if needed
      provider.addScope('profile');
      provider.addScope('email');

      const result = await signInWithPopup(auth, provider);
      return result.user;
    } catch (err) {
      const errorMessage = mapAuthError(err.code);
      setError(errorMessage);
      throw new Error(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  return { signInWithGoogle, loading, error };
};

/**
 * Hook for logout
 */
export const useLogout = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const logout = async () => {
    setLoading(true);
    setError(null);

    try {
      await signOut(auth);
    } catch (err) {
      const errorMessage = mapAuthError(err.code);
      setError(errorMessage);
      throw new Error(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  return { logout, loading, error };
};

/**
 * Map Firebase auth error codes to user-friendly messages
 */
const mapAuthError = (code) => {
  const errorMap = {
    'auth/email-already-in-use': 'Email already registered',
    'auth/weak-password': 'Password must be at least 6 characters',
    'auth/invalid-email': 'Invalid email address',
    'auth/user-not-found': 'Email not found',
    'auth/wrong-password': 'Incorrect password',
    'auth/too-many-requests': 'Too many login attempts, try again later',
    'auth/account-exists-with-different-credential': 'Email already exists with different provider',
    'auth/popup-closed-by-user': 'Sign-in popup was closed',
    'auth/network-request-failed': 'Network error, check your connection'
  };

  return errorMap[code] || 'Authentication failed, please try again';
};
