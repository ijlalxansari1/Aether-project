"""
FAQ / Glossary Router
"""
from fastapi import APIRouter
from fastapi.encoders import jsonable_encoder
from app.modules import faq

router = APIRouter()

@router.get("/faq")
async def get_faq():
    return jsonable_encoder({"items": faq.get_faq()})

@router.get("/glossary")
async def get_glossary():
    return jsonable_encoder({"items": faq.get_glossary()})
