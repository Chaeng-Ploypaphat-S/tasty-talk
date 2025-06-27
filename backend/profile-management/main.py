import strawberry
from fastapi import FastAPI
from strawberry.fastapi import GraphQLRouter
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "sqlite:///./profiles.db"
engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Profile(Base):
    __tablename__ = "profiles"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    address = Column(String, default=None, index=True)

Base.metadata.create_all(bind=engine)

@strawberry.type
class ProfileType:
    id: int
    name: str
    email: str = strawberry.field(default=None)
    address: str = strawberry.field(default=None)

def get_profiles():
    db = SessionLocal()
    profiles = db.query(Profile).all()
    db.close()
    return [ProfileType(id=p.id, name=p.name, email=p.email, address=p.address) for p in profiles]

@strawberry.type
class Query:
    profiles: list[ProfileType] = strawberry.field(resolver=get_profiles)

schema = strawberry.Schema(query=Query)

app = FastAPI()
graphql_app = GraphQLRouter(schema)
app.include_router(graphql_app, prefix="/graphql")