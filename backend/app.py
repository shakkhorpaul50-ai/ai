"""
AI Backend API for Hugging Face Spaces
Features:
- Sleep/wake logic (loads model on first request, unloads after inactivity)
- Firebase integration for auth and data storage
- Chat completions API compatible with OpenAI format
"""

import os
import time
import json
import threading
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Depends, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
import uvicorn

# Firebase
import firebase_admin
from firebase_admin import credentials, auth, firestore

# Model handling
try:
    from transformers import AutoModelForCausalLM, AutoTokenizer
    import torch
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    print("Warning: transformers not installed. Using mock model.")

# ============== CONFIGURATION ==============

# Time before unloading model due to inactivity (5 minutes)
MODEL_TIMEOUT = int(os.getenv("MODEL_TIMEOUT", "300"))
# Maximum time for generation (30 seconds)
MAX_GENERATION_TIME = int(os.getenv("MAX_GENERATION_TIME", "30"))
# Model to use (small model for free tier)
DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "TinyLlama/TinyLlama-1.1B-Chat-v1.0")

# ============== FIREBASE SETUP ==============

def init_firebase():
    """Initialize Firebase Admin SDK"""
    try:
        # Check if already initialized
        firebase_admin.get_app()
    except ValueError:
        # Try to get credentials from environment
        firebase_creds = os.getenv("FIREBASE_CREDENTIALS")
        
        if firebase_creds:
            # Parse JSON from environment variable
            creds_dict = json.loads(firebase_creds)
            cred = credentials.Certificate(creds_dict)
        else:
            # Try to load from file
            cred_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "firebase-credentials.json")
            if os.path.exists(cred_path):
                cred = credentials.Certificate(cred_path)
            else:
                print("Warning: Firebase credentials not found. Auth will be disabled.")
                return None
        
        firebase_admin.initialize_app(cred)
        print("Firebase initialized successfully")
    
    return firestore.client()

# ============== MODEL MANAGER (SLEEP/WAKE) ==============

class ModelManager:
    """
    Manages AI model with sleep/wake behavior:
    - Model is unloaded after period of inactivity
    - Loaded on-demand when request comes in
    - Tracks usage statistics
    """
    
    def __init__(self):
        self.model = None
        self.tokenizer = None
        self.last_used = None
        self.lock = threading.Lock()
        self.stats = {
            "loads": 0,
            "unloads": 0,
            "total_requests": 0,
            "total_tokens": 0
        }
        self._cleanup_thread = threading.Thread(target=self._cleanup_loop, daemon=True)
        self._cleanup_thread.start()
    
    def _cleanup_loop(self):
        """Background thread to unload model after inactivity"""
        while True:
            time.sleep(60)  # Check every minute
            with self.lock:
                if self.model is not None and self.last_used is not None:
                    idle_time = time.time() - self.last_used
                    if idle_time > MODEL_TIMEOUT:
                        print(f"Unloading model due to inactivity ({idle_time:.0f}s)")
                        self._unload_model()
    
    def _load_model(self):
        """Load model into memory"""
        if not TRANSFORMERS_AVAILABLE:
            print("Warning: Using mock model (transformers not installed)")
            self.model = "mock"
            self.tokenizer = "mock"
            return
        
        print(f"Loading model: {DEFAULT_MODEL}")
        start_time = time.time()
        
        self.tokenizer = AutoTokenizer.from_pretrained(
            DEFAULT_MODEL,
            trust_remote_code=True
        )
        
        self.model = AutoModelForCausalLM.from_pretrained(
            DEFAULT_MODEL,
            torch_dtype=torch.float16,
            device_map="auto",
            trust_remote_code=True
        )
        
        load_time = time.time() - start_time
        print(f"Model loaded in {load_time:.2f}s")
        
        self.stats["loads"] += 1
    
    def _unload_model(self):
        """Unload model from memory"""
        if self.model is not None:
            if TRANSFORMERS_AVAILABLE and self.model != "mock":
                del self.model
                del self.tokenizer
                import gc
                gc.collect()
                if torch.cuda.is_available():
                    torch.cuda.empty_cache()
            
            self.model = None
            self.tokenizer = None
            self.stats["unloads"] += 1
            print("Model unloaded")
    
    def generate(self, prompt: str, max_tokens: int = 100) -> Dict[str, Any]:
        """Generate text with automatic model loading"""
        with self.lock:
            # Load model if not loaded
            if self.model is None:
                self._load_model()
            
            self.last_used = time.time()
            self.stats["total_requests"] += 1
            
            # Generate
            if not TRANSFORMERS_AVAILABLE or self.model == "mock":
                # Mock generation for testing
                result = f"[Mock response to: {prompt[:50]}...]"
                tokens = len(result.split())
            else:
                inputs = self.tokenizer(prompt, return_tensors="pt").to(self.model.device)
                
                with torch.no_grad():
                    outputs = self.model.generate(
                        **inputs,
                        max_new_tokens=max_tokens,
                        temperature=0.7,
                        top_p=0.9,
                        pad_token_id=self.tokenizer.eos_token_id
                    )
                
                result = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
                tokens = outputs.shape[1] - inputs.input_ids.shape[1]
            
            self.stats["total_tokens"] += tokens
            
            return {
                "text": result,
                "tokens": tokens,
                "model": DEFAULT_MODEL
            }
    
    def get_stats(self) -> Dict[str, Any]:
        """Get model statistics"""
        return {
            **self.stats,
            "loaded": self.model is not None,
            "last_used": self.last_used,
            "idle_time": time.time() - self.last_used if self.last_used else None
        }

# ============== Pydantic Models ==============

class ChatMessage(BaseModel):
    role: str = Field(..., description="Role: system, user, or assistant")
    content: str = Field(..., description="Message content")

class ChatCompletionRequest(BaseModel):
    model: str = Field(default=DEFAULT_MODEL, description="Model to use")
    messages: List[ChatMessage] = Field(..., description="Chat messages")
    max_tokens: int = Field(default=100, description="Maximum tokens to generate")
    temperature: float = Field(default=0.7, description="Sampling temperature")

class GenerateRequest(BaseModel):
    prompt: str = Field(..., description="Prompt text")
    max_tokens: int = Field(default=100, description="Maximum tokens to generate")

class HealthResponse(BaseModel):
    status: str
    model_loaded: bool
    stats: Dict[str, Any]

# ============== FASTAPI APP ==============

# Global model manager
model_manager = ModelManager()

# Security
security = HTTPBearer(auto_error=False)

# Firestore client (initialized lazily)
db = None

def get_db():
    """Get Firestore client"""
    global db
    if db is None:
        db = init_firebase()
    return db

async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify Firebase ID token"""
    if not credentials:
        return None
    
    try:
        decoded_token = auth.verify_id_token(credentials.credentials)
        return decoded_token
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid authentication credentials: {str(e)}"
        )

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    # Startup
    print("🚀 Starting AI Backend Server...")
    print(f"   Model: {DEFAULT_MODEL}")
    print(f"   Timeout: {MODEL_TIMEOUT}s")
    print(f"   Max generation time: {MAX_GENERATION_TIME}s")
    
    # Initialize Firebase
    global db
    db = init_firebase()
    if db:
        print("✅ Firebase initialized")
    else:
        print("⚠️ Firebase not initialized (running without auth)")
    
    yield
    
    # Shutdown
    print("🛑 Shutting down...")
    if model_manager.model is not None:
        model_manager._unload_model()

# Create FastAPI app
app = FastAPI(
    title="AI Backend API",
    description="Sleep/wake AI model with Firebase integration",
    version="1.0.0",
    lifespan=lifespan
)

# CORS - Allow Cloudflare Pages frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============== API ENDPOINTS ==============

@app.get("/", response_model=HealthResponse)
async def root():
    """Root endpoint - returns health status"""
    return HealthResponse(
        status="ok",
        model_loaded=model_manager.model is not None,
        stats=model_manager.get_stats()
    )

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return await root()

@app.post("/generate")
async def generate(
    request: GenerateRequest,
    user=Depends(verify_token)
):
    """Generate text from prompt"""
    try:
        # Log request to Firestore if available
        db = get_db()
        if db and user:
            db.collection('generations').add({
                'user_id': user.get('uid'),
                'prompt': request.prompt[:100],  # Truncate
                'timestamp': firestore.SERVER_TIMESTAMP
            })
        
        # Generate
        result = model_manager.generate(
            prompt=request.prompt,
            max_tokens=request.max_tokens
        )
        
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Generation failed: {str(e)}"
        )

@app.post("/chat/completions")
async def chat_completions(
    request: ChatCompletionRequest,
    user=Depends(verify_token)
):
    """OpenAI-compatible chat completions API"""
    try:
        # Convert messages to prompt
        prompt = ""
        for msg in request.messages:
            if msg.role == "system":
                prompt += f"System: {msg.content}\n"
            elif msg.role == "user":
                prompt += f"User: {msg.content}\n"
            elif msg.role == "assistant":
                prompt += f"Assistant: {msg.content}\n"
        prompt += "Assistant:"
        
        # Generate
        result = model_manager.generate(
            prompt=prompt,
            max_tokens=request.max_tokens
        )
        
        # Format as OpenAI response
        return {
            "id": f"chatcmpl-{int(time.time())}",
            "object": "chat.completion",
            "created": int(time.time()),
            "model": request.model,
            "choices": [{
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": result["text"].split("Assistant:")[-1].strip()
                },
                "finish_reason": "stop"
            }],
            "usage": {
                "prompt_tokens": len(prompt.split()),
                "completion_tokens": result["tokens"],
                "total_tokens": len(prompt.split()) + result["tokens"]
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Chat completion failed: {str(e)}"
        )

@app.get("/stats")
async def get_stats(user=Depends(verify_token)):
    """Get model statistics"""
    return model_manager.get_stats()

@app.post("/admin/wake")
async def wake_model(user=Depends(verify_token)):
    """Manually wake up the model"""
    if not user or not user.get('admin'):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    if model_manager.model is None:
        model_manager._load_model()
    
    return {"status": "awake", "stats": model_manager.get_stats()}

@app.post("/admin/sleep")
async def sleep_model(user=Depends(verify_token)):
    """Manually put model to sleep"""
    if not user or not user.get('admin'):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    if model_manager.model is not None:
        model_manager._unload_model()
    
    return {"status": "sleeping", "stats": model_manager.get_stats()}

# ============== MAIN ==============

if __name__ == "__main__":
    port = int(os.getenv("PORT", "7860"))
    uvicorn.run(app, host="0.0.0.0", port=port)
