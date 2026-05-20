# 🚀 Deployment Guide - Step by Step

This guide will walk you through deploying your AI platform with all free tiers.

**Estimated time:** 45-60 minutes
**Total cost:** $0

---

## 📋 Prerequisites

Before starting, make sure you have:
- [ ] A GitHub account (for Cloudflare Pages)
- [ ] A Hugging Face account (free signup)
- [ ] A Cloudflare account (free signup)
- [ ] A Google account (for Firebase)

---

## Step 1: Set Up Firebase (Authentication + Database)

**Time:** 10-15 minutes

### 1.1 Create Firebase Project

1. Go to https://console.firebase.google.com/
2. Click **"Create a project"**
3. Project name: `ai-chat-platform` (or any name you like)
4. Disable Google Analytics (not needed)
5. Click **"Create project"**

### 1.2 Enable Authentication

1. In left sidebar, click **"Build"** → **"Authentication"**
2. Click **"Get Started"**
3. Enable **Email/Password** provider:
   - Click "Email/Password"
   - Toggle "Enable" to ON
   - Click "Save"
4. (Optional) Enable **Google** provider:
   - Click "Google"
   - Configure OAuth consent screen (follow prompts)
   - Enable the toggle
   - Click "Save"

### 1.3 Create Firestore Database

1. In left sidebar, click **"Build"** → **"Firestore Database"**
2. Click **"Create database"**
3. Choose **"Start in test mode"** (allows reads/writes temporarily)
4. Select region closest to your users (e.g., `us-central`)
5. Click **"Enable"**

### 1.4 Get Firebase Config (for Frontend)

1. Click ⚙️ **"Project settings"** (gear icon)
2. In "General" tab, scroll to "Your apps"
3. Click **"</>"** (Web app)
4. App nickname: `ai-chat-frontend`
5. Check "Also set up Firebase Hosting" (optional)
6. Click **"Register app"**
7. Copy the `firebaseConfig` object (looks like this):
   ```javascript
   const firebaseConfig = {
     apiKey: "AIzaSy...",
     authDomain: "your-project.firebaseapp.com",
     projectId: "your-project-id",
     storageBucket: "your-project.appspot.com",
     messagingSenderId: "123456789",
     appId: "1:123456789:web:abc123"
   };
   ```
8. **Important:** Update `frontend/js/firebase-config.js` with your config

### 1.5 Get Service Account Key (for Backend)

1. In Firebase Console, click ⚙️ **"Project settings"**
2. Click **"Service accounts"** tab
3. Click **"Generate new private key"**
4. Click **"Generate key"**
5. Save the JSON file securely (you'll need it for Hugging Face)

---

## Step 2: Deploy Backend to Hugging Face Spaces

**Time:** 15-20 minutes

### 2.1 Create Hugging Face Account

1. Go to https://huggingface.co/
2. Click **"Sign Up"** (top right)
3. Sign up with email or GitHub
4. Verify your email

### 2.2 Create New Space

1. Click your profile picture → **"New Space"**
2. Fill in details:
   - **Owner:** Your username
   - **Space name:** `ai-chat-backend`
   - **License:** `apache-2.0`
   - **Space SDK:** Select **"Docker"** (not Gradio/Streamlit)
   - **Space Hardware:** `CPU (free)`
3. Click **"Create Space"**

### 2.3 Upload Backend Files

You have 2 options:

#### Option A: Using Git (Recommended)

```bash
# 1. Clone the space (replace with your username)
git clone https://huggingface.co/spaces/YOUR_USERNAME/ai-chat-backend
cd ai-chat-backend

# 2. Copy your backend files
cp /path/to/your/backend/app.py .
cp /path/to/your/backend/requirements.txt .
cp /path/to/your/backend/Dockerfile .

# 3. Commit and push
git add .
git commit -m "Initial backend deployment"
git push
```

#### Option B: Using Web Interface

1. In your Space, click **"Files"** tab
2. Click **"Upload files"**
3. Drag and drop or select:
   - `app.py`
   - `requirements.txt`
   - `Dockerfile`
4. Click **"Commit changes"**

### 2.4 Add Firebase Secrets

1. In your Space, click **"Settings"** tab
2. Scroll to **"Repository secrets"**
3. Click **"New secret"**
4. Add these secrets:

   **Secret 1: FIREBASE_CREDENTIALS**
   - Name: `FIREBASE_CREDENTIALS`
   - Value: Copy-paste the ENTIRE content of your Firebase service account JSON file (from Step 1.5)
   - Click **"Save"**

   **Secret 2: MODEL_TIMEOUT** (optional)
   - Name: `MODEL_TIMEOUT`
   - Value: `300` (5 minutes)
   - Click **"Save"**

### 2.5 Wait for Build

1. Go to **"App"** tab in your Space
2. You'll see "Building..." status
3. Wait 3-5 minutes for build to complete
4. Once done, you should see "Running" status

### 2.6 Test Your API

Open a terminal and test:

```bash
# Test health endpoint
curl https://YOUR_USERNAME-ai-chat-backend.hf.space/health

# Test generation (this will wake up the model)
curl -X POST https://YOUR_USERNAME-ai-chat-backend.hf.space/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Hello, how are you?", "max_tokens": 50}'
```

**Note:** First request will take 30-60 seconds (cold start). Subsequent requests will be fast.

---

## Step 3: Deploy Frontend to Cloudflare Pages

**Time:** 10-15 minutes

### 3.1 Push Frontend to GitHub

1. Create a new repository on GitHub (e.g., `ai-chat-frontend`)
2. Push your frontend code:

```bash
# Navigate to your frontend folder
cd /path/to/your/frontend

# Initialize git repo
git init

# Add all files
git add .

# Commit
git commit -m "Initial frontend commit"

# Add remote (replace with your repo URL)
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/ai-chat-frontend.git

# Push
git push -u origin main
```

### 3.2 Create Cloudflare Account

1. Go to https://dash.cloudflare.com/sign-up
2. Sign up with email or GitHub
3. Verify your email

### 3.3 Deploy to Cloudflare Pages

1. In Cloudflare Dashboard, click **"Pages"** in left sidebar
2. Click **"Create a project"**
3. Click **"Connect to Git"**
4. Select your GitHub account
5. Select your repository (`ai-chat-frontend`)
6. Click **"Begin setup"**
7. Configure build settings:
   - **Project name:** `ai-chat-frontend` (or any name)
   - **Production branch:** `main`
   - **Build command:** (leave empty - static HTML)
   - **Build output directory:** `/` (or `./`)
8. Click **"Save and Deploy"**

9. Wait for deployment (1-2 minutes)
10. Click the provided URL to view your site

### 3.4 Update API URL

1. In your GitHub repo, edit `index.html`
2. Find the `CONFIG` object at the top of the script
3. Update `API_URL` with your Hugging Face Space URL:

```javascript
const CONFIG = {
    API_URL: 'https://your-username-ai-chat-backend.hf.space',
    // ... rest of config
};
```

4. Commit the change
5. Cloudflare will automatically redeploy

### 3.5 (Optional) Add Custom Domain

1. In Cloudflare Pages, click your project
2. Click **"Custom domains"** tab
3. Click **"Set up a custom domain"**
4. Enter your domain (e.g., `ai-chat.yourdomain.com`)
5. Follow Cloudflare's DNS instructions

---

## Step 4: Test Everything

### 4.1 Test Frontend

1. Visit your Cloudflare Pages URL (e.g., `https://ai-chat-frontend.pages.dev`)
2. You should see the chat interface
3. Check the status indicator (should show "Standby" or "Online")

### 4.2 Test Backend Connection

1. Type a message and click "Send"
2. First message will show "Waking up AI server..." (30-60 seconds)
3. You should get a response from the AI

### 4.3 Test Authentication (Optional)

1. Click "Login" button
2. Sign up with email/password
3. Check Firebase Console → Auth → Users (should see new user)
4. Check Firestore → conversations (should see chat history)

### 4.4 Verify Sleep/Wake

1. Wait 5 minutes without using the chat
2. Send another message
3. Should show "Waking up AI server..." again (model went to sleep)

---

## 🎉 Congratulations!

Your AI platform is now live with:

- ✅ **Frontend:** Cloudflare Pages (free forever)
- ✅ **Backend:** Hugging Face Spaces (free tier with sleep/wake)
- ✅ **Database:** Firebase (free tier)
- ✅ **Authentication:** Firebase Auth (free tier)
- ✅ **Total Cost:** $0/month

## 📊 Usage Limits Summary

| Service | Free Tier | Your Usage |
|---------|-----------|------------|
| Cloudflare Pages | Unlimited | ✅ Within limits |
| Hugging Face Spaces | 2 CPU, sleeps after 48h | ✅ Free tier |
| Firebase Auth | 10,000 users/mo | ✅ Within limits |
| Firebase Firestore | 50k reads, 20k writes/day | ✅ Within limits |

## 🔮 Next Steps

After you have it running, you can:

1. **Customize the UI** - Edit `index.html` to change colors, layout, etc.
2. **Change the AI Model** - Edit `backend/app.py` to use a different model
3. **Add Features** - Image generation, voice input, file uploads
4. **Custom Domain** - Add your own domain name
5. **Mobile App** - Wrap the web app with Capacitor or PWA

## 🆘 Need Help?

If something doesn't work:

1. Check the browser console (F12) for errors
2. Check Firebase Console for auth/database errors
3. Check Hugging Face Space logs for backend errors
4. Verify all URLs and API keys are correct

---

**🎊 You're all set! Happy building!**