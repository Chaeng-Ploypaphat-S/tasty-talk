import strawberry
from fastapi import FastAPI
from strawberry.fastapi import GraphQLRouter
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from typing import List, Optional

DATABASE_URL = "sqlite:///./customers.db"  # Change to your DB as needed

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Customer(Base):
    __tablename__ = "customers"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    zipcode = Column(String, nullable=False)
    favorite_food = Column(String, nullable=True)
    favorite_drinks = Column(String, nullable=True)
    favorite_vendors = Column(String, nullable=True)

Base.metadata.create_all(bind=engine)

@strawberry.type
class CustomerType:
    id: int
    name: str
    email: str
    zipcode: str
    favorite_food: Optional[str]
    favorite_drinks: Optional[str]
    favorite_vendors: Optional[str]

@strawberry.type
class Query:
    @strawberry.field
    def customers(self) -> List[CustomerType]:
        db = SessionLocal()
        customers = db.query(Customer).all()
        db.close()
        return [
            CustomerType(
                id=c.id,
                name=c.name,
                email=c.email,
                zipcode=c.zipcode,
                favorite_food=c.favorite_food,
                favorite_drinks=c.favorite_drinks,
                favorite_vendors=c.favorite_vendors,
            )
            for c in customers
        ]

@strawberry.input
class CustomerInput:
    name: str
    email: str
    zipcode: str
    favorite_food: Optional[str] = ""
    favorite_drinks: Optional[str] = ""
    favorite_vendors: Optional[str] = ""

@strawberry.type
class Mutation:
    @strawberry.mutation
    def signup(self, customer: CustomerInput) -> CustomerType:
        db = SessionLocal()
        db_customer = db.query(Customer).filter(Customer.email == customer.email).first()
        if db_customer:
            db.close()
            raise Exception("Email already registered")
        new_customer = Customer(
            name=customer.name,
            email=customer.email,
            zipcode=customer.zipcode,
            favorite_food=customer.favorite_food,
            favorite_drinks=customer.favorite_drinks,
            favorite_vendors=customer.favorite_vendors,
        )
        db.add(new_customer)
        db.commit()
        db.refresh(new_customer)
        db.close()
        return CustomerType(
            id=new_customer.id,
            name=new_customer.name,
            email=new_customer.email,
            zipcode=new_customer.zipcode,
            favorite_food=new_customer.favorite_food,
            favorite_drinks=new_customer.favorite_drinks,
            favorite_vendors=new_customer.favorite_vendors,
        )

schema = strawberry.Schema(query=Query, mutation=Mutation)

app = FastAPI()
graphql_app = GraphQLRouter(schema)
app.include_router(graphql_app, prefix="/graphql")