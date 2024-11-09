from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, JSON, DateTime, ARRAY
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime

Base = declarative_base()

class DBUser(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    google_id = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    name = Column(String)
    picture = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    solved_questions = relationship("DBUserSolvedQuestion", back_populates="user")

class DBQuestion(Base):
    __tablename__ = "questions"
    
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    text = Column(String, nullable=False)
    hint = Column(String)
    difficulty = Column(String, nullable=False)
    topics = Column(ARRAY(String), nullable=False)
    test_cases = Column(JSON, nullable=False)  # Store test cases as JSON
    programming_language = Column(String, nullable=False)  # Add this line
    created_at = Column(DateTime, default=datetime.utcnow)
    
    solved_by = relationship("DBUserSolvedQuestion", back_populates="question")

class DBUserSolvedQuestion(Base):
    __tablename__ = "user_solved_questions"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False)
    user_code = Column(String, nullable=False)
    test_results = Column(JSON, nullable=False)  # Store test results as JSON
    is_correct = Column(Boolean, nullable=False)
    feedback = Column(JSON, nullable=False)  # Store feedback as JSON
    solved_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("DBUser", back_populates="solved_questions")
    question = relationship("DBQuestion", back_populates="solved_by") 