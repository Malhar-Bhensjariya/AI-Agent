import React, { createContext, useContext } from 'react';
import { useAuth, useSignUp, useLogin, useGoogleSignIn, useLogout } from '../hooks/useAuthFirebase';

/**
 * Auth Context - provides authentication state and methods to entire app
 */
const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const { user, loading, error: authError, idToken } = useAuth();
  const { signup, loading: signupLoading, error: signupError } = useSignUp();
  const { login, loading: loginLoading, error: loginError } = useLogin();
  const { signInWithGoogle, loading: googleLoading, error: googleError } = useGoogleSignIn();
  const { logout, loading: logoutLoading, error: logoutError } = useLogout();

  const value = {
    // Auth state
    user,
    authentication: {
      loading,
      isAuthenticated: !!user,
      idToken
    },

    // Auth methods
    methods: {
      signup: { fn: signup, loading: signupLoading, error: signupError },
      login: { fn: login, loading: loginLoading, error: loginError },
      signInWithGoogle: { fn: signInWithGoogle, loading: googleLoading, error: googleError },
      logout: { fn: logout, loading: logoutLoading, error: logoutError }
    },

    // Combined error state
    error: authError || signupError || loginError || googleError || logoutError
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

/**
 * Hook to use Auth context
 */
export const useAuthContext = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuthContext must be used within AuthProvider');
  }
  return context;
};

/**
 * HOC for protecting routes - requires authentication
 */
export const ProtectedRoute = ({ children, fallback = null }) => {
  const { authentication } = useAuthContext();

  if (authentication.loading) {
    return <div>Loading...</div>;
  }

  if (!authentication.isAuthenticated) {
    return fallback || <div>Please log in to continue</div>;
  }

  return children;
};
