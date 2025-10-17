"""
Start the Newsletter Worker

This script starts the background worker that executes scheduled jobs.

Usage:
    python start_worker.py
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    from backend.worker import main
    import asyncio

    print("=" * 70)
    print("Newsletter Worker - Starting")
    print("=" * 70)

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nWorker stopped by user")
    except Exception as e:
        print(f"\n\nWorker crashed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
