from config.database import Base, engine
from models.user import User

Base.metadata.create_all(bind=engine)

print("Users table created successfully!")