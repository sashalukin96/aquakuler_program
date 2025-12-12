from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from os import getenv
from dotenv import load_dotenv
from sqlalchemy.testing import fails

load_dotenv()

# engine = create_engine(
#     getenv('DB_URL'),
#     connect_args={"check_same_thread": False}
# )

engine = create_engine(
    f'postgresql://{getenv('USER')}:{getenv('PASSWORD')}@{getenv('HOST')}:{getenv('PORT')}/{getenv('DB_NAME')}',
    echo=False
)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

class Base(DeclarativeBase):
	pass

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

