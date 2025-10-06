from sqlmodel import Field, SQLModel
from sqlalchemy import Column, JSON
from datetime import date, datetime, timedelta

class User(SQLModel, table=True):
    email: str = Field(primary_key=True)
    username: str
    first_name: str
    last_name: str
    weight: int | None = None
    activity_level: str | None = None
    calorie_goal: int = 2000
    protein_goal: int = 0
    carb_goal: int = 0
    fat_goal: int = 0
    food_journal: list["JournalEntry"] = Field(sa_column=Column(JSON))
    
# class FoodJournal(SQLModel):
#     date: date
#     journal: list["JournalEntry"] = Field(sa_column=Column(JSON))

class JournalEntry(SQLModel):
    name: str
    time: str
    calories: int
    protein: int
    carbs: int
    fat: int

# class TokenData(SQLModel, table=True):
#     email: str | None = Field(primary_key=True)
    
# class Token(SQLModel, table=True):
#     access_token: str = Field(primary_key=True)
#     bearer: str = "bearer"