from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel


class RequestUserCreate(BaseModel):
    username: str
    password: str
    email: str


class ResponseUser(BaseModel):
    id: int
    username: str
    email: str


class WordBase(BaseModel):
    original: str
    translation: str


class WordResponse(WordBase):
    id: int
    owner_id: int
    image_url: Optional[str] = None
    created_at: datetime


class TestCreate(BaseModel):
    hardness_level: int = 1
    count_words: Optional[int] = 10
    useMyDict: bool


class TestCreateFromCollections(BaseModel):
    collections_id: int


class TestResultBase(BaseModel):
    word_id: int
    is_correct: bool


class TestResultCreate(TestResultBase):
    pass


class TestResultResponse(TestResultBase):
    id: int
    user_id: int
    created_at: datetime


class TestResultsCreate(BaseModel):
    results: List[TestResultCreate]


class AnswerRequest(BaseModel):
    word_id: int
    original: str
    user_translation: str


class CheckResultsRequest(BaseModel):
    answer: List[AnswerRequest]


class CollectionRequest(BaseModel):
    name: str
    is_public: bool = False
    words_ids: list[int]
