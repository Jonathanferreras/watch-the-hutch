#!/usr/bin/env python3
"""Script to verify admin user exists and test password."""

import os
import sys

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from app.api.v1.admin.admin_service import AdminService
from app.api.v1.admin.admin_repository import AdminUserSQLModel
from app.db import get_engine
from sqlmodel import SQLModel
from app.security import verify_password

def verify_admin():
    """Verify admin user exists and test authentication."""
    
    # Import models
    from app.api.v1.events.events_repository import EventSQLModel
    from app.api.v1.state.state_repository import StateSQLModel
    from app.api.v1.admin.admin_repository import AdminUserSQLModel
    
    engine = get_engine()
    
    # Get admin username from env or use default
    username = os.getenv("ADMIN_USERNAME", "wth_admin")
    password = os.getenv("ADMIN_PASSWORD", "watchthehutchy1556")
    
    print(f"🔍 Verifying admin user: {username}\n")
    
    # Initialize service
    admin_service = AdminService()
    
    # Check if admin exists
    admin_sql = admin_service.repository.get_by_username(username)
    if not admin_sql:
        print(f"❌ Admin user '{username}' does not exist!")
        print("   Run the seed script to create it:")
        print(f"   ADMIN_USERNAME={username} ADMIN_PASSWORD={password} python scripts/seed_admin.py")
        sys.exit(1)
    
    print(f"✅ Admin user found:")
    print(f"   ID: {admin_sql.id}")
    print(f"   Username: {admin_sql.username}")
    print(f"   Role: {admin_sql.role.value}")
    print(f"   Active: {admin_sql.is_active}")
    print(f"   Created: {admin_sql.created_at}")
    
    # Test password verification
    print(f"\n🔐 Testing password verification...")
    password_valid = verify_password(password, admin_sql.password_hash)
    
    if password_valid:
        print(f"✅ Password verification successful!")
        print(f"   You can log in with:")
        print(f"   Username: {username}")
        print(f"   Password: {password}")
    else:
        print(f"❌ Password verification failed!")
        print(f"   The stored password hash does not match the provided password.")
        print(f"   You may need to recreate the admin user.")
    
    # Test authentication through service
    print(f"\n🔑 Testing authentication through service...")
    admin = admin_service.authenticate(username, password)
    if admin:
        print(f"✅ Authentication successful!")
        print(f"   Authenticated as: {admin.username} ({admin.role.value})")
    else:
        print(f"❌ Authentication failed!")
        print(f"   Check the logs for more details.")


if __name__ == "__main__":
    verify_admin()
