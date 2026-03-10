import { initializeApp } from 'firebase/app';
import { getStorage } from 'firebase/storage';
import { getFirestore } from 'firebase/firestore';
import { getAuth } from 'firebase/auth';

const firebaseConfig = {
  apiKey: "AIzaSyBSLc9OZIrvAi0f83eTZfkI2HFDE8GvzmU",
  authDomain: "aida-57fc0.firebaseapp.com",
  projectId: "aida-57fc0",
  storageBucket: "aida-57fc0.firebasestorage.app",
  messagingSenderId: "688956737948",
  appId: "1:688956737948:web:592351d8751e14a10da059",
  measurementId: "G-J5MTC84L5J"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);

// Initialize Firebase Auth
export const auth = getAuth(app);

// Initialize Firebase Storage
export const storage = getStorage(app);

// Initialize Firestore
export const firestore = getFirestore(app);

// Set persistence to LOCAL (survive page refreshes)
import { setPersistence, browserLocalPersistence } from 'firebase/auth';
setPersistence(auth, browserLocalPersistence).catch(err => console.error('Persistence error:', err));

export default app;
