import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Load environment variables from a .env file (if present)
load_dotenv("../.env")

# Retrieve the database URL from environment variables; provide a default for local development.
DATABASE_URL = os.getenv("DATABASE_URL", "mysql+mysqlconnector://lucid:lucid@localhost/lucid-db")
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "mysecretkey")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
JWT_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", 30))

# Create the engine and sessionmaker
engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


