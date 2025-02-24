from typing import List

from fastapi import HTTPException
from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.db.models import User, Word, TestResult, Test, Image, Collection
from app.schemas.schemas import RequestUserCreate, TestResultCreate, WordBase
from sqlalchemy.future import select
from sqlalchemy import update
from sqlalchemy import desc


async def create_user_word(db: AsyncSession, word: WordBase, user_id: int):
    db_word = Word(**word.model_dump(), owner_id=user_id)
    db.add(db_word)
    await db.commit()
    await db.refresh(db_word)
    return db_word


async def db_get_words_by_user(db: AsyncSession, user_id: int = None):
    query = select(Word)

    if user_id is not None:
        query = query.where(Word.owner_id == user_id).order_by(desc(Word.created_at))

    result = await db.execute(query)
    return result.scalars().all()


async def db_create_test(db: AsyncSession, owner_id: int):
    db_test = Test(owner_id=owner_id)
    db.add(db_test)
    await db.commit()
    await db.refresh(db_test)
    return db_test


async def db_create_test_result(db: AsyncSession, test_id: int, words: List[Word]):
    arr = []
    for i in words:
        db_test_result = TestResult(test_id=test_id, word_id=i.id, is_correct=False)
        db.add(db_test_result)

        await db.commit()
        await db.refresh(db_test_result)
        arr.append(db_test_result)

    return arr


async def db_get_test(db: AsyncSession, test_id: int):
    query = select(Test).where(Test.id == test_id)
    result = await db.execute(query)
    return result.scalars().all()


async def db_get_all_test(db: AsyncSession, user_id: int):
    query = select(Test).where(Test.owner_id == user_id).order_by(desc(Test.created_at))  # сортировка по возрастанию
    result = await db.execute(query)
    return result.scalars().all()


async def db_get_test_results(db: AsyncSession, test_id: int):
    query = select(TestResult).options(joinedload(TestResult.word)).where(TestResult.test_id == test_id)
    result = await db.execute(query)
    return result.scalars().all()


async def db_get_random_words(db: AsyncSession, user_id: int = None, limit: int = 1):
    query = select(Word).order_by(func.random()).limit(limit)

    if user_id is not None:
        query = query.where(Word.owner_id == user_id)

    result = await db.execute(query)
    return result.scalars().all()


async def db_update_test_result(db: AsyncSession, test_id: int, word_ids: List[int]):
    query = (
        update(TestResult)
        .where(TestResult.test_id == test_id)
        .where(TestResult.word_id.in_(word_ids))
        .values(is_correct=True)
    )

    await db.execute(query)
    await db.commit()


async def db_update_test(db: AsyncSession, test_id: int, accuracy: int):
    query = (
        update(Test)
        .where(Test.id == test_id)
        .values(accuracy=accuracy)
    )

    await db.execute(query)
    await db.commit()


async def db_upload_image_for_word(
        db: AsyncSession,
        filename: str,
        content: bytes,
        word_id: int
) -> Image:

    db_image = Image(filename=filename, content=content, word_id=word_id)

    db.add(db_image)
    await db.commit()
    await db.refresh(db_image)

    return db_image


async def db_get_image_by_word_id(
    db: AsyncSession,
    word_id: int
) -> Image:
    query = select(Image).where(Image.word_id == word_id).limit(1)
    result = await db.execute(query)
    db_image = result.scalars().first()
    if db_image is None:
        raise HTTPException(status_code=404, detail=f"Image for word_id {word_id} not found")
    return db_image


async def db_create_collection(db: AsyncSession, name, words_ids, is_public, user_id):

    # existing_collection = await db.execute(select(Collection).where(Collection.name == name))
    # if existing_collection.scalars().first():
    #     raise HTTPException(status_code=400, detail="Collection with this name already exists")

    db_collection = Collection(name=name, is_public=is_public, owner_id=user_id)
    db.add(db_collection)
    await db.commit()
    await db.refresh(db_collection)

    stmt = select(Word).where(Word.id.in_(words_ids))
    result = await db.execute(stmt)
    words = result.scalars().all()

    # Проверяем, что все слова найдены
    if len(words) != len(words_ids):
        raise HTTPException(status_code=404, detail="One or more words not found")

    for word in words:
        # word.collections.append(db_collection)
        db_collection.words.append(word)

    # Сохраняем изменения в базе данных
    await db.commit()
    await db.refresh(db_collection)
    return db_collection


async def db_get_one_collection(db: AsyncSession, collection_id: int = None):
    query = select(Collection).where(Collection.id == collection_id)
    result = await db.execute(query)
    return result.scalars().first()


async def db_get_all_collections(db: AsyncSession, owner_id: int = None):
    if not owner_id:
        query = select(Collection).where(Collection.is_public == True).order_by(desc(Collection.created_at))
    else:
        query = select(Collection).where(Collection.owner_id == owner_id).order_by(desc(Collection.created_at))
    result = await db.execute(query)
    return result.scalars().all()