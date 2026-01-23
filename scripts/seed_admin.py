#!/usr/bin/env python3
"""Script to seed the database with an initial admin user."""

import os
import sys

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from app.api.v1.admin.admin_model import AdminCreate, AdminRole
from app.api.v1.admin.admin_service import AdminService
from app.db import get_engine
from sqlmodel import SQLModel

def seed_admin():
    """Create an initial admin user from environment variables."""
    
    # Get credentials from environment
    username = os.getenv("ADMIN_USERNAME", "admin")
    password = os.getenv("ADMIN_PASSWORD")
    role_str = os.getenv("ADMIN_ROLE", "ADMIN")
    
    if not password:
        print("❌ Error: ADMIN_PASSWORD environment variable must be set")
        print("\nUsage:")
        print("  ADMIN_USERNAME=admin ADMIN_PASSWORD=yourpassword ADMIN_ROLE=ADMIN python scripts/seed_admin.py")
        print("\nRoles: VIEWER, EDITOR, ADMIN")
        sys.exit(1)
    
    # Validate role
    try:
        role = AdminRole[role_str.upper()]
    except KeyError:
        print(f"❌ Error: Invalid role '{role_str}'. Must be one of: VIEWER, EDITOR, ADMIN")
        sys.exit(1)
    
    # Initialize the database (create tables if they don't exist)
    # Import all models to register them with SQLModel.metadata
    from app.api.v1.events.events_repository import EventSQLModel
    from app.api.v1.state.state_repository import StateSQLModel
    from app.api.v1.admin.admin_repository import AdminUserSQLModel
    
    engine = get_engine()
    SQLModel.metadata.create_all(engine)
    
    # Initialize service
    admin_service = AdminService()
    
    # Check if admin already exists
    existing = admin_service.repository.get_by_username(username)
    if existing:
        # Check if we should force recreate (for testing/debugging)
        force_recreate = os.getenv("FORCE_RECREATE_ADMIN", "false").lower() == "true"
        
        if force_recreate:
            print(f"🔄 Force recreate enabled, deleting existing admin...")
            from sqlmodel import Session, select
            with Session(engine) as session:
                session.delete(existing)
                session.commit()
            print(f"✅ Deleted existing admin user")
        else:
            print(f"ℹ️  Admin user '{username}' already exists!")
            print(f"   ID: {existing.id}")
            print(f"   Role: {existing.role.value}")
            print(f"   Active: {existing.is_active}")
            print("   Skipping creation.")
            print("   To force recreate, set FORCE_RECREATE_ADMIN=true")
            sys.exit(0)
    
    print(f"🌱 Creating admin user...\n")
    print(f"   Username: {username}")
    print(f"   Role: {role.value}")
    
    # Create admin
    try:
        admin_create = AdminCreate(
            username=username,
            password=password,
            role=role
        )
        created_admin = admin_service.create_admin(admin_create)
        print(f"\n✅ Successfully created admin user!")
        print(f"   ID: {created_admin.id}")
        print(f"   Username: {created_admin.username}")
        print(f"   Role: {created_admin.role.value}")
        print(f"   Created at: {created_admin.created_at}")
    except Exception as e:
        print(f"❌ Failed to create admin user: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    seed_admin()
