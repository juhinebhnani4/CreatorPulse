#!/usr/bin/env python3
"""
Quick start script for AI Newsletter Scraper.
"""

import subprocess
import sys
from pathlib import Path


def main():
    """Run the Streamlit application."""
    app_path = Path(__file__).parent / "src" / "streamlit_app.py"
    
    if not app_path.exists():
        print(f"❌ Error: Cannot find {app_path}")
        sys.exit(1)
    
    print("🚀 Starting AI Newsletter Scraper...")
    print("📱 The app will open in your browser at http://localhost:8501")
    print("⏹️  Press Ctrl+C to stop")
    print("-" * 60)
    
    try:
        subprocess.run(
            [sys.executable, "-m", "streamlit", "run", str(app_path)],
            check=True
        )
    except KeyboardInterrupt:
        print("\n👋 Application stopped")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

