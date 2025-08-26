#!/usr/bin/env python3
"""
Setup script for LangGraph Document Processing Workflow
"""

import subprocess
import sys
import os

def install_requirements():
    """Install required packages."""
    print("📦 Installing required packages...")
    
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ All packages installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install packages: {e}")
        return False

def check_python_version():
    """Check if Python version is compatible."""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        return False
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} is compatible")
    return True

def check_environment():
    """Check environment setup."""
    print("\n🔍 Checking environment...")
    
    # Check Python version
    if not check_python_version():
        return False
    
    # Check if virtual environment is activated
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("✅ Virtual environment is activated")
    else:
        print("⚠️  Virtual environment not detected")
        print("   Consider creating one: python3 -m venv .venv && source .venv/bin/activate")
    
    return True

def main():
    """Main setup function."""
    print("🚀 LangGraph Document Processing Workflow Setup\n")
    
    # Check environment
    if not check_environment():
        print("\n❌ Environment check failed. Please fix the issues above.")
        return
    
    # Install requirements
    if install_requirements():
        print("\n🎉 Setup completed successfully!")
        print("\n📝 Next steps:")
        print("1. Set your Azure OpenAI environment variables:")
        print("   export AZURE_OPENAI_API_KEY=your_api_key_here")
        print("   export AZURE_OPENAI_ENDPOINT=your_endpoint_here")
        print("   export AZURE_OPENAI_DEPLOYMENT_NAME=your_deployment_name")
        print("2. Test the workflow:")
        print("   python3 test_workflow.py")
        print("3. Run the main processor:")
        print("   python3 langgraph_document_processor.py")
    else:
        print("\n❌ Setup failed. Please check the error messages above.")

if __name__ == "__main__":
    main()
