#!/usr/bin/env python3
"""
Interactive Demo Script for SmartOps Demo Commercial (Quest 2.2)
================================================================

Script interactivo para probar el flujo completo:
1. THE LOADER: Subir archivo (PDF/Imagen)
2. THE SHOW: Hacer preguntas (Chat RAG)
3. THE NEURALIZER: Cerrar sesión

Uso:
    python interactive_demo.py
    python interactive_demo.py <file_path>
"""

import requests
import os
import sys
import json
from typing import Optional

# Configuration
API_URL = "http://localhost:8001/demo"
DEFAULT_FILE = "menus/steak cortes y aves.jpg"
NEURALIZER_SECRET = "flash"

# Colors for terminal output
class Colors:
    GREEN = "\033[92m"
    BLUE = "\033[94m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    RESET = "\033[0m"
    BOLD = "\033[1m"


def print_success(msg: str):
    """Print success message in green."""
    print(f"{Colors.GREEN}[SUCCESS]{Colors.RESET} {msg}")


def print_info(msg: str):
    """Print info message in blue."""
    print(f"{Colors.BLUE}[INFO]{Colors.RESET} {msg}")


def print_warning(msg: str):
    """Print warning message in yellow."""
    print(f"{Colors.YELLOW}[WARNING]{Colors.RESET} {msg}")


def print_error(msg: str):
    """Print error message in red."""
    print(f"{Colors.RED}[ERROR]{Colors.RESET} {msg}")


def print_separator():
    """Print visual separator."""
    print(f"{Colors.BOLD}{'=' * 70}{Colors.RESET}")


def print_bot_response(response: str):
    """Print bot response formatted."""
    print(f"\n{Colors.BLUE}Bot:{Colors.RESET}")
    print(f"  {response}\n")


def upload_document(file_path: str) -> Optional[dict]:
    """
    THE LOADER: Upload a document (PDF or Image) to start demo session.
    
    Args:
        file_path: Path to the file (PDF, JPG, or PNG)
        
    Returns:
        Response dict with session_id, or None if failed
    """
    print_separator()
    print_info("Starting THE LOADER - Document Upload")
    print_separator()
    
    # Validate file exists
    if not os.path.exists(file_path):
        print_error(f"File not found: {file_path}")
        return None
    
    # Determine file type
    file_ext = os.path.splitext(file_path)[1].lower()
    if file_ext == ".pdf":
        content_type = "application/pdf"
    elif file_ext in [".jpg", ".jpeg"]:
        content_type = "image/jpeg"
    elif file_ext == ".png":
        content_type = "image/png"
    else:
        print_error(f"Unsupported file type: {file_ext}")
        return None
    
    # Prepare multipart form data
    with open(file_path, "rb") as f:
        files = {
            "file": (os.path.basename(file_path), f, content_type),
            "business_name": (None, "Demo Steakhouse"),
            "business_type": (None, "restaurante"),
        }
        
        try:
            print_info(f"Uploading {file_ext.upper()} file: {os.path.basename(file_path)}")
            response = requests.post(f"{API_URL}/upload", files=files, timeout=60)
            response.raise_for_status()
            
            data = response.json()
            session_id = data.get("session_id")
            message = data.get("message", "")
            
            print_success(f"Document uploaded successfully!")
            print_info(f"Session ID: {Colors.BOLD}{session_id}{Colors.RESET}")
            print_info(f"Message: {message}")
            
            return data
            
        except requests.exceptions.RequestException as e:
            print_error(f"Failed to upload document: {str(e)}")
            return None


def send_message(session_id: str, user_input: str) -> Optional[str]:
    """
    THE SHOW: Send a message to the bot and get RAG-powered response.
    
    Args:
        session_id: UUID of the demo session
        user_input: User's question/message
        
    Returns:
        Bot response string, or None if failed
    """
    try:
        payload = {
            "session_id": session_id,
            "message": user_input
        }
        
        response = requests.post(
            f"{API_URL}/message",
            json=payload,
            timeout=30
        )
        response.raise_for_status()
        
        data = response.json()
        bot_response = data.get("response", "No response received")
        
        return bot_response
        
    except requests.exceptions.RequestException as e:
        print_error(f"Failed to send message: {str(e)}")
        return None


def reset_session(session_id: str, save_lead: bool = False) -> bool:
    """
    THE NEURALIZER: Close demo session and clean up vectors.
    
    Args:
        session_id: UUID of the demo session
        save_lead: Whether to save a lead record
        
    Returns:
        True if successful, False otherwise
    """
    print_separator()
    print_info("Starting THE NEURALIZER - Session Cleanup")
    print_separator()
    
    try:
        payload = {
            "session_id": session_id,
            "secret_word": NEURALIZER_SECRET,
            "save_lead": save_lead
        }
        
        response = requests.post(
            f"{API_URL}/reset",
            json=payload,
            timeout=30
        )
        response.raise_for_status()
        
        data = response.json()
        message = data.get("message", "")
        vectors_deleted = data.get("deleted_vectors", 0)
        
        print_success("Session closed successfully!")
        print_info(f"Vectors deleted: {vectors_deleted}")
        print_info(f"Message: {message}")
        
        return True
        
    except requests.exceptions.RequestException as e:
        print_error(f"Failed to close session: {str(e)}")
        return False


def check_api_health() -> bool:
    """
    Check if API is accessible.
    
    Returns:
        True if API is healthy, False otherwise
    """
    try:
        response = requests.get(f"{API_URL}/health", timeout=5)
        response.raise_for_status()
        data = response.json()
        if data.get("status") == "healthy":
            return True
    except Exception:
        pass
    return False


def main():
    """Main interactive demo loop."""
    
    print_separator()
    print(f"{Colors.BOLD}SmartOps Demo Commercial - Interactive Testing{Colors.RESET}")
    print(f"{Colors.BOLD}Quest 2.2: PDF/Image Ingestion + RAG{Colors.RESET}")
    print_separator()
    
    # Get file path from command line or use default
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
    else:
        file_path = DEFAULT_FILE
    
    # Check API health
    print_info("Checking API health...")
    if not check_api_health():
        print_error(f"API is not accessible at {API_URL}")
        print_warning("Make sure FastAPI server is running: python -m uvicorn app.main:app --reload --port 8001")
        sys.exit(1)
    
    print_success("API is healthy!")
    
    # Step 1: Upload document (THE LOADER)
    upload_response = upload_document(file_path)
    if not upload_response:
        print_error("Failed to initialize demo session")
        sys.exit(1)
    
    session_id = upload_response.get("session_id")
    
    # Step 2: Interactive chat loop (THE SHOW)
    print_separator()
    print(f"{Colors.BOLD}Chat Loop - Type 'exit' to quit, 'reset' to close session{Colors.RESET}")
    print_separator()
    
    while True:
        try:
            user_input = input(f"\n{Colors.BOLD}You:{Colors.RESET} ").strip()
            
            if not user_input:
                print_warning("Please enter a message")
                continue
            
            # Check for special commands
            if user_input.lower() == "exit":
                print_info("Exiting chat loop...")
                break
            
            if user_input.lower() == "reset":
                print_info("Resetting session...")
                reset_session(session_id, save_lead=True)
                break
            
            # Send message to bot
            bot_response = send_message(session_id, user_input)
            if bot_response:
                print_bot_response(bot_response)
            else:
                print_error("Failed to get response from bot")
                
        except KeyboardInterrupt:
            print_warning("\nInterrupted by user")
            break
        except Exception as e:
            print_error(f"Unexpected error: {str(e)}")
            continue
    
    # Step 3: Close session (THE NEURALIZER)
    print_separator()
    print_info("Closing demo session...")
    reset_session(session_id, save_lead=False)
    
    print_separator()
    print_success("Demo session finished!")
    print_separator()


if __name__ == "__main__":
    main()
