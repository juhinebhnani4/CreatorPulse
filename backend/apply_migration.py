"""
Apply database migration using Supabase Management API
"""
import os
import sys
from pathlib import Path
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def apply_migration():
    """Apply the newsletter schema fix using Supabase Management API."""

    # Get credentials
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_service_key = os.getenv('SUPABASE_SERVICE_KEY') or os.getenv('SUPABASE_KEY')

    if not supabase_url or not supabase_service_key:
        print("Error: Missing SUPABASE_URL or SUPABASE_SERVICE_KEY in .env file")
        return False

    # Extract project reference from URL
    # Format: https://PROJECT_REF.supabase.co
    project_ref = supabase_url.replace('https://', '').replace('.supabase.co', '')

    print(f"Project: {project_ref}")
    print(f"Supabase URL: {supabase_url}")

    # Read SQL migration
    sql_file = Path(__file__).parent / "migrations" / "fix_newsletters_schema.sql"
    with open(sql_file, 'r') as f:
        sql = f.read()

    print("\nApplying SQL migration...")
    print("=" * 60)
    print(sql)
    print("=" * 60)

    # Use PostgREST /rpc endpoint to execute SQL (requires a stored procedure)
    # Since we can't directly execute SQL via the Python client, we'll use
    # a workaround: alter the table via PostgREST metadata API

    # Alternative: Use psycopg2 or asyncpg to connect directly
    try:
        # Try using psycopg2 if available
        import psycopg2

        # Get database connection string from env
        db_url = os.getenv('DATABASE_URL')
        if not db_url:
            print("\nDATABASE_URL not found in .env")
            print("Please add your Supabase Postgres connection string:")
            print("DATABASE_URL=postgresql://postgres:[YOUR-PASSWORD]@db.xxx.supabase.co:5432/postgres")
            return False

        print("\nConnecting to database...")
        conn = psycopg2.connect(db_url)
        cursor = conn.cursor()

        print("Executing SQL...")
        cursor.execute(sql)
        conn.commit()

        print("SUCCESS! Migration applied.")

        cursor.close()
        conn.close()

        return True

    except ImportError:
        print("\npsycopg2 not installed.")
        print("Installing psycopg2...")

        import subprocess
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", "psycopg2-binary"], check=True)
            print("psycopg2 installed. Please run this script again.")
        except:
            print("\nCould not install psycopg2 automatically.")
            print("\nPlease install it manually:")
            print("  pip install psycopg2-binary")
            print("\nThen run this script again.")

        return False

    except Exception as e:
        print(f"\nError executing SQL: {e}")
        print("\nPlease apply the SQL manually in Supabase dashboard:")
        print("1. Go to https://supabase.com/dashboard")
        print("2. Select your project")
        print("3. Click 'SQL Editor'")
        print("4. Paste and run the SQL shown above")
        return False

if __name__ == '__main__':
    success = apply_migration()
    sys.exit(0 if success else 1)
