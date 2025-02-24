from sqlalchemy import Column, ForeignKey, Integer, String, Boolean, LargeBinary, UniqueConstraint
from sqlalchemy.orm import relationship, mapped_column, Mapped
from typing import List, Optional
from sqlalchemy.sql import expression
from app.db.session import Base


class User(Base):
    __tablename__ = "users"
    username: Mapped[str] = mapped_column(String, unique=True, index=False, nullable=False)
    email: Mapped[str] = mapped_column(String, unique=True, index=False, nullable=True)
    hashed_password = Column(String)

    words: Mapped[List['Word']] = relationship("Word", back_populates="owner")
    tests: Mapped[List['Test']] = relationship("Test", back_populates="owner")


class Word(Base):
    __tablename__ = "words"
    original: Mapped[str] = mapped_column(String, unique=False, index=True, nullable=False)
    translation: Mapped[str] = mapped_column(String, unique=False, index=True, nullable=False)
    owner_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'), nullable=False)
    hardness_level: Mapped[int] = mapped_column(Integer, index=False, nullable=True, default=1)

    owner = relationship("User", back_populates="words")
    test_results = relationship("TestResult", back_populates="word")
    images = relationship("Image", back_populates="word")
    collections: Mapped[list['Collection']] = relationship(secondary='collections_words', back_populates='words')


    def to_dict(self):
        return {
            "id": self.id,
            "original": self.original,
            "translation": self.translation,
            "owner_id": self.owner_id,
            "hardness_level": self.hardness_level,
        }


class Collection(Base):
    __tablename__ = "collections"
    name: Mapped[str] = mapped_column(String, unique=False, index=True, nullable=False)
    owner_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'), nullable=False)
    is_public = Column(Boolean, server_default=expression.false(), default=False)

    words: Mapped[list['Word']] = relationship(secondary='collections_words', back_populates='collections', lazy="selectin")


class CollectionsWords(Base):
    __tablename__ = "collections_words"

    collection_id: Mapped[int] = mapped_column(Integer, ForeignKey('collections.id'), primary_key=True)
    word_id: Mapped[int] = mapped_column(Integer, ForeignKey('words.id'), primary_key=True)

    __table_args__ = (
        UniqueConstraint('collection_id', 'word_id', name='uq_collection_word'),
    )


class Image(Base):
    __tablename__ = "images"
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, index=True)
    content = Column(LargeBinary)
    word_id = Column(Integer, ForeignKey("words.id"))

    word = relationship("Word", back_populates="images")


class Test(Base):
    __tablename__ = "tests"
    owner_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'), nullable=False)
    accuracy: Mapped[int] = mapped_column(Integer, index=False, nullable=True)

    owner = relationship("User", back_populates="tests")
    test_results: Mapped[List['TestResult']] = relationship("TestResult", back_populates="test")

    def to_dict(self):
        return {
            "id": self.id,
            "owner_id": self.owner_id,
            "accuracy": self.accuracy,
        }


class TestResult(Base):
    __tablename__ = "test_results"
    test_id: Mapped[int] = mapped_column(Integer, ForeignKey('tests.id'), nullable=False)
    word_id: Mapped[int] = mapped_column(Integer, ForeignKey('words.id'), nullable=False)
    is_correct = Column(Boolean, server_default=expression.false(), default=False)

    word = relationship("Word", back_populates="test_results")
    test = relationship("Test", back_populates="test_results")

    def to_dict(self):
        return {
            "id": self.id,
            "test_id": self.test_id,
            "word_id": self.word_id,
            "is_correct": self.is_correct
        }
