from pydantic import BaseModel


class CreateUserRequest(BaseModel):
    email: str
    username: str
    first_name: str
    last_name: str
    password: str

class UpdateUserRequest(BaseModel):
    email: str | None = None
    username: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    weight: int | None = None
    activity_level: str | None = None
    calorie_goal: int | None = None
    protein_goal: int | None = None
    carb_goal: int | None = None
    fat_goal: int | None = None




class TokenData(BaseModel):
    email: str
    
class Token(BaseModel):
    access_token: str
    bearer: str = "bearer"