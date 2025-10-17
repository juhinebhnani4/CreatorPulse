#!/usr/bin/env python3
"""
Quick migration runner for development.
Automatically runs Alembic migrations.
"""
import os
import sys
import subprocess
from pathlib import Path

def main():
    """Run database migrations."""
    # Change to backend directory
    backend_dir = Path(__file__).parent
    os.chdir(backend_dir)

    print("=" * 60)
    print("CreatorPulse Database Migration Runner")
    print("=" * 60)
    print()

    # Check if .env exists
    env_file = backend_dir.parent / '.env'
    if not env_file.exists():
        print("WARNING: .env file not found!")
        print()
        print("Please create a .env file with your database credentials:")
        print("  SUPABASE_URL=https://xxx.supabase.co")
        print("  SUPABASE_DB_PASSWORD=your-password")
        print()
        print("Or:")
        print("  DATABASE_URL=postgresql://postgres:password@db.xxx.supabase.co:5432/postgres")
        print()
        response = input("Continue anyway? (y/N): ")
        if response.lower() != 'y':
            return 1

    print("Running migrations...")
    print()

    try:
        # Run alembic upgrade
        result = subprocess.run(
            [sys.executable, "-m", "alembic", "upgrade", "head"],
            check=True,
            capture_output=True,
            text=True
        )

        print(result.stdout)
        if result.stderr:
            print(result.stderr)

        print()
        print("=" * 60)
        print("SUCCESS! Migrations applied.")
        print("=" * 60)
        print()
        print("Your newsletter generation should now work correctly!")
        print()

        return 0

    except subprocess.CalledProcessError as e:
        print()
        print("=" * 60)
        print("ERROR: Migration failed")
        print("=" * 60)
        print()
        print(e.stdout)
        print(e.stderr)
        print()
        print("Troubleshooting:")
        print("1. Check your database credentials in .env")
        print("2. Verify your IP is whitelisted in Supabase")
        print("3. Try manual migration (see backend/MIGRATIONS.md)")
        print()

        return 1

    except Exception as e:
        print()
        print("=" * 60)
        print("ERROR:", str(e))
        print("=" * 60)
        print()
        return 1

if __name__ == '__main__':
    sys.exit(main())
