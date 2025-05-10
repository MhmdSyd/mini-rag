from fastapi import FastAPI, APIRouter, Depends, Request
import os
from fastapi.responses import RedirectResponse
from helpers.config import get_settings, Settings

base_router = APIRouter(
    prefix='/api/v1',
    tags=['welcome']
)

@base_router.get('/welcome')
async def welcome(request: Request,app_settings: Settings = Depends(get_settings)):

    
    APP_NAME = app_settings.APP_NAME
    APP_VERSION = app_settings.APP_VERSION
    base_url = str(request.base_url).rstrip('/')
    docs_url = f"{base_url}/docs"
    SOURCE_CODE = app_settings.SOURCE_CODE
    
    return {
        'APP_NAME': APP_NAME,
        'APP_VERSION': APP_VERSION,
        'API_DOCS_SWAGGER': docs_url,
        'SOURCE_CODE': SOURCE_CODE,
    }

