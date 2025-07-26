"""
ESG Report Generation Tool - Main Entry Point
"""
import subprocess
import sys
import os

def main():
    """Main entry point for the ESG Report Generation Tool"""
    print("🌱 ESG Report Generation Tool")
    print("=" * 50)
    print("Starting the agentic ESG assessment application...")
    print("This tool uses AI agents to provide real-time ESG insights and generate comprehensive reports.")
    print()
    
    # Check if we're in the correct directory
    if not os.path.exists("app.py"):
        print("❌ Error: app.py not found. Please run this from the project root directory.")
        return
    
    try:
        # Run the Streamlit application
        print("🚀 Launching Streamlit application...")
        print("📱 The application will open in your default web browser.")
        print("🔗 If it doesn't open automatically, go to: http://localhost:8501")
        print()
        print("To stop the application, press Ctrl+C")
        print("=" * 50)
        
        subprocess.run([sys.executable, "-m", "streamlit", "run", "app.py"], check=True)
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error running Streamlit: {e}")
        print("💡 Make sure Streamlit is installed: pip install streamlit")
    except KeyboardInterrupt:
        print("\n👋 ESG Report Generator stopped by user.")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    main()
