#!/usr/bin/env python3
"""
Simple backup script for dev database before TIMESTAMPTZ migration
"""

import os
import subprocess
from datetime import datetime
from pathlib import Path
import sys

def run_command(cmd, description):
    """Run a command and handle output"""
    print(f"  {description}...")
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            check=True
        )
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        print(f"    ❌ Error: {e.stderr}")
        return False, e.stderr

def main():
    # Configuration
    db_host = os.getenv('POSTGRES_HOST', 'localhost')
    db_port = os.getenv('POSTGRES_PORT', '5432')
    db_name = os.getenv('POSTGRES_DB', 'mindsethappybot')
    db_user = os.getenv('POSTGRES_USER', 'postgres')
    db_password = os.getenv('POSTGRES_PASSWORD', 'postgres')

    # Create backup directory
    backup_dir = Path('backups')
    backup_dir.mkdir(exist_ok=True)

    # Generate timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

    print("=" * 60)
    print("DEV DATABASE BACKUP BEFORE TIMESTAMPTZ MIGRATION")
    print("=" * 60)
    print(f"Database: {db_name}")
    print(f"Timestamp: {timestamp}")
    print()

    # Set PGPASSWORD environment variable
    os.environ['PGPASSWORD'] = db_password

    # Create backup filename
    backup_file = backup_dir / f"dev_backup_{timestamp}.sql"

    # Run pg_dump
    cmd = f'pg_dump -h {db_host} -p {db_port} -U {db_user} -d {db_name} --no-owner --no-acl'

    print("Creating database backup...")
    success, output = run_command(f'{cmd} > "{backup_file}"', "Dumping database")

    if success:
        # Check file size
        file_size = backup_file.stat().st_size
        size_mb = file_size / (1024 * 1024)
        print(f"  ✅ Backup created: {backup_file}")
        print(f"  📦 Size: {size_mb:.2f} MB")

        # Create a simple data snapshot
        snapshot_file = backup_dir / f"data_snapshot_{timestamp}.txt"
        snapshot_cmd = f'''psql -h {db_host} -p {db_port} -U {db_user} -d {db_name} -t -c "SELECT 'users: ' || COUNT(*) FROM users UNION SELECT 'moments: ' || COUNT(*) FROM moments UNION SELECT 'conversations: ' || COUNT(*) FROM conversations"'''

        print()
        print("Creating data snapshot...")
        success, output = run_command(f'{snapshot_cmd} > "{snapshot_file}"', "Getting row counts")

        if success:
            print(f"  ✅ Snapshot created: {snapshot_file}")
            # Read and display snapshot
            with open(snapshot_file, 'r') as f:
                snapshot_data = f.read().strip()
                print()
                print("Current data in database:")
                for line in snapshot_data.split('\n'):
                    if line.strip():
                        print(f"  - {line.strip()}")

        print()
        print("=" * 60)
        print("✅ BACKUP COMPLETE!")
        print("=" * 60)
        print()
        print(f"Backup saved to: {backup_file}")
        print()
        print("To restore if needed:")
        print(f'  psql -h {db_host} -U {db_user} -d {db_name} < "{backup_file}"')
        print()
        return True
    else:
        print()
        print("❌ BACKUP FAILED!")
        print("   Please check the error messages above")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)