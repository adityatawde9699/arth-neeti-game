
# Script to test Django environment in Railway

import os
import django
import sys

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.core.settings')

# Add the project root to sys.path
sys.path.append('/app')

try:
    django.setup()
    print("Django setup successful.")
except Exception as e:
    print(f"Django setup failed: {e}")
    sys.exit(1)

from django.db import connection, connections
from django.db.utils import OperationalError
from django.contrib.auth.models import User

def check_db():
    print("Checking database connection...")
    try:
        db_conn = connections['default']
        try:
            c = db_conn.cursor()
        except OperationalError:
            print("OperationalError: Could not connect to database.")
            return False
        else:
            print("Database connection successful.")
            return True
    except Exception as e:
        print(f"Database check failed: {e}")
        return False

def check_migrations():
    print("Checking for auth_user table...")
    try:
        count = User.objects.count()
        print(f"User table exists. User count: {count}")
        return True
    except Exception as e:
        print(f"User check failed (Migrations might need to run): {e}")
        return False

if __name__ == "__main__":
    if check_db():
        check_migrations()
