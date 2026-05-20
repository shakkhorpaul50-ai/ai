/**
 * Firebase Configuration
 * 
 * Instructions:
 * 1. Go to https://console.firebase.google.com/
 * 2. Create a new project
 * 3. Enable Authentication (Email/Password, Google, etc.)
 * 4. Enable Firestore Database
 * 5. Go to Project Settings > General > Your apps > Web
 * 6. Register app and copy the config object here
 */

// Replace this with your actual Firebase config
const firebaseConfig = {
    apiKey: "YOUR_API_KEY",
    authDomain: "your-project.firebaseapp.com",
    projectId: "your-project-id",
    storageBucket: "your-project.appspot.com",
    messagingSenderId: "123456789",
    appId: "your-app-id"
};

// Initialize Firebase
import { initializeApp } from 'https://www.gstatic.com/firebasejs/10.7.0/firebase-app.js';
import { 
    getAuth, 
    createUserWithEmailAndPassword, 
    signInWithEmailAndPassword,
    signInWithPopup,
    GoogleAuthProvider,
    signOut,
    onAuthStateChanged
} from 'https://www.gstatic.com/firebasejs/10.7.0/firebase-auth.js';
import { 
    getFirestore, 
    collection, 
    doc, 
    setDoc, 
    getDoc,
    addDoc,
    query,
    where,
    orderBy,
    getDocs,
    serverTimestamp 
} from 'https://www.gstatic.com/firebasejs/10.7.0/firebase-firestore.js';

const app = initializeApp(firebaseConfig);
const auth = getAuth(app);
const db = getFirestore(app);
const googleProvider = new GoogleAuthProvider();

// ==================== AUTH FUNCTIONS ====================

export async function signUpWithEmail(email, password) {
    try {
        const userCredential = await createUserWithEmailAndPassword(auth, email, password);
        
        // Create user document in Firestore
        await setDoc(doc(db, "users", userCredential.user.uid), {
            email: email,
            createdAt: serverTimestamp(),
            lastLogin: serverTimestamp(),
            requestCount: 0
        });
        
        return { success: true, user: userCredential.user };
    } catch (error) {
        return { success: false, error: error.message };
    }
}

export async function signInWithEmail(email, password) {
    try {
        const userCredential = await signInWithEmailAndPassword(auth, email, password);
        
        // Update last login
        await setDoc(doc(db, "users", userCredential.user.uid), {
            lastLogin: serverTimestamp()
        }, { merge: true });
        
        return { success: true, user: userCredential.user };
    } catch (error) {
        return { success: false, error: error.message };
    }
}

export async function signInWithGoogle() {
    try {
        const result = await signInWithPopup(auth, googleProvider);
        
        // Create or update user document
        await setDoc(doc(db, "users", result.user.uid), {
            email: result.user.email,
            displayName: result.user.displayName,
            photoURL: result.user.photoURL,
            lastLogin: serverTimestamp(),
            requestCount: 0
        }, { merge: true });
        
        return { success: true, user: result.user };
    } catch (error) {
        return { success: false, error: error.message };
    }
}

export async function logOut() {
    try {
        await signOut(auth);
        return { success: true };
    } catch (error) {
        return { success: false, error: error.message };
    }
}

export function onAuthChange(callback) {
    return onAuthStateChanged(auth, callback);
}

// ==================== DATABASE FUNCTIONS ====================

export async function saveConversation(userId, messages) {
    try {
        const conversationRef = await addDoc(collection(db, "conversations"), {
            userId: userId,
            messages: messages,
            createdAt: serverTimestamp(),
            updatedAt: serverTimestamp()
        });
        
        // Update user's request count
        const userRef = doc(db, "users", userId);
        await setDoc(userRef, {
            requestCount: increment(1),
            lastRequest: serverTimestamp()
        }, { merge: true });
        
        return { success: true, conversationId: conversationRef.id };
    } catch (error) {
        return { success: false, error: error.message };
    }
}

export async function getUserConversations(userId) {
    try {
        const q = query(
            collection(db, "conversations"),
            where("userId", "==", userId),
            orderBy("createdAt", "desc")
        );
        
        const querySnapshot = await getDocs(q);
        const conversations = [];
        
        querySnapshot.forEach((doc) => {
            conversations.push({
                id: doc.id,
                ...doc.data()
            });
        });
        
        return { success: true, conversations };
    } catch (error) {
        return { success: false, error: error.message };
    }
}

export async function getUserStats(userId) {
    try {
        const userDoc = await getDoc(doc(db, "users", userId));
        if (userDoc.exists()) {
            return { success: true, stats: userDoc.data() };
        } else {
            return { success: false, error: "User not found" };
        }
    } catch (error) {
        return { success: false, error: error.message };
    }
}

// Helper for Firestore increment
function increment(n) {
    // This is a placeholder - in real Firestore use firebase.firestore.FieldValue.increment()
    return n;
}

// Export for use in other modules
export { auth, db };
export default app;