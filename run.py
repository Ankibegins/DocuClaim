#!/usr/bin/env python3
"""
ClauseMind - Startup Script
Run this script to start the ClauseMind application
"""

import os
import sys
import subprocess
import webbrowser
import time
from pathlib import Path

def check_dependencies():
    """Check if required dependencies are installed"""
    try:
        import fastapi
        import uvicorn
        import langchain
        import sentence_transformers
        import faiss
        import PyPDF2
        import google.generativeai
        print("✅ All dependencies are installed")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("Please install dependencies with: pip install -r requirements.txt")
        return False

def check_env_file():
    """Check if .env file exists and has required variables"""
    env_file = Path(".env")
    if not env_file.exists():
        print("⚠️  .env file not found")
        print("Creating .env file with default values...")
        
        env_content = """# ClauseMind Configuration
GEMINI_API_KEY=your_gemini_api_key_here
MODEL_NAME=gemini-pro
EMBEDDING_MODEL=all-MiniLM-L6-v2
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
TOP_K_RETRIEVAL=5
"""
        
        with open(env_file, 'w') as f:
            f.write(env_content)
        
        print("✅ Created .env file")
        print("⚠️  Please update GEMINI_API_KEY in .env file with your actual API key")
        return False
    
    # Check if API key is set
    with open(env_file, 'r') as f:
        content = f.read()
        if 'your_gemini_api_key_here' in content:
            print("⚠️  Please update GEMINI_API_KEY in .env file with your actual API key")
            return False
    
    print("✅ Environment configuration looks good")
    return True

def create_directories():
    """Create necessary directories"""
    directories = ['data', 'frontend']
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
    print("✅ Directories created")

def start_server():
    """Start the FastAPI server"""
    print("\n🚀 Starting ClauseMind server...")
    print("=" * 50)
    
    try:
        # Start the server
        subprocess.run([
            sys.executable, "-m", "uvicorn", 
            "app.main:app", 
            "--host", "0.0.0.0", 
            "--port", "8000", 
            "--reload"
        ])
    except KeyboardInterrupt:
        print("\n\n🛑 Server stopped by user")
    except Exception as e:
        print(f"\n❌ Error starting server: {e}")

def open_browser():
    """Open browser to the application"""
    try:
        time.sleep(3)  # Wait for server to start
        webbrowser.open("http://localhost:8000")
        webbrowser.open("http://localhost:8000/docs")
        print("🌐 Opened browser to application")
    except Exception as e:
        print(f"⚠️  Could not open browser: {e}")

def main():
    """Main startup function"""
    print("🧠 ClauseMind - Intelligent Clause Retriever & Decision System")
    print("=" * 60)
    
    # Check dependencies
    if not check_dependencies():
        return
    
    # Check environment
    env_ok = check_env_file()
    
    # Create directories
    create_directories()
    
    print("\n📋 Quick Start Guide:")
    print("1. Get your Gemini API key from: https://makersuite.google.com/app/apikey")
    print("2. Update the GEMINI_API_KEY in .env file")
    print("3. Upload a PDF document via the web interface")
    print("4. Start querying the system!")
    
    if not env_ok:
        print("\n⚠️  Please configure your API key before starting the server")
        return
    
    print("\n🎯 Starting application...")
    print("📖 API Documentation will be available at: http://localhost:8000/docs")
    print("🌐 Web Interface will be available at: http://localhost:8000")
    print("🛑 Press Ctrl+C to stop the server")
    
    # Start server
    start_server()

if __name__ == "__main__":
    main() 