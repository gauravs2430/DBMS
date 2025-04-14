from typing import List
from uuid import uuid4 
from fastapi import FastAPI, HTTPException , Depends 
from fastapi.middleware.cors import CORSMiddleware
from app.queries import (
    get_random_question,
    get_random_questions_by_topic,
    get_random_questions_for_exam,
    get_topics_for_exam,
    add_question,
    remove_question,
    update_question,
    get_all_users_and_scores , 
    calculate_score , 
    save_quiz_responses , 
    save_quiz_start,
    register_user , 
    login_user 
)
from app.schemas import (
    RandomQuestionResponse,
    RandomQuestionListResponse,
    TopicListResponse,
    UserScoreListResponse,
    QuestionCreate,
    QuestionResponse, QuizResponse , 
    RegisterUserRequest ,
    RegisterUserResponse ,
    LoginRequest
)

app = FastAPI()

Origins = ["http://localhost:8080"]


app.add_middleware(
    CORSMiddleware,
    allow_origins=Origins,  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "FastAPI is running!"}


# 1. Endpoint to get a random question
@app.get("/random-question", response_model=RandomQuestionResponse)
async def random_question():
    question = get_random_question()
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    return RandomQuestionResponse(question=question)

# 2. Endpoint to get random questions by topic
@app.get("/random-questions-by-topic/{topic_id}", response_model=RandomQuestionListResponse)
async def random_questions_by_topic(topic_id: int, limit_start: int = 10, limit_end: int = 15):
    questions = get_random_questions_by_topic(topic_id, limit_start, limit_end)
    return RandomQuestionListResponse(questions=questions)

# 3. Endpoint to get random questions for a particular exam
@app.get("/random-questions-for-exam/{exam_id}", response_model=RandomQuestionListResponse)
async def random_questions_for_exam(exam_id: int, limit_start: int = 10, limit_end: int = 15):
    questions = get_random_questions_for_exam(exam_id, limit_start, limit_end)
    return RandomQuestionListResponse(questions=questions)

# 4. Endpoint to get all topics for a particular exam
@app.get("/topics-for-exam/{exam_id}", response_model=TopicListResponse)
async def topics_for_exam(exam_id: int):
    topics = get_topics_for_exam(exam_id)
    return TopicListResponse(topics=topics)

# 5. Endpoint to add a new question (Admin only)
@app.post("/add-question", response_model=QuestionResponse)
async def add_new_question(question: QuestionCreate):
    try:
        add_question(question.topic_id, question.question_text, question.difficulty)
        return QuestionResponse(message="Question added successfully")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# 6. Endpoint to remove a question (Admin only)
@app.delete("/remove-question/{question_id}", response_model=QuestionResponse)
async def remove_question_endpoint(question_id: int):
    try:
        remove_question(question_id)
        return QuestionResponse(message="Question removed successfully")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# 7. Endpoint to update a question (Admin only)
@app.put("/update-question/{question_id}", response_model=QuestionResponse)
async def update_question_endpoint(question_id: int, question: QuestionCreate):
    try:
        update_question(question_id, question.question_text, question.difficulty)
        return QuestionResponse(message="Question updated successfully")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# 8. Endpoint to get all users and their quiz scores
@app.get("/users-and-scores", response_model=UserScoreListResponse)
async def users_and_scores():
    users_scores = get_all_users_and_scores()
    return UserScoreListResponse(users_scores=users_scores)


@app.post("/start-quiz/{topic_id}")
async def start_quiz(topic_id: int, user_id: int):
    # Generate a unique quiz_id
    quiz_id = str(uuid4())  # Unique ID for the quiz (UUID string)

    # Fetch random questions based on the topic
    questions = get_random_questions_by_topic(topic_id)

    save_quiz_start(quiz_id, user_id, topic_id )
    return {"quiz_id": quiz_id, "questions": questions}



@app.post("/submit-quiz/{quiz_id}")
async def submit_quiz(quiz_id: str, user_responses: List[QuizResponse]):
    # Calculate score based on correct answers
    score = calculate_score(user_responses)

    # Save responses and update score
    save_quiz_responses(quiz_id, user_responses, score)

    return {"message": "Quiz submitted successfully", "score": score}


@app.post("/register", response_model=RegisterUserResponse)
def register_user_route(payload: RegisterUserRequest):
    result = register_user(payload.username, payload.password, payload.email, payload.role)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return result


@app.post("/login")
def login(request: LoginRequest):
    return login_user(
        username=request.username,
        password=request.password
    )