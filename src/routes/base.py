from fastapi import FastAPI, APIRouter
import os
from helpers.config import get_settings

base_router = APIRouter(
    prefix='/api/v1',
    tags=['api_v1']
)

@base_router.get('/')
async def welcome():

    app_settings = get_settings()
    APP_NAME = app_settings.APP_NAME
    APP_VERSION = app_settings.APP_NAME
    
    return {
        'APP_NAME': APP_NAME,
        'APP_VERSION': APP_VERSION
    }


