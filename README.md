# 🤖 AI Platform with Sleep/Wake Backend

Complete AI chat platform with:
- ✅ **Cloudflare Pages** frontend (free forever)
- ✅ **Hugging Face Spaces** backend with sleep/wake logic (free tier)
- ✅ **Firebase** authentication and data storage (free tier)
- ✅ **Zero cost** deployment (all free tiers)

## 📁 Project Structure

```
ai-platform/
├── backend/
│   ├── app.py              # FastAPI backend with sleep/wake
│   ├── requirements.txt    # Python dependencies
│   └── Dockerfile          # Hugging Face Spaces deployment
├── frontend/
│   ├── index.html          # Main HTML/JS/CSS
│   └── js/
│       └── firebase-config.js  # Firebase configuration
└── README.md               # This file
```

## 🚀 Quick Start Guide

### Step 1: Setup Firebase (Authentication + Database)

1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Click "Create Project"
3. Name your project (e.g., "ai-chat-platform")
4. Disable Google Analytics (not needed)
5. Click "Create"

**Enable Authentication:**
1. Go to "Build" → "Authentication" in left sidebar
2. Click "Get Started"
3. Enable "Email/Password" (toggle to "Enabled")
4. Enable "Google" (click, enable, save)
5. Add your domain to "Authorized domains" later

**Create Firestore Database:**
1. Go to "Build" → "Firestore Database"
2. Click "Create Database"
3. Choose "Start in test mode" (allows all reads/writes for 30 days)
4. Select region (choose closest to your users)
5. Click "Enable"

**Get Firebase Config:**
1. Go to Project Settings (gear icon)
2. In "General" tab, scroll to "Your apps"
3. Click "</>" (Web)
4. Register app with nickname
5. Copy the `firebaseConfig` object
6. Replace in `frontend/js/firebase-config.js`

**Get Service Account Key (for backend):**
1. Go to Project Settings → "Service accounts"
2. Click "Generate new private key"
3. Save the JSON file securely
4. You'll add this to Hugging Face Secrets later

### Step 2: Deploy Backend to Hugging Face Spaces

1. Go to [Hugging Face](https://huggingface.co/)
2. Sign up for free account
3. Click "New" → "Space"
4. Configure:
   - Owner: Your username
   - Space Name: `ai-chat-backend`
   - License: Apache-2.0
   - Space SDK: Docker (Blank)
   - Space Hardware: CPU (free tier)
5. Click "Create Space"

**Upload Backend Files:**

Method 1 - Git (Recommended):
```bash
# Clone the space
git clone https://huggingface.co/spaces/YOUR_USERNAME/ai-chat-backend
cd ai-chat-backend

# Copy backend files
cp /path/to/backend/app.py .
cp /path/to/backend/requirements.txt .
cp /path/to/backend/Dockerfile .

# Push
git add .
git commit -m "Initial backend deployment"
git push
```

Method 2 - Web Interface:
1. In your Space, click "Files" tab
2. Click "Upload files"
3. Upload `app.py`, `requirements.txt`, and `Dockerfile`

**Add Secrets (Firebase):**
1. In your Space, click "Settings" tab
2. Scroll to "Repository secrets"
3. Click "New secret"
4. Add these secrets:
   - Name: `FIREBASE_CREDENTIALS`
   - Value: Copy the entire content of your Firebase service account JSON file
5. Click "Save"

**Verify Deployment:**
1. Wait for Space to build (2-5 minutes)
2. Click "App" tab to see if it's running
3. Test API:
   ```
   curl https://YOUR_USERNAME-ai-chat-backend.hf.space/health
   ```

### Step 3: Deploy Frontend to Cloudflare Pages

1. Create a GitHub/GitLab repository
2. Push your frontend code:
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin https://github.com/YOUR_USERNAME/ai-chat-frontend.git
   git push -u origin main
   ```

3. Go to [Cloudflare Dashboard](https://dash.cloudflare.com/)
4. Sign up/login (free)
5. Click "Pages" in left sidebar
6. Click "Create a project"
7. Click "Connect to Git"
8. Select your repository
9. Configure build settings:
   - Project name: `ai-chat-frontend`
   - Production branch: `main`
   - Build command: (leave empty for static HTML)
   - Build output directory: `/` (root)
10. Click "Save and Deploy"

**Update API URL:**
1. Once deployed, go to your Cloudflare Pages domain
2. Edit `index.html` in your repo
3. Update `CONFIG.API_URL` to your Hugging Face Space URL:
   ```javascript
   const CONFIG = {
       API_URL: 'https://your-username-ai-chat-backend.hf.space'
       // ...
   };
   ```
4. Commit and push - Cloudflare will auto-deploy

### Step 4: Configure CORS on Backend

Edit `app.py` and update the CORS origins:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://your-frontend.pages.dev",  # Your Cloudflare Pages URL
        "https://your-custom-domain.com",   # If using custom domain
        "http://localhost:3000",            # Local development
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

Push changes to Hugging Face Space to redeploy.

## 🎉 Success!

Your AI platform is now live:

- **Frontend:** https://your-username.pages.dev
- **Backend API:** https://your-username-ai-chat-backend.hf.space
- **Firebase Console:** https://console.firebase.google.com

## 📝 Usage Limits (Free Tiers)

| Service | Free Tier Limits |
|---------|-----------------|
| **Cloudflare Pages** | Unlimited requests, 500 builds/month |
| **Hugging Face Spaces** | 2 CPU, 16GB RAM, sleeps after 48h inactivity |
| **Firebase Auth** | 10,000 users/month |
| **Firebase Firestore** | 50k reads, 20k writes, 20k deletes/day |

## 🔧 Customization

### Change AI Model

Edit `backend/app.py`:
```python
DEFAULT_MODEL = "microsoft/DialoGPT-medium"  # Change to any Hugging Face model
```

### Add More Features

- **Image generation:** Integrate Stable Diffusion
- **Voice:** Add speech-to-text with Whisper
- **File uploads:** Use Firebase Storage

## 🆘 Troubleshooting

**Backend not responding?**
- Check Hugging Face Space logs in "Files & Versions" → "Logs"
- Verify secrets are set correctly

**CORS errors?**
- Update `allow_origins` in `app.py` with your exact frontend URL
- Include `https://` prefix

**Firebase auth not working?**
- Check browser console for errors
- Verify Firebase config in `firebase-config.js`
- Ensure Auth providers are enabled in Firebase Console

## 📄 License

MIT License - Feel free to use for personal or commercial projects!