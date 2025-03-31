# app/routes.py

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
import time

from .schemas import UserCreate, UserLogin, UserResponse, PostCreate, PostResponse
from .dependencies import get_db, get_current_user
from .services import create_user, authenticate_user, create_post, get_user_posts, delete_post

router = APIRouter()

# In-memory cache: maps user_id to a tuple (posts, timestamp)
user_posts_cache = {}

@router.post("/signup", response_model=UserResponse)
def signup(user: UserCreate, db: Session = Depends(get_db)):
    """
    Endpoint to sign up a new user.
    """
    new_user = create_user(db, user.email, user.password)
    # Immediately log in the user and generate a JWT token.
    _, token = authenticate_user(db, user.email, user.password)
    return UserResponse(email=new_user.email, token=token)

@router.post("/login", response_model=UserResponse)
def login(user: UserLogin, db: Session = Depends(get_db)):
    """
    Endpoint to log in an existing user.
    """
    authenticated_user, token = authenticate_user(db, user.email, user.password)
    return UserResponse(email=authenticated_user.email, token=token)

@router.post("/addpost", response_model=PostResponse)
def add_post(
    post: PostCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Endpoint to add a new post for an authenticated user.
    """
    new_post = create_post(db, current_user.id, post.text)
    return PostResponse(
        id=new_post.id,
        text=new_post.text,
        created_at=new_post.created_at,
        user_id=new_post.user_id
    )

@router.get("/getposts", response_model=List[PostResponse])
def get_posts(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Endpoint to retrieve all posts, using caching to minimize DB load.
    """
    current_time = time.time()
    cache_entry = user_posts_cache.get(current_user.id, None)

    if cache_entry:
        cached_posts, timestamp = cache_entry
        if current_time - timestamp < 300:
            return cached_posts

    posts = get_user_posts(db, current_user)

    post_response = [
        PostResponse(
            id=p.id,
            text=p.text,
            created_at=p.created_at,
            user_id=p.user_id
        ) for p in posts
    ]

    # Cache the result for future requests by this user
    user_posts_cache[current_user.id] = (post_response, current_time)
    

    return post_response


@router.delete("/deletepost/{post_id}")
def delete_post_endpoint(
    post_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Deletes the specified post if it belongs to the authenticated user.
    
    - Requires a valid JWT token for authentication.
    - Accepts a post_id as a path parameter.
    - Clears the per-user cache upon successful deletion.
    
    Returns:
        A success message if the post is deleted.
    
    Raises:
        HTTPException: For invalid token, missing token, or if the post is not found or unauthorized.
    """
    # Attempt to delete the post; an error will be raised if deletion is not permitted.
    delete_post(db, post_id, current_user.id)
    
    # Invalidate the cache for the user if it exists
    if current_user.id in user_posts_cache:
        del user_posts_cache[current_user.id]
    
    return {"detail": "Post deleted successfully"}