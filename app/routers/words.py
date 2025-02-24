import os
import shutil
from typing import Annotated
from fastapi import Depends, FastAPI, APIRouter, HTTPException, File, UploadFile
from sqlalchemy import func, select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from app.db.models import Word
from app.schemas.schemas import ResponseUser, WordResponse, WordBase
from app.db.session import get_db
from app.routers.auth import get_current_user
from app.db.crud import *
from fastapi.responses import StreamingResponse
from PIL import Image
from io import BytesIO
from loguru import logger

logger.add("info.log")

router = APIRouter(prefix='', tags=['words'])


@router.post("/word", status_code=status.HTTP_201_CREATED)
async def create_word(
        word: WordBase,
        db: AsyncSession = Depends(get_db),
        current_user: ResponseUser = Depends(get_current_user)
):
    return await create_user_word(db=db, word=word, user_id=current_user['id'])


@router.get("/users/words/", response_model=list[WordResponse])
async def read_words(user_id: int = None, db: AsyncSession = Depends(get_db)):
    words = await db_get_words_by_user(db, user_id=user_id)
    return [
        {
            "id": word.id,
            "original": word.original,
            "translation": word.translation,
            "owner_id": word.owner_id,
            "created_at": word.created_at
        }
        for word in words
    ]


def resize_image(image_bytes: bytes, max_width: int = 200) -> bytes:
    """
    Изменяет размер изображения до указанной ширины, сохраняя пропорции.

    :param image_bytes: Бинарные данные изображения.
    :param max_width: Максимальная ширина изображения.
    :return: Бинарные данные сжатого изображения.
    """
    # Открываем изображение из бинарных данных
    image = Image.open(BytesIO(image_bytes))

    # Вычисляем новые размеры с сохранением пропорций
    width, height = image.size
    new_height = int((max_width / width) * height)

    # Изменяем размер изображения
    resized_image = image.resize((max_width, new_height), Image.Resampling.LANCZOS)

    # Сохраняем изображение в бинарный формат
    output_buffer = BytesIO()
    resized_image.save(output_buffer, format="JPEG")  # Можно изменить на "PNG" или другой формат
    return output_buffer.getvalue()


@router.post("/upload-image/{word_id}")
async def upload_image(
        word_id: int,  # ID слова, к которому привязывается изображение
        file: UploadFile = File(...),  # Загружаемый файл
        db: AsyncSession = Depends(get_db),  # Сессия базы данных
):
    # Сохраняем файл временно
    file_location = f"temp_{file.filename}"
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Читаем файл
    with open(file_location, "rb") as buffer:
        image_content = buffer.read()

    # Удаляем временный файл
    os.remove(file_location)

    try:
        resized_image_content = resize_image(image_content, max_width=200)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to resize image: {str(e)}")

    # Используем функцию для загрузки изображения
    try:
        db_image = await db_upload_image_for_word(
            db=db,  # Сессия базы данных
            filename=file.filename,  # Имя файла
            content=resized_image_content,  # Содержимое файла
            word_id=word_id  # ID слова
        )
        return {"filename": db_image.filename, "id": db_image.id, "word_id": word_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/word/{word_id}/image")
async def get_image_for_word(
    word_id: int,
    db: AsyncSession = Depends(get_db)
):
    db_image = await db_get_image_by_word_id(db, word_id)
    return StreamingResponse(
        BytesIO(db_image.content),
        media_type=db_image.filename.split('.')[-1],  # Dynamically determine media type
        headers={"Content-Disposition": f"attachment; filename={db_image.filename}"}
    )

