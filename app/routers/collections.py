import os
import shutil
from typing import Annotated
from fastapi import Depends, FastAPI, APIRouter, HTTPException, File, UploadFile
from sqlalchemy import func, select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from app.db.models import Word
from app.schemas.schemas import ResponseUser, WordResponse, WordBase, CollectionRequest
from app.db.session import get_db
from app.routers.auth import get_current_user
from app.db.crud import *
from fastapi.responses import StreamingResponse
from PIL import Image
from io import BytesIO
from loguru import logger

logger.add("info.log")

router = APIRouter(prefix='', tags=['collections'])


@router.post("/collection", status_code=status.HTTP_201_CREATED)
async def create_collection(
    collection_request: CollectionRequest,
    db: AsyncSession = Depends(get_db),
    current_user: ResponseUser = Depends(get_current_user)
):

    return await db_create_collection(
        db=db,
        name=collection_request.name,
        words_ids=collection_request.words_ids,
        is_public=collection_request.is_public,
        user_id=current_user['id']
    )


@router.get("/collection/all")
async def get_all_collections(owner_id: int = None, db: AsyncSession = Depends(get_db)):
    return await db_get_all_collections(db=db, owner_id=owner_id)


@router.get("/collection/{collection_id}")
async def get_one_collection(collection_id: int, db: AsyncSession = Depends(get_db)):
    return await db_get_one_collection(db=db, collection_id=collection_id)


