from dotenv import load_dotenv
from app.databases import get_db_connection
import logging

# Load environment variables
load_dotenv()

# 1. Retrieve a random question
def get_random_question():

    query = """
       SELECT q.question_id, q.question_text, q.difficulty, t.topic_name, en.exam_name
FROM questions q
INNER JOIN topics t ON q.topic_id = t.topic_id
INNER JOIN exams e ON t.exam_id = e.exam_id
INNER JOIN exam_names en ON e.exam_name_id = en.exam_name_id
ORDER BY RAND()
LIMIT 1;

    """
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(query)
    result = cursor.fetchone()

    return result

# 2. Retrieve random questions (10 to 15) from the same topic
def get_random_questions_by_topic(topic_id, limit_start=1, limit_end=15):
    query = """
        SELECT q.question_id, q.question_text, q.difficulty, 
       t.topic_name, en.exam_name
FROM questions q
JOIN topics t ON q.topic_id = t.topic_id
JOIN exams e ON t.exam_id = e.exam_id
JOIN exam_names en ON e.exam_name_id = en.exam_name_id
WHERE q.topic_id = %s
ORDER BY RAND()
LIMIT %s, %s;

    """
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(query, (topic_id, limit_start, limit_end))
    result = cursor.fetchall()
    conn.close()
    return result

# 3. Retrieve random questions (10 to 15) of random topics for a particular exam
def get_random_questions_for_exam(exam_id, limit_start=10, limit_end=15):
    query = """
       SELECT 
    q.question_id, 
    q.question_text, 
    q.difficulty, 
    t.topic_name, 
    en.exam_name
FROM questions q
INNER JOIN topics t ON q.topic_id = t.topic_id
INNER JOIN exams e ON t.exam_id = e.exam_id
INNER JOIN exam_names en ON e.exam_name_id = en.exam_name_id
WHERE e.exam_id = %s
ORDER BY RAND()
LIMIT %s OFFSET %s;

    """
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(query, (exam_id, limit_start, limit_end))
    result = cursor.fetchall()
    conn.close()
    return result

# 4. Retrieve all topics for a particular exam
def get_topics_for_exam(exam_id):
    query = """
        SELECT 
    t.topic_id, 
    t.topic_name, 
    en.exam_name
FROM topics t
INNER JOIN exams e ON t.exam_id = e.exam_id
INNER JOIN exam_names en ON e.exam_name_id = en.exam_name_id
WHERE e.exam_id = %s;

    """
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(query, (exam_id,))
    result = cursor.fetchall()
    conn.close()
    return result

# 5. Admin - Add a new question
def add_question(topic_id, question_text, difficulty):
    query = "INSERT INTO questions (topic_id, question_text, difficulty) VALUES (%s, %s, %s); :"
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(query, (topic_id, question_text, difficulty))
    conn.commit()
    conn.close()

# 6. Admin - Remove a question
def remove_question(question_id):
    query = "DELETE FROM questions WHERE question_id = %s;"
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(query, (question_id,))
    conn.commit()
    conn.close()

# 7. Admin - Update a question
def update_question(question_id, question_text, difficulty):
    query = "UPDATE questions SET question_text = %s, difficulty = %s WHERE question_id = %s;"
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(query, (question_text, difficulty, question_id))
    conn.commit()
    conn.close()


# 8. Retrieve all users (students and admins) and their quiz scores, even if they have not attempted any quizzes
def get_all_users_and_scores():
    query = """
    SELECT users.name, quizzes.score
    FROM users
    LEFT JOIN quizzes ON users.user_id = quizzes.user_id;
    """
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)  # To get results as a dictionary
    cursor.execute(query)
    result = cursor.fetchall()
    conn.close()
    return result


def calculate_score(user_responses):
    score = 0
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    for response in user_responses:
        query = "SELECT correct_option FROM questions WHERE question_id = %s;"
        cursor.execute(query, (response.question_id,))
        correct_answer = cursor.fetchone()

        if correct_answer and correct_answer['correct_option'] == response.selected_option:
            score += 1  # Assuming each correct answer gives 1 point

    conn.close()
    return score


def save_quiz_responses(quiz_id, user_responses, score):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Insert responses into `quiz_responses` table
    for response in user_responses:
        query = "INSERT INTO quiz_responses (quiz_id, question_id, selected_option) VALUES (%s, %s, %s);"
        cursor.execute(query, (quiz_id, response.question_id, response.selected_option))

    # Update the final score in `quizzes` table
    query = "UPDATE quizzes SET score = %s WHERE quiz_id = %s;"
    cursor.execute(query, (score, quiz_id))

    conn.commit()
    conn.close()

from app.databases import get_db_connection

def save_quiz_start(quiz_id: str, user_id: int, topic_id: int):
    """
    Saves quiz start info in the database.

    Args:
        quiz_id (str): Unique identifier for the quiz.
        user_id (int): ID of the user taking the quiz.
        topic_id (int): ID of the quiz topic.
    """
    query = "INSERT INTO quizzes (quiz_id, user_id, topic_id, score) VALUES (%s, %s, %s, %s);"

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(query, (quiz_id, user_id, topic_id, 0))  # Score is initially 0
        conn.commit()
    except Exception as e:
        print(f"Error saving quiz start: {e}")
    finally:
        cursor.close()
        conn.close()

