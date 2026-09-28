import datetime
import secrets
from typing import Any
from pydantic import BaseModel
from bson import ObjectId
from db import get_db


class ApiUser(BaseModel):
    id: str | None = None
    username: str
    api_key: str
    created_at: datetime.datetime
    is_active: bool
    last_active_at: datetime.datetime
    role: str  # "superuser" or "user"

    def __init__(self, username: str, role: str = "user", **data: Any):
        if "api_key" not in data:
            data["api_key"] = f"lia-{secrets.token_urlsafe(48)}"
        if "created_at" not in data:
            data["created_at"] = datetime.datetime.now()
        if "is_active" not in data:
            data["is_active"] = True
        if "last_active_at" not in data:
            data["last_active_at"] = datetime.datetime.now()
        super().__init__(username=username, role=role, **data)

    def check_is_active(self) -> bool:
        """Check if the api key is active."""
        return self.is_active

    def update_last_active_time(self) -> None:
        """Update the last login timestamp."""
        self.last_active_at = datetime.datetime.now()

    def update_active_status(self, is_active: bool) -> None:
        """Update the active status of the API key."""
        self.is_active = is_active

    def is_superuser(self) -> bool:
        """Check if the user is a superuser."""
        return self.role == "superuser"

    def to_dict(self) -> dict:
        """Convert the user to a dictionary."""
        result = {
            "username": self.username,
            "api_key": self.api_key,
            "created_at": self.created_at.isoformat(),
            "is_active": self.is_active,
            "last_active_at": self.last_active_at.isoformat(),
            "role": self.role
        }
        if self.id:
            result["id"] = self.id
        return result


def create_api_user(username: str, role: str = "user") -> ApiUser:
    """Create a new API user with a unique API key."""
    db = get_db()
    users_collection = db["api_users"]

    # Validate role
    if role not in ["user", "superuser"]:
        raise ValueError("Role must be either 'user' or 'superuser'")

    # Check if username already exists
    existing_user = users_collection.find_one({"username": username})
    if existing_user:
        raise ValueError(f"Username '{username}' already exists")

    new_user = ApiUser(username=username, role=role)
    result = users_collection.insert_one(new_user.to_dict())
    new_user.id = str(result.inserted_id)

    return new_user


def get_api_user(api_key: str) -> ApiUser | None:
    """Retrieve an API user by their API key."""
    db = get_db()
    users_collection = db["api_users"]
    user_data = users_collection.find_one({"api_key": api_key})

    if user_data:
        user_data["id"] = str(user_data.pop("_id"))
        return ApiUser(**user_data)
    return None


def get_me(api_key: str) -> ApiUser | None:
    """Get the current API user details."""
    return get_api_user(api_key)


def deactivate_api_user(user_id: str) -> bool:
    """Deactivate an API user by their API key."""
    db = get_db()
    users_collection = db["api_users"]
    result = users_collection.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": {"is_active": False}}
    )
    return result.modified_count > 0


def activate_api_user(user_id: str) -> bool:
    """Activate an API user by their API key."""
    db = get_db()
    users_collection = db["api_users"]
    result = users_collection.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": {"is_active": True}}
    )
    print(result)
    return result.modified_count > 0


def get_all_api_users() -> list[ApiUser]:
    """Retrieve all API users."""
    db = get_db()
    users_collection = db["api_users"]
    users_data = users_collection.find()
    result = []
    for user in users_data:
        user["id"] = str(user.pop("_id"))
        result.append(ApiUser(**user))
    return result


def delete_api_user(user_id: str) -> bool:
    """Delete an API user by their username."""
    db = get_db()
    users_collection = db["api_users"]
    result = users_collection.delete_one({"_id": ObjectId(user_id)})
    return result.deleted_count > 0


def get_user_by_id(user_id: str) -> ApiUser | None:
    """Retrieve an API user by their ID."""
    db = get_db()
    users_collection = db["api_users"]
    user_data = users_collection.find_one({"_id": ObjectId(user_id)})

    if user_data:
        user_data["id"] = str(user_data.pop("_id"))
        return ApiUser(**user_data)
    return None
