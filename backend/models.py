from pydantic import BaseModel
from typing import List
from datetime import datetime

class TestCase(BaseModel):
    input: str
    expectedOutput: str

class TestCaseResult(TestCase):
    actualOutput: str

class Question(BaseModel):
    name: str
    text: str
    testCases: List[TestCase]
    hint: str

class Feedback(BaseModel):
    isCorrect: bool
    feedback: str
    strengths: List[str]
    weaknesses: List[str]

class QuestionParams(BaseModel):
    difficulty: str
    topics: List[str]

class SolvedQuestion(BaseModel):
    question: Question
    userCode: str
    feedback: Feedback
    testResults: List[TestCaseResult]

class SessionInfo(BaseModel):
    user_id: str
    exp: datetime

class RunTestsRequest(BaseModel):
    code: str
    question: Question

class SubmitRequest(BaseModel):
    code: str
    question: Question
    test_results: List[TestCaseResult]

class RunTestsResponse(BaseModel):
    results: List[TestCaseResult]