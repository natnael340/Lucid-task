
import secrets
import time
import datetime
import jwt
from datetime import timedelta
from typing import List, Tuple
from fastapi import HTTPException
from sqlalchemy.orm import Session
from .models import User, Post
from .config import JWT_SECRET_KEY, JWT_ALGORITHM, JWT_EXPIRE_MINUTES
from .utils import hash_password, verify_password

# In-memory cache for posts with a 5-minute time-to-live (TTL)


def create_user(db: Session, email: str, password: str) -> User:
    """
    Creates a new user in the database.
    """
    existing_user = db.query(User).filter(User.email == email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    user = User(email=email, password=hash_password(password))
    db.add(user)
    db.commit()
    db.refresh(user)

    return user

def authenticate_user(db: Session, email: str, password: str) -> Tuple[User, str]:
    """
    Authenticates a user by verifying the provided password and returns a JWT token.
    
    Args:
        db (Session): The database session.
        email (str): The user's email.
        password (str): The user's plain text password.
    
    Raises:
        HTTPException: If authentication fails.
    
    Returns:
        (User, str): The authenticated user and the JWT token.
    """
    user = db.query(User).filter(User.email == email).first()
    if user and verify_password(password, user.password):
        # Generate JWT token.
        payload = {
            "sub": user.email,
            "exp": datetime.datetime.utcnow() + timedelta(minutes=JWT_EXPIRE_MINUTES)
        }
        token = jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
        return user, token
    raise HTTPException(status_code=401, detail="Invalid email or password")


def create_post(db: Session, user_id: int, text: str) -> Post:
    """
    Creates a new post linked to a specific user.
    """
    post = Post(user_id=user_id, text=text)
    db.add(post)
    db.commit()
    db.refresh(post)
    return post


def get_user_posts(db: Session, user: User) -> List[Post]:
    """
    Retrieves all posts, using an in-memory cache to minimize DB calls.
    """
    
    posts = db.query(Post).filter_by(user_id=user.id).all()
    return posts


def delete_post(db: Session, post_id: int, user_id: int) -> bool:
    """
    Deletes a post with the given post_id if it belongs to the user.
    
    Args:
        db (Session): Database session.
        post_id (int): The ID of the post to delete.
        user_id (int): The ID of the authenticated user.
    
    Raises:
        HTTPException: If the post is not found or does not belong to the user.
    
    Returns:
        bool: True if the post was successfully deleted.
    """
    post = db.query(Post).filter(Post.id == post_id, Post.user_id == user_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found or unauthorized")
    
    db.delete(post)
    db.commit()
    return True