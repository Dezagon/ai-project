from pydantic import BaseModel
from app.models import JournalEntry


class CreateUserRequest(BaseModel):
    email: str
    username: str
    first_name: str
    last_name: str
    password: str
    food_journal: list[JournalEntry] = []

class UpdateUserRequest(BaseModel):
    # email: str | None = None
    # username: str | None = None
    # first_name: str | None = None
    # last_name: str | None = None
    weight: int | None = None
    activity_level: str | None = None
    calorie_goal: int | None = None
    protein_goal: int | None = None
    carb_goal: int | None = None
    fat_goal: int | None = None

class UpdateUserFoodJournalRequest(BaseModel):
    journal_entries: list["JournalEntryRequest"]

class JournalEntryRequest(BaseModel):
    name: str
    time: str
    calories: int
    protein: int | None = None
    carbs: int | None = None
    fat: int | None = None


class TokenData(BaseModel):
    email: str
    
class Token(BaseModel):
    access_token: str
    bearer: str = "bearer"