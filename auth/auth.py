import datetime
import secrets
from typing import Any

from pydantic.v1 import BaseModel

from db import get_db


class ApiUser(BaseModel):
    username: str
    api_key: str
    created_at: datetime.datetime
    is_active: bool
    last_active_at: datetime.datetime
    is_superuser: bool

    def __init__(self, username: str, **data: Any):
        data["api_key"] = f"bsg-ai-{secrets.token_urlsafe(48)}"
        data["created_at"] = datetime.datetime.now()
        data["is_active"] = True
        data["last_active_at"] = datetime.datetime.now()
        data["is_superuser"] = False
        super().__init__(username=username, **data)

    def check_is_active(self) -> bool:
        """Check if the api key is active."""
        return self.is_active

    def update_last_active_time(self) -> None:
        """Update the last login timestamp."""
        self.last_active_at = datetime.datetime.now()

    def update_active_status(self, is_active: bool) -> None:
        """Update the active status of the API key."""
        self.is_active = is_active

    def set_superuser(self, is_superuser: bool) -> None:
        """Set the superuser status of the API user."""
        self.is_superuser = is_superuser

    def check_superuser(self) -> bool:
        """Check if the user is a superuser."""
        return self.is_superuser

    def to_dict(self) -> dict:
        """Convert the user to a dictionary."""
        return {
            "username": self.username,
            "api_key": self.api_key,
            "created_at": self.created_at.isoformat(),
            "is_active": self.is_active,
            "last_active_at": self.last_active_at.isoformat(),
            "is_superuser": self.is_superuser
        }


def create_api_user(username: str) -> ApiUser:
    """Create a new API user with a unique API key."""
    db = get_db()
    users_collection = db["api_users"]

    # Check if username already exists
    existing_user = users_collection.find_one({"username": username})
    if existing_user:
        raise ValueError(f"Username '{username}' already exists")

    new_user = ApiUser(username=username)
    users_collection.insert_one(new_user.to_dict())

    return new_user


def get_api_user(api_key: str) -> ApiUser | None:
    """Retrieve an API user by their API key."""
    db = get_db()
    users_collection = db["api_users"]
    user_data = users_collection.find_one({"api_key": api_key})

    if user_data:
        return ApiUser(**user_data)
    return None


def get_me(api_key: str) -> ApiUser | None:
    """Get the current API user details."""
    return get_api_user(api_key)


def deactivate_api_user(username: str) -> bool:
    """Deactivate an API user by their API key."""
    db = get_db()
    users_collection = db["api_users"]
    result = users_collection.update_one(
        {"username": username},
        {"$set": {"is_active": False}}
    )
    return result.modified_count > 0


def activate_api_user(username: str) -> bool:
    """Activate an API user by their API key."""
    db = get_db()
    users_collection = db["api_users"]
    result = users_collection.update_one(
        {"username": username},
        {"$set": {"is_active": True}}
    )
    print(result)
    return result.modified_count > 0

def get_all_api_users() -> list[ApiUser]:
    """Retrieve all API users."""
    db = get_db()
    users_collection = db["api_users"]
    users_data = users_collection.find()
    return [ApiUser(**user) for user in users_data]
