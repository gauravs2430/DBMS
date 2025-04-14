from pydantic import BaseModel , EmailStr 
from typing import List, Optional

from pydantic import BaseModel

class QuizResponse(BaseModel):
    question_id: int
    selected_option: str  # Assuming the user selects an option as a string


class User(BaseModel):
    name: str
    friend: 'User' 
 # Forward reference using string annotation

# Schema for a single question
class QuestionBase(BaseModel):
    question_id: int
    question_text: str
    difficulty: str
    topic_name: str
    exam_name: str


class QuestionCreate(BaseModel):
    topic_id: int
    question_text: str
    difficulty: str


# Schema for a list of questions
class QuestionListResponse(BaseModel):
    questions: List[QuestionBase]


# Schema for a topic in an exam
class TopicBase(BaseModel):
    topic_id: int
    topic_name: str
    exam_name: str


# Schema for a list of topics for a particular exam
class TopicListResponse(BaseModel):
    topics: List[TopicBase]


# Schema for a user and their quiz score
class UserScore(BaseModel):
    name: str
    score: Optional[float]  # Users may not have attempted any quizzes, so the score can be None


# Schema for a list of all users and their quiz scores
class UserScoreListResponse(BaseModel):
    users_scores: List[UserScore]


# Schema for response when adding/updating/deleting a question
class QuestionResponse(BaseModel):
    message: str
    question_id: Optional[int] = None


# Example response for getting random questions (can be used in API endpoints)
class RandomQuestionResponse(BaseModel):
    question: QuestionBase


# Schema for retrieving random questions from a particular topic
class RandomQuestionListResponse(BaseModel):
    questions: List[QuestionBase]

class RegisterUserRequest(BaseModel):
    username: str
    password: str  # Ideally hashed before storing
    email: EmailStr
    role: str  # 'student' or 'admin'

class RegisterUserResponse(BaseModel):
    message: str
    user_id: Optional[int] = None

class LoginRequest(BaseModel):
    username: str
    password: str