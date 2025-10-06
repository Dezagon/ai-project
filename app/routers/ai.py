# FastAPI SQLModel
from fastapi import APIRouter, Depends, HTTPException, status, Response
from typing import Annotated
from sqlmodel import Session, select

# Ollama
import asyncio
from ollama import AsyncClient, chat, ChatResponse

from app.routers.auth import get_current_user

from app.models import User
from app.database import get_db

router = APIRouter()

# USE OLLAMA API

# GET Reports
@router.get("/user_food_journal", status_code=status.HTTP_200_OK)
async def get_user_food_journal(current_user: Annotated[User, Depends(get_current_user)]):
    return current_user.food_journal

@router.get("/user", status_code=status.HTTP_200_OK)
async def get_user(current_user: Annotated[User, Depends(get_current_user)]) -> User:
    return current_user

@router.get("/ai_nutriton_suggestions", status_code=status.HTTP_200_OK)
async def get_ai_suggestions(current_user: Annotated[User, Depends(get_current_user)]) -> str:
    if current_user.weight and current_user.activity_level and current_user.calorie_goal and current_user.protein_goal and current_user.carb_goal and current_user.fat_goal:
        suggested_calories_message = {"role": "user", "content": f"Given weight {str(current_user.weight)}, macro goals only if they are not 0 or None: {str(current_user.protein_goal)} grams of protein, {str(current_user.carb_goal)} grams of carbohydrates, {str(current_user.fat_goal)} grams of fat, and activity level {current_user.activity_level}, provide a calorie goal"}
        # suggested_macros_adjustments_message = {"role": "user", "content": f"What kind of adjustments, if any, should be made given this food journal {current_user.food_journal}"}
        response: ChatResponse = chat(model='ALIENTELLIGENCE/personalizednutrition:latest', messages=[suggested_calories_message])
        return response.message.content
    raise HTTPException(status_code=status.HTTP_206_PARTIAL_CONTENT, detail="Not enough data for AI suggestions")

# PATCH Methods
    
