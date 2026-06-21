// Import the functions you need from the SDKs you need
import { initializeApp } from "firebase/app";
import { getAnalytics } from "firebase/analytics";

// Your web app's Firebase configuration
// For Firebase JS SDK v7.20.0 and later, measurementId is optional
const firebaseConfig = {
  apiKey: "AIzaSyAkXEJbUw_BojC1G_Gy4PX-6fezHgvNq84",
  authDomain: "recommendation-be7d1.firebaseapp.com",
  projectId: "recommendation-be7d1",
  storageBucket: "recommendation-be7d1.firebasestorage.app",
  messagingSenderId: "92948354637",
  appId: "1:92948354637:web:6ac1c15d48b0cfa4c1ae04",
  measurementId: "G-1ZPXPS5NZR"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);
const analytics = getAnalytics(app);

export { app, analytics };
