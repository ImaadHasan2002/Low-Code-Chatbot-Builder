from datetime import datetime
from typing import Optional

from ..models.user import UserCreate, UserInDB
from ..utils.password import get_password_hash, verify_password

class AuthService:
    async def get_user_by_email(self, email: str) -> Optional[UserInDB]:
        """Get a user by email."""
        try:
            user = await UserInDB.find_one(UserInDB.email == email)
            return user
        except Exception as e:
            print(f"Error getting user by email: {str(e)}")
            return None

    async def create_user(self, user: UserCreate) -> UserInDB:
        """Create a new user."""
        try:
            user_in_db = UserInDB(
                email=user.email,
                username=user.name,
                hashed_password=get_password_hash(user.password),
                subscription_plan=user.subscription_plan
            )
            await user_in_db.insert()
            return user_in_db
        except Exception as e:
            raise Exception(f"Error creating user: {str(e)}")

    async def authenticate_user(self, email: str, password: str) -> Optional[UserInDB]:
        """Authenticate a user."""
        try:
            user = await self.get_user_by_email(email)
            if not user:
                return None
            if not verify_password(password, user.hashed_password):
                return None
            return user
        except Exception as e:
            print(f"Error authenticating user: {str(e)}")
            return None

    async def update_user(self, user_id: str, update_data: dict) -> Optional[UserInDB]:
        """Update user information."""
        try:
            user = await UserInDB.get(user_id)
            if not user:
                return None
            
            for field, value in update_data.items():
                if hasattr(user, field) and field not in ["id", "hashed_password"]:
                    setattr(user, field, value)
            
            user.updated_at = datetime.utcnow()
            await user.save()
            return user
        except Exception as e:
            print(f"Error updating user: {str(e)}")
            return None

    async def change_password(self, user_id: str, old_password: str, new_password: str) -> bool:
        """Change user password."""
        try:
            user = await UserInDB.get(user_id)
            if not user:
                return False
            
            # Verify old password
            if not verify_password(old_password, user.hashed_password):
                return False
            
            # Update password
            user.hashed_password = get_password_hash(new_password)
            user.updated_at = datetime.utcnow()
            await user.save()
            return True
        except Exception as e:
            print(f"Error changing password: {str(e)}")
            return False
