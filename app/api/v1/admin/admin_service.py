import logging
from datetime import datetime
from typing import Optional
from app.api.v1.admin.admin_model import AdminUser, AdminCreate
from app.api.v1.admin.admin_repository import AdminRepository, AdminUserSQLModel
from app.security import hash_password, verify_password

logger = logging.getLogger(__name__)

class AdminService:
    def __init__(self, repository: AdminRepository = None):
        self.repository = repository or AdminRepository()

    def create_admin(self, payload: AdminCreate) -> AdminUser:
        """Create a new admin user."""
        # Hash the password
        password_hash = hash_password(payload.password)
        
        # Create SQLModel directly (don't need domain model until after save)
        now = datetime.utcnow()
        admin_sql = AdminUserSQLModel(
            username=payload.username,
            password_hash=password_hash,
            role=payload.role,
            created_at=now,
            updated_at=now,
            last_login_at=None,
            is_active=True
        )
        
        # Save to database
        with self.repository._get_session() as session:
            session.add(admin_sql)
            session.commit()
            session.refresh(admin_sql)
            # Return domain model after save (now has id)
            return admin_sql.to_domain()

    def authenticate(self, username: str, password: str) -> Optional[AdminUser]:
        """Authenticate an admin user by username and password."""
        admin_sql = self.repository.get_by_username(username)
        
        if not admin_sql:
            logger.debug(f"Authentication failed: user '{username}' not found")
            return None
        
        if not admin_sql.is_active:
            logger.warning(f"Attempted login for inactive admin: {username}")
            return None
        
        password_valid = verify_password(password, admin_sql.password_hash)
        if not password_valid:
            logger.debug(f"Authentication failed: invalid password for user '{username}'")
            return None
        
        # Update last login timestamp
        self.repository.update_last_login(admin_sql.id)
        
        # Return domain model (without password_hash)
        return admin_sql.to_domain()