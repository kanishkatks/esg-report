#!/usr/bin/env python3
"""
Installation script for ESG Report Generator
"""
import subprocess
import sys
import os

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        if e.stdout:
            print(f"Output: {e.stdout}")
        if e.stderr:
            print(f"Error: {e.stderr}")
        return False

def main():
    """Main installation process"""
    print("🌱 ESG Report Generator - Installation Script")
    print("=" * 50)
    
    # Check Python version
    if sys.version_info < (3, 11):
        print("❌ Python 3.11 or higher is required")
        sys.exit(1)
    
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")
    
    # Install core dependencies first
    core_deps = [
        "streamlit>=1.28.0",
        "pandas>=2.0.0",
        "plotly>=5.17.0",
        "matplotlib>=3.7.0",
        "requests>=2.31.0",
        "python-dotenv>=1.0.0",
        "pydantic>=2.0.0",
        "reportlab>=4.0.0",
        "pillow>=10.0.0"
    ]
    
    print("\n📦 Installing core dependencies...")
    for dep in core_deps:
        if not run_command(f"pip install {dep}", f"Installing {dep.split('>=')[0]}"):
            print(f"⚠️ Failed to install {dep}, continuing...")
    
    # Install optional dependencies
    optional_deps = [
        "mistralai>=0.4.0",
        "PyPDF2>=3.0.0",
        "python-docx>=0.8.11",
        "openpyxl>=3.1.0",
        "langchain>=0.1.0",
        "crewai>=0.28.0"
    ]
    
    print("\n📦 Installing optional dependencies...")
    for dep in optional_deps:
        if not run_command(f"pip install {dep}", f"Installing {dep.split('>=')[0]}"):
            print(f"⚠️ Optional dependency {dep} failed to install, will use fallback")
    
    # Create .env file if it doesn't exist
    if not os.path.exists('.env'):
        print("\n📝 Creating .env file...")
        try:
            with open('.env.example', 'r') as example:
                content = example.read()
            with open('.env', 'w') as env_file:
                env_file.write(content)
            print("✅ .env file created from template")
            print("💡 Please edit .env file to add your Mistral API key")
        except Exception as e:
            print(f"⚠️ Could not create .env file: {e}")
    
    # Create data directories
    os.makedirs('data', exist_ok=True)
    os.makedirs('logs', exist_ok=True)
    print("✅ Created data and logs directories")
    
    print("\n🎉 Installation completed!")
    print("\n📋 Next steps:")
    print("1. Edit .env file to add your Mistral API key (optional)")
    print("2. Run: python main.py")
    print("3. Or run: streamlit run app.py")
    print("\n🔗 For help, see README.md")

if __name__ == "__main__":
    main()