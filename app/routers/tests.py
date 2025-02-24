import json
from datetime import datetime
from typing import Annotated, Optional
from fastapi import Depends, FastAPI, APIRouter, HTTPException
from sqlalchemy import func, select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from starlette import status
from app.db.models import TestResult, Collection
from app.schemas.schemas import ResponseUser, WordResponse, TestResultResponse, TestResultsCreate, TestCreate, \
    CheckResultsRequest, CollectionRequest, TestCreateFromCollections
from app.db.session import get_db, get_db_local
from app.routers.auth import get_current_user
from app.db.crud import *
from loguru import logger

logger.add("info.log")

router = APIRouter(prefix='', tags=['tests'])


@router.post("/test")
async def create_test(create_request: TestCreate,
                      current_user: ResponseUser = Depends(get_current_user),
                      db: AsyncSession = Depends(get_db)):

    test = await db_create_test(owner_id=current_user['id'], db=db)

    if create_request.useMyDict:
        words = await db_get_random_words(db, user_id=current_user['id'], limit=create_request.count_words)
    else:
        words = await db_get_random_words(db, limit=create_request.count_words)

    logger.info(json.dumps(test.to_dict(), ensure_ascii=False))

    for i in words:
        logger.info(json.dumps(i.to_dict(), ensure_ascii=False))

    test_result = await db_create_test_result(db=db, test_id=test.id, words=words)

    return {
        "test": {
            "test_id": test.id,
            "owner_id": test.owner_id,
            "created_at": test.created_at
        },
        "words": words
    }


@router.post("/test_from_collections")
async def create_from_collections(create_request: TestCreateFromCollections,
                      current_user: ResponseUser = Depends(get_current_user),
                      db: AsyncSession = Depends(get_db)):

    collection = await db_get_one_collection(db=db, collection_id=create_request.collections_id)

    test = await db_create_test(owner_id=1, db=db)

    words = []

    for word in collection.words:
        words.append(word)

    # if create_request.useMyDict:
    #     words = await db_get_random_words(db, user_id=current_user['id'], limit=create_request.count_words)
    # else:
    #     words = await db_get_random_words(db, limit=create_request.count_words)

    # logger.info(json.dumps(test.to_dict(), ensure_ascii=False))

    for i in words:
        logger.info(json.dumps(i.to_dict(), ensure_ascii=False))

    test_result = await db_create_test_result(db=db, test_id=test.id, words=words)

    return {
         "test": {
             "test_id": test.id,
             "owner_id": test.owner_id,
             "created_at": test.created_at
         },
         "words": words
    }


@router.get("/test/{test_id}")
async def get_test(test_id: int, db: AsyncSession = Depends(get_db)):
    test = await db_get_test(db=db, test_id=test_id)
    return test


@router.get("/test/{user_id}/all_test")
async def get_all_tests_by_user(user_id: int, db: AsyncSession = Depends(get_db)):
    all_test = await db_get_all_test(db=db, user_id=user_id)
    return all_test


@router.get("/test/{test_id}/results")
async def get_test_results(test_id: int, db: AsyncSession = Depends(get_db)):
    test_results = await db_get_test_results(db=db, test_id=test_id)

    results = []
    for test_result in test_results:
        result_dict = {
            "user_answer": {
                "id": test_result.id,
                "word_id": test_result.word_id,
                "word_original": test_result.word.original,
                "is_correct": test_result.is_correct
            }}
        results.append(result_dict)

    return results




@router.post("/test/{test_id}/check")
async def check_test_results(
        test_id: int,
        request: CheckResultsRequest,
        current_user: ResponseUser = Depends(get_current_user),
        db: AsyncSession = Depends(get_db),
):
    test = await db_get_test(db=db, test_id=test_id)
    if not test:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Test not found!")

    test_results = await db_get_test_results(db=db, test_id=test_id)
    if not test_results:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No test results found!")

    # Проверяем, что слова в ответе соответствуют словам в тесте
    original_word_ids = {result.word_id for result in test_results}
    user_word_ids = {answer.word_id for answer in request.answer}

    if original_word_ids != user_word_ids:
        raise HTTPException(
            status_code=status.HTTP_412_PRECONDITION_FAILED,
            detail="Words in the answer do not match the words in the test!",
        )

    # Проверяем правильность ответов
    correct_answer_word_ids = set()
    for word_in_test in test_results:
        for word_in_answer in request.answer:
            if (
                    word_in_test.word_id == word_in_answer.word_id
                    and word_in_test.word.original == word_in_answer.original
                    and word_in_test.word.translation == word_in_answer.user_translation
            ):
                correct_answer_word_ids.add(word_in_test.word_id)

    # Обновляем результаты теста в базе данных
    await db_update_test_result(db=db, test_id=test_id, word_ids=list(correct_answer_word_ids))

    # Рассчитываем точность
    correct_answers_count = len(correct_answer_word_ids)
    total_answers_count = len(request.answer)
    accuracy = round((correct_answers_count / total_answers_count) * 100, 0) if total_answers_count > 0 else 0

    # Обновляем тест с новой точностью
    await db_update_test(db=db, test_id=test_id, accuracy=int(accuracy))

    return {"accuracy": accuracy}




