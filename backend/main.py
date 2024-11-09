from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.chains import LLMChain
from langchain.output_parsers import PydanticOutputParser
import uuid
from fastapi import FastAPI, HTTPException, Depends, Header, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional
import random
from google.oauth2 import id_token
from google.auth.transport import requests
from google.auth import exceptions as google_auth_exceptions
from models import TestCase, Question, Feedback, QuestionParams, SolvedQuestion, RunTestsRequest, SubmitRequest, TestCaseResult, RunTestsResponse

import os
import subprocess
from dotenv import load_dotenv
from datetime import datetime, timedelta
from jose import JWTError, jwt
from fastapi.responses import JSONResponse 
from prompts import QUESTION_GENERATION_PROMPT_TEMPLATES, FEEDBACK_PROMPT_TEMPLATES

from database.models import DBUser, DBQuestion, DBUserSolvedQuestion
from database.config import get_db, init_db
from sqlalchemy.orm import Session
from enum import Enum

# Load environment variables from .env file
load_dotenv()

# Get OpenAI API key from environment variables
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY environment variable is not set")

# Add these constants
JWT_SECRET = os.getenv("JWT_SECRET")  # Store this in .env
JWT_ALGORITHM = "HS256"
SESSION_DURATION = timedelta(days=7)
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 days in minutes

# Define allowed origins
ALLOWED_ORIGINS = [
    "http://localhost",
    "http://localhost:3000",
    "http://localhost:3001",
    "http://llm-bots.bits-pilani.ac.in:3000",
    "http://llm-bots.bits-pilani.ac.in:3001",
    "http://llm-bots.bits-pilani.ac.in",
    "172.20.17.71",
    "172.20.17.71:3000",
    "172.20.17.71:3001",
    # Add more origins as needed
]

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mock database
questions_db = []
solved_questions_db = []

# Get Google Client ID from environment variables
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
if not GOOGLE_CLIENT_ID:
    raise ValueError("GOOGLE_CLIENT_ID environment variable is not set")

class TokenRequest(BaseModel):
    token: str

def verify_token(token: str):
    try:
        # Print token for debugging
        print(f"Verifying Google token: {token[:20]}...")
        
        # Request object for Google auth
        request = requests.Request()

        # Verify the token with Google
        idinfo = id_token.verify_oauth2_token(
            token,
            request,
            GOOGLE_CLIENT_ID
        )

        # Verify issuer
        if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
            raise ValueError('Wrong issuer.')
        
        # Verify audience
        if idinfo['aud'] != GOOGLE_CLIENT_ID:
            raise ValueError('Wrong audience.')

        # Print verification result for debugging
        print(f"Google token verification successful: {idinfo}")
        
        return idinfo

    except (ValueError, google_auth_exceptions.GoogleAuthError) as e:
        print(f"Google token verification failed: {str(e)}")
        raise HTTPException(
            status_code=401,
            detail=f"Invalid Google token: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"}
        )

# Add this function to create session tokens
def create_session_token(user_info: dict) -> str:
    to_encode = {
        "sub": user_info["sub"],
        "email": user_info["email"],
        "exp": datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
        "iat": datetime.utcnow(),
        "nbf": datetime.utcnow(),  # not valid before
        "jti": str(uuid.uuid4()),  # unique identifier for the token
        "type": "access"
    }
    return jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)

@app.post("/api/login")
async def login(token_request: TokenRequest, db: Session = Depends(get_db)):
    try:
        print(f"Received login request with Google token: {token_request.token[:20]}...")
        
        # Verify Google token
        user_info = verify_token(token_request.token)
        
        # Check if user exists, if not create new user
        user = db.query(DBUser).filter(DBUser.google_id == user_info["sub"]).first()
        if not user:
            # Create new user
            user = DBUser(
                google_id=user_info["sub"],
                email=user_info["email"],
                name=user_info.get("name", ""),
                picture=user_info.get("picture", "")
            )
            db.add(user)
            db.commit()
            db.refresh(user)
        
        # Create session token
        session_token = create_session_token({
            "sub": user_info["sub"],
            "email": user_info["email"]
        })
        
        print(f"Created session token: {session_token[:20]}...")
        
        return {
            "session_token": session_token,
            "token_type": "bearer",
            "expires_in": SESSION_DURATION.total_seconds()
        }
        
    except Exception as e:
        print(f"Login error: {str(e)}")
        raise HTTPException(status_code=401, detail=str(e))

# Update token verification
def verify_session_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        if datetime.fromtimestamp(payload["exp"]) < datetime.utcnow():
            raise HTTPException(
                status_code=401,
                detail="Token has expired",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return payload
    except JWTError as e:
        print(f"JWT Error: {str(e)}")  # Add this for debugging
        raise HTTPException(
            status_code=401,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

# Update the token verification middleware
async def get_token_from_header(authorization: Optional[str] = Header(None)) -> dict:
    if not authorization:
        raise HTTPException(
            status_code=401, 
            detail="Authorization header missing",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    try:
        scheme, token = authorization.split()
        if scheme.lower() != 'bearer':
            raise HTTPException(
                status_code=401,
                detail="Invalid authentication scheme",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return verify_session_token(token)
    except ValueError:
        raise HTTPException(
            status_code=401,
            detail="Invalid authorization header format",
            headers={"WWW-Authenticate": "Bearer"},
        )

# Initialize database tables
init_db()

# Update question generation endpoint to store questions
@app.post("/api/generate_question")
async def generate_question(
    params: QuestionParams,
    token_payload: dict = Depends(get_token_from_header),
    db: Session = Depends(get_db)
):
    try:
        print(f"Received params: {params}")
        print(f"Token payload: {token_payload}")
        
        llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7, store=True, cache=False)
        output_parser = PydanticOutputParser(pydantic_object=Question)

        prompt = ChatPromptTemplate.from_messages([
            ("user", QUESTION_GENERATION_PROMPT_TEMPLATES[params.programming_language])
        ])

        chain = prompt | llm | output_parser

        # Get current user
        user = db.query(DBUser).filter(DBUser.google_id == token_payload["sub"]).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Fetch questions already solved by this user
        solved_questions = (
            db.query(DBQuestion)
            .join(DBUserSolvedQuestion)
            .filter(DBUserSolvedQuestion.user_id == user.id)
            .all()
        )
        
        # Generate new question
        question = chain.invoke({
            "difficulty": params.difficulty,
            "topics": ", ".join(params.topics),
            "avoid_questions": "\n".join([f"- {q.name}" for q in solved_questions]),
            "format_instructions": output_parser.get_format_instructions()
        })
        
        # Strip whitespace from expected outputs
        for test_case in question.testCases:
            test_case.expectedOutput = test_case.expectedOutput.strip()
        
        # Store question in database
        db_question = DBQuestion(
            name=question.name,
            text=question.text,
            hint=question.hint,
            difficulty=params.difficulty,
            topics=params.topics,
            test_cases=[tc.dict() for tc in question.testCases],
            programming_language=params.programming_language
        )
        db.add(db_question)
        db.commit()
        db.refresh(db_question)
        
        # Create initial test results with empty actual outputs
        initial_test_results = [
            {
                "input": tc.input,
                "expectedOutput": tc.expectedOutput,
                "actualOutput": ""  # Empty actual output initially
            }
            for tc in question.testCases
        ]

        # Create the solved question record
        solved_question = DBUserSolvedQuestion(
            user_id=user.id,
            question_id=db_question.id,
            user_code="",  # No code submitted yet
            test_results=initial_test_results,  # Initialize with all test cases
            is_correct=False,  # Not solved yet
            feedback={  # Initial feedback
                "isCorrect": False,
                "feedback": "Question not attempted yet",
                "strengths": [],
                "weaknesses": ["Not attempted"],
                "topics": params.topics  # Include topics in feedback
            }
        )
        
        db.add(solved_question)
        db.commit()
        
        return question
        
    except Exception as e:
        print(f"Error generating question: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

class ProgrammingLanguage(str, Enum):
    OCAML = "ocaml"
    JAVA = "java"
    C = "c"

def execute_code(language: ProgrammingLanguage, code: str, input_args: str) -> subprocess.CompletedProcess:
    try:
        if language == ProgrammingLanguage.OCAML:
            with open('main.ml', 'w') as f:
                f.write(code)
            return subprocess.run(
                input_args,
                shell=True,
                capture_output=True,
                text=True,
                timeout=5
            )
        elif language == ProgrammingLanguage.JAVA:
            with open('Main.java', 'w') as f:
                f.write(code)
            # Compile Java code
            subprocess.run(['javac', 'Main.java'], check=True, capture_output=True)
            # Run Java code
            return subprocess.run(
                ['java', 'Main'] + input_args.split()[1:],
                capture_output=True,
                text=True,
                timeout=5
            )
        elif language == ProgrammingLanguage.C:
            with open('main.c', 'w') as f:
                f.write(code)
            # Compile C code
            subprocess.run(['gcc', 'main.c', '-o', 'program'], check=True, capture_output=True)
            # Run compiled program
            return subprocess.run(
                ['./program'] + input_args.split()[1:],
                capture_output=True,
                text=True,
                timeout=5
            )
    finally:
        # Cleanup files
        cleanup_files(language)

def cleanup_files(language: ProgrammingLanguage):
    if language == ProgrammingLanguage.OCAML:
        if os.path.exists('main.ml'): os.remove('main.ml')
    elif language == ProgrammingLanguage.JAVA:
        for file in ['Main.java', 'Main.class']:
            if os.path.exists(file): os.remove(file)
    elif language == ProgrammingLanguage.C:
        for file in ['main.c', 'program']:
            if os.path.exists(file): os.remove(file)

@app.post("/api/run_tests", response_model=RunTestsResponse)
async def run_tests(
    request: RunTestsRequest,
    token_payload: dict = Depends(get_token_from_header)
):
    results = []
    for test_case in request.question.testCases:
        try:
            process = execute_code(
                ProgrammingLanguage(request.programming_language),
                request.code,
                test_case.input
            )
            
            actual_output = process.stdout.strip()
            error_output = process.stderr.strip()
            
            if error_output:
                actual_output = f"{actual_output}\nError: {error_output}"

            results.append(TestCaseResult(
                input=test_case.input,
                expectedOutput=test_case.expectedOutput,
                actualOutput=str(actual_output)
            ))
            
        except subprocess.TimeoutExpired:
            results.append(TestCaseResult(
                input=test_case.input,
                expectedOutput=test_case.expectedOutput,
                actualOutput="Error: Execution timed out"
            ))
        except Exception as e:
            results.append(TestCaseResult(
                input=test_case.input,
                expectedOutput=test_case.expectedOutput,
                actualOutput=f"Error: {str(e)}"
            ))
        finally:
            if os.path.exists('main.ml'):
                os.remove('main.ml')
                
    return RunTestsResponse(results=results)

def generate_feedback(request: SubmitRequest, is_correct: bool):
    # Initialize ChatGPT for feedback generation
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7, store=True, cache=False)
    output_parser = PydanticOutputParser(pydantic_object=Feedback)

    # Create prompt template for code feedback
    prompt = ChatPromptTemplate.from_messages([
        ("user", FEEDBACK_PROMPT_TEMPLATES[request.programming_language])
    ])

    # Create chain and generate feedback
    chain = prompt | llm | output_parser

    feedback = chain.invoke({
        "code": request.code,
        "question": request.question.text,
        "test_results": [result.actualOutput for result in request.test_results],
        "is_correct": is_correct,
        "format_instructions": output_parser.get_format_instructions()
    })
    return feedback

@app.post("/api/submit", response_model=Feedback)
async def submit(
    request: SubmitRequest,
    token_payload: dict = Depends(get_token_from_header),
    db: Session = Depends(get_db)
):
    user = db.query(DBUser).filter(DBUser.google_id == token_payload["sub"]).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Get question from database
    question = db.query(DBQuestion).filter(DBQuestion.name == request.question.name).first()
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")

    # Find the existing solved question record
    solved_question = (
        db.query(DBUserSolvedQuestion)
        .filter(
            DBUserSolvedQuestion.user_id == user.id,
            DBUserSolvedQuestion.question_id == question.id
        )
        .first()
    )
    
    if not solved_question:
        raise HTTPException(status_code=404, detail="Question attempt not found")

    is_correct = all(
        result.actualOutput == tc.expectedOutput 
        for tc, result in zip(request.question.testCases, request.test_results)
    )
    
    # Generate feedback using existing code
    feedback = generate_feedback(request, is_correct)
    
    # Update the existing record
    solved_question.user_code = request.code
    solved_question.test_results = [tr.dict() for tr in request.test_results]
    solved_question.is_correct = is_correct
    solved_question.feedback = feedback.dict()
    solved_question.solved_at = datetime.utcnow()  # Update the timestamp
    
    db.commit()
    
    return feedback

# Update get_solved_questions endpoint
@app.get("/api/solved_questions")
async def get_solved_questions(
    token_payload: dict = Depends(get_token_from_header),
    db: Session = Depends(get_db)
):
    user = db.query(DBUser).filter(DBUser.google_id == token_payload["sub"]).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    solved_questions = (
        db.query(DBUserSolvedQuestion)
        .join(DBQuestion)
        .filter(DBUserSolvedQuestion.user_id == user.id)
        .order_by(DBUserSolvedQuestion.solved_at.desc())
        .all()
    )
    
    return [
        SolvedQuestion(
            question=Question(
                name=sq.question.name,
                text=sq.question.text,
                testCases=[TestCase(**tc) for tc in sq.question.test_cases],
                hint=sq.question.hint
            ),
            userCode=sq.user_code,
            feedback=Feedback(**sq.feedback),
            testResults=[TestCaseResult(**tr) for tr in sq.test_results]
        )
        for sq in solved_questions
    ]

@app.post("/api/refresh")
async def refresh_token(current_token: dict = Depends(get_token_from_header)):
    try:
        # Create new token with updated expiration
        new_token = create_session_token({
            "sub": current_token["sub"],
            "email": current_token["email"]
        })
        return {
            "access_token": new_token,
            "token_type": "bearer",
            "expires_in": SESSION_DURATION.total_seconds()
        }
    except JWTError:
        raise HTTPException(
            status_code=401,
            detail="Could not refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    print(f"HTTP Exception: {exc.detail}")  # Debug log
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
        headers=exc.headers,
    )

@app.middleware("http")
async def log_requests(request: Request, call_next):
    print(f"\nRequest: {request.method} {request.url}")
    try:
        response = await call_next(request)
        print(f"Response Status: {response.status_code}")
        return response
    except Exception as e:
        print(f"Request Error: {str(e)}")
        raise

# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=8000)