from fastapi import FastAPI, APIRouter, Depends
import os
from fastapi.responses import RedirectResponse
from helpers.config import get_settings, Settings

base_router = APIRouter(
    prefix='/api/v1',
    tags=['welcome']
)

@base_router.get('/welcome')
async def welcome(app_settings: Settings = Depends(get_settings)):

    
    APP_NAME = app_settings.APP_NAME
    APP_VERSION = app_settings.APP_VERSION
    
    return {
        'APP_NAME': APP_NAME,
        'APP_VERSION': APP_VERSION,
        'API_DOCS_SWAGGER': 'http://localhost:8000/docs#',
        'SOURCE_CODE': 'https://github.com/MhmdSyd/mini-rag',
    }

