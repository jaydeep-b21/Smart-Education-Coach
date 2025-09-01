from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from google import genai
from google.genai import types
from dotenv import load_dotenv
import os
import json
import uuid
from datetime import datetime

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# In-memory storage (in production, use a proper database)
tutoring_sessions = {}  # session_id: session_data
user_profiles = {}      # user_id: profile_data
exam_results = {}       # exam_id: result_data

# Global counters
request_counter = 0
MAX_REQUESTS = 100

def get_or_create_session(user_id, topic=None):
    """Get existing session or create new one"""
    session_id = str(uuid.uuid4())
    
    if user_id not in user_profiles:
        user_profiles[user_id] = {
            'sessions': [],
            'learning_progress': {},
            'strengths': [],
            'weaknesses': []
        }
    
    session_data = {
        'session_id': session_id,
        'user_id': user_id,
        'topic': topic,
        'conversation_history': [],
        'learning_objectives': [],
        'concepts_covered': [],
        'difficulty_level': 'beginner',
        'created_at': datetime.now().isoformat(),
        'status': 'active'
    }
    
    tutoring_sessions[session_id] = session_data
    user_profiles[user_id]['sessions'].append(session_id)
    
    return session_data

@api_view(['POST'])
def start_tutoring_session(request):
    """Start a new personalized tutoring session"""
    global request_counter
    
    if request_counter >= MAX_REQUESTS:
        return Response({"error": "Request limit exceeded"}, 
                       status=status.HTTP_429_TOO_MANY_REQUESTS)
    
    request_counter += 1
    
    user_id = request.data.get("user_id", "default_user")
    topic = request.data.get("topic", "")
    learning_goals = request.data.get("learning_goals", [])
    difficulty_level = request.data.get("difficulty_level", "beginner")
    
    if not topic:
        return Response({"error": "Topic is required"}, 
                       status=status.HTTP_400_BAD_REQUEST)
    
    session = get_or_create_session(user_id, topic)
    session['learning_objectives'] = learning_goals
    session['difficulty_level'] = difficulty_level
    
    # Generate personalized introduction
    system_instruction = f"""You are an expert tutor specializing in {topic}. 
    Your student wants to learn about {topic} at a {difficulty_level} level.
    Learning goals: {', '.join(learning_goals) if learning_goals else 'General understanding'}
    
    Start by:
    1. Greeting the student warmly
    2. Asking about their current knowledge level
    3. Explaining how you'll structure the learning session
    4. Asking what specific aspect they'd like to start with
    
    Be encouraging, adaptive, and interactive."""
    
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                temperature=0.7
            ),
            contents=f"Start a tutoring session for {topic}"
        )
        
        intro_message = response.text.strip()
        session['conversation_history'].append({
            "role": "assistant", 
            "content": intro_message,
            "timestamp": datetime.now().isoformat()
        })
        
        return Response({
            "session_id": session['session_id'],
            "topic": topic,
            "message": intro_message,
            "learning_objectives": learning_goals,
            "difficulty_level": difficulty_level
        })
        
    except Exception as e:
        return Response({"error": str(e)}, 
                       status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
def tutoring_chat(request):
    """Continue tutoring conversation with adaptive learning"""
    global request_counter
    
    if request_counter >= MAX_REQUESTS:
        return Response({"error": "Request limit exceeded"}, 
                       status=status.HTTP_429_TOO_MANY_REQUESTS)
    
    request_counter += 1
    
    session_id = request.data.get("session_id", "")
    user_message = request.data.get("message", "")
    
    if not session_id or session_id not in tutoring_sessions:
        return Response({"error": "Invalid session ID"}, 
                       status=status.HTTP_400_BAD_REQUEST)
    
    if not user_message:
        return Response({"error": "Message is required"}, 
                       status=status.HTTP_400_BAD_REQUEST)
    
    session = tutoring_sessions[session_id]
    session['conversation_history'].append({
        "role": "user", 
        "content": user_message,
        "timestamp": datetime.now().isoformat()
    })
    
    # Build context for AI
    conversation_context = ""
    for msg in session['conversation_history'][-10:]:  # Last 10 messages
        role = msg["role"].capitalize()
        conversation_context += f"{role}: {msg['content']}\n"
    
    system_instruction = f"""You are tutoring {session['topic']} at {session['difficulty_level']} level.
    Learning objectives: {', '.join(session['learning_objectives'])}
    Concepts already covered: {', '.join(session['concepts_covered'])}
    
    Guidelines:
    - Provide clear, step-by-step explanations
    - Use examples and analogies appropriate for the difficulty level
    - Ask follow-up questions to check understanding
    - Adapt your teaching style based on student responses
    - Identify and note new concepts being taught
    - Be encouraging and patient
    - If student seems confused, simplify and try different approaches
    - If student is ready, suggest moving to more advanced topics
    """
    
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                temperature=0.7
            ),
            contents=conversation_context
        )
        
        assistant_message = response.text.strip()
        session['conversation_history'].append({
            "role": "assistant", 
            "content": assistant_message,
            "timestamp": datetime.now().isoformat()
        })
        
        # Simple concept extraction (in production, use more sophisticated NLP)
        if "concept:" in assistant_message.lower():
            # Extract concepts mentioned in the response
            pass  # Implement concept extraction logic
        
        return Response({
            "session_id": session_id,
            "reply": assistant_message,
            "concepts_covered": session['concepts_covered']
        })
        
    except Exception as e:
        return Response({"error": str(e)}, 
                       status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
def generate_exam(request):
    """Generate MCQ exam based on tutoring session"""
    global request_counter
    
    if request_counter >= MAX_REQUESTS:
        return Response({"error": "Request limit exceeded"}, 
                       status=status.HTTP_429_TOO_MANY_REQUESTS)
    
    request_counter += 1
    
    session_id = request.data.get("session_id", "")
    num_questions = request.data.get("num_questions", 5)
    difficulty = request.data.get("difficulty", "medium")
    
    if not session_id or session_id not in tutoring_sessions:
        return Response({"error": "Invalid session ID"}, 
                       status=status.HTTP_400_BAD_REQUEST)
    
    session = tutoring_sessions[session_id]
    
    # Analyze conversation to extract key concepts
    conversation_summary = ""
    for msg in session['conversation_history']:
        if msg['role'] == 'assistant':
            conversation_summary += msg['content'] + "\n"
    
    exam_prompt = f"""Based on the tutoring session about {session['topic']}, create {num_questions} multiple choice questions at {difficulty} difficulty level.

    Topic: {session['topic']}
    Concepts covered: {', '.join(session['concepts_covered']) if session['concepts_covered'] else 'Extract from conversation'}
    Difficulty level: {session['difficulty_level']}
    
    Return ONLY a valid JSON object in this exact format:
    {{
        "exam_id": "unique_id",
        "topic": "{session['topic']}",
        "difficulty": "{difficulty}",
        "questions": [
            {{
                "question_id": 1,
                "question": "Question text here?",
                "options": ["A) Option 1", "B) Option 2", "C) Option 3", "D) Option 4"],
                "correct_answer": "A",
                "explanation": "Why this answer is correct"
            }}
        ]
    }}
    
    Make questions test understanding, not just memorization. Include clear explanations.
    """
    
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            config=types.GenerateContentConfig(
                system_instruction="You are an expert exam creator. Return only valid JSON.",
                temperature=0.3
            ),
            contents=exam_prompt
        )
        
        exam_json_text = response.text.strip()
        
        # Clean up response to extract JSON
        if "```json" in exam_json_text:
            start = exam_json_text.find("```json") + 7
            end = exam_json_text.rfind("```")
            exam_json_text = exam_json_text[start:end].strip()
        elif "```" in exam_json_text:
            start = exam_json_text.find("```") + 3
            end = exam_json_text.rfind("```")
            exam_json_text = exam_json_text[start:end].strip()
        
        exam_data = json.loads(exam_json_text)
        exam_id = str(uuid.uuid4())
        exam_data['exam_id'] = exam_id
        exam_data['session_id'] = session_id
        exam_data['created_at'] = datetime.now().isoformat()
        
        # Store exam for grading
        exam_results[exam_id] = {
            'exam_data': exam_data,
            'submitted_answers': None,
            'score': None,
            'graded_at': None
        }
        
        # Remove correct answers from response to student
        student_exam = {
            "exam_id": exam_id,
            "topic": exam_data['topic'],
            "difficulty": exam_data['difficulty'],
            "questions": []
        }
        
        for q in exam_data['questions']:
            student_exam['questions'].append({
                "question_id": q['question_id'],
                "question": q['question'],
                "options": q['options']
            })
        
        return Response(student_exam)
        
    except json.JSONDecodeError:
        return Response({"error": "Failed to generate valid exam format"}, 
                       status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    except Exception as e:
        return Response({"error": str(e)}, 
                       status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
def submit_exam(request):
    """Submit exam answers for auto-grading"""
    global request_counter
    
    if request_counter >= MAX_REQUESTS:
        return Response({"error": "Request limit exceeded"}, 
                       status=status.HTTP_429_TOO_MANY_REQUESTS)
    
    request_counter += 1
    
    exam_id = request.data.get("exam_id", "")
    submitted_answers = request.data.get("answers", {})  # {question_id: selected_option}
    
    if not exam_id or exam_id not in exam_results:
        return Response({"error": "Invalid exam ID"}, 
                       status=status.HTTP_400_BAD_REQUEST)
    
    if not submitted_answers:
        return Response({"error": "Answers are required"}, 
                       status=status.HTTP_400_BAD_REQUEST)
    
    exam_result = exam_results[exam_id]
    exam_data = exam_result['exam_data']
    
    # Grade the exam
    correct_count = 0
    total_questions = len(exam_data['questions'])
    detailed_results = []
    
    for question in exam_data['questions']:
        q_id = question['question_id']
        correct_answer = question['correct_answer']
        submitted_answer = submitted_answers.get(str(q_id), "")
        is_correct = submitted_answer == correct_answer
        
        if is_correct:
            correct_count += 1
        
        detailed_results.append({
            "question_id": q_id,
            "question": question['question'],
            "submitted_answer": submitted_answer,
            "correct_answer": correct_answer,
            "is_correct": is_correct,
            "explanation": question['explanation']
        })
    
    score_percentage = (correct_count / total_questions) * 100
    
    # Update exam result
    exam_result.update({
        'submitted_answers': submitted_answers,
        'score': score_percentage,
        'correct_count': correct_count,
        'total_questions': total_questions,
        'detailed_results': detailed_results,
        'graded_at': datetime.now().isoformat()
    })
    
    # Generate personalized feedback
    feedback_prompt = f"""Based on this exam performance, provide constructive feedback:
    
    Topic: {exam_data['topic']}
    Score: {score_percentage:.1f}% ({correct_count}/{total_questions})
    
    Questions and performance:
    {json.dumps(detailed_results, indent=2)}
    
    Provide:
    1. Overall performance assessment
    2. Strengths identified
    3. Areas for improvement
    4. Specific study recommendations
    5. Encouragement and next steps
    
    Keep it constructive and motivating.
    """
    
    try:
        feedback_response = client.models.generate_content(
            model="gemini-2.5-flash",
            config=types.GenerateContentConfig(
                system_instruction="You are an encouraging tutor providing personalized feedback.",
                temperature=0.6
            ),
            contents=feedback_prompt
        )
        
        feedback = feedback_response.text.strip()
        
        return Response({
            "exam_id": exam_id,
            "score": score_percentage,
            "correct_count": correct_count,
            "total_questions": total_questions,
            "grade": get_letter_grade(score_percentage),
            "detailed_results": detailed_results,
            "feedback": feedback,
            "graded_at": exam_result['graded_at']
        })
        
    except Exception as e:
        return Response({
            "exam_id": exam_id,
            "score": score_percentage,
            "correct_count": correct_count,
            "total_questions": total_questions,
            "grade": get_letter_grade(score_percentage),
            "detailed_results": detailed_results,
            "feedback": "Exam graded successfully, but feedback generation failed.",
            "error": str(e)
        })

@api_view(['POST'])
def get_learning_path(request):
    """Get personalized learning path recommendation"""
    global request_counter
    
    if request_counter >= MAX_REQUESTS:
        return Response({"error": "Request limit exceeded"}, 
                       status=status.HTTP_429_TOO_MANY_REQUESTS)
    
    request_counter += 1
    
    user_id = request.data.get("user_id", "default_user")
    subject = request.data.get("subject", "")
    current_level = request.data.get("current_level", "beginner")
    goals = request.data.get("goals", [])
    
    if not subject:
        return Response({"error": "Subject is required"}, 
                       status=status.HTTP_400_BAD_REQUEST)
    
    # Analyze user's past performance
    user_profile = user_profiles.get(user_id, {})
    past_sessions = []
    
    for session_id in user_profile.get('sessions', []):
        if session_id in tutoring_sessions:
            past_sessions.append(tutoring_sessions[session_id])
    
    learning_path_prompt = f"""Create a personalized learning path for:
    
    Subject: {subject}
    Current Level: {current_level}
    Goals: {', '.join(goals) if goals else 'General mastery'}
    Past Performance: {len(past_sessions)} previous sessions
    
    Return a JSON object with this structure:
    {{
        "learning_path": [
            {{
                "module": "Module Name",
                "topics": ["Topic 1", "Topic 2"],
                "estimated_duration": "2-3 hours",
                "difficulty": "beginner/intermediate/advanced",
                "prerequisites": ["Previous knowledge needed"]
            }}
        ],
        "recommended_next_session": "Specific topic to start with",
        "study_tips": ["Tip 1", "Tip 2"]
    }}
    """
    
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            config=types.GenerateContentConfig(
                system_instruction="You are an educational planning expert. Return only valid JSON.",
                temperature=0.4
            ),
            contents=learning_path_prompt
        )
        
        path_text = response.text.strip()
        
        # Clean up JSON response
        if "```json" in path_text:
            start = path_text.find("```json") + 7
            end = path_text.rfind("```")
            path_text = path_text[start:end].strip()
        
        learning_path = json.loads(path_text)
        
        return Response(learning_path)
        
    except Exception as e:
        return Response({"error": str(e)}, 
                       status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def get_session_progress(request, session_id):
    """Get progress for a specific tutoring session"""
    if session_id not in tutoring_sessions:
        return Response({"error": "Session not found"}, 
                       status=status.HTTP_404_NOT_FOUND)
    
    session = tutoring_sessions[session_id]
    
    # Calculate progress metrics
    total_messages = len(session['conversation_history'])
    concepts_learned = len(session['concepts_covered'])
    
    progress_data = {
        "session_id": session_id,
        "topic": session['topic'],
        "status": session['status'],
        "total_messages": total_messages,
        "concepts_covered": session['concepts_covered'],
        "concepts_count": concepts_learned,
        "difficulty_level": session['difficulty_level'],
        "created_at": session['created_at'],
        "learning_objectives": session['learning_objectives']
    }
    
    return Response(progress_data)

@api_view(['GET'])
def get_user_profile(request, user_id):
    """Get user's learning profile and history"""
    if user_id not in user_profiles:
        return Response({"error": "User not found"}, 
                       status=status.HTTP_404_NOT_FOUND)
    
    profile = user_profiles[user_id]
    
    # Get session summaries
    session_summaries = []
    for session_id in profile['sessions']:
        if session_id in tutoring_sessions:
            session = tutoring_sessions[session_id]
            session_summaries.append({
                "session_id": session_id,
                "topic": session['topic'],
                "status": session['status'],
                "created_at": session['created_at'],
                "concepts_count": len(session['concepts_covered'])
            })
    
    # Get exam history
    user_exams = []
    for exam_id, exam_result in exam_results.items():
        if exam_result['exam_data'].get('session_id') in profile['sessions']:
            if exam_result['score'] is not None:
                user_exams.append({
                    "exam_id": exam_id,
                    "topic": exam_result['exam_data']['topic'],
                    "score": exam_result['score'],
                    "graded_at": exam_result['graded_at']
                })
    
    return Response({
        "user_id": user_id,
        "sessions": session_summaries,
        "exam_history": user_exams,
        "learning_progress": profile['learning_progress'],
        "strengths": profile['strengths'],
        "weaknesses": profile['weaknesses']
    })

@api_view(['POST'])
def explain_concept(request):
    """Get detailed explanation of a specific concept"""
    global request_counter
    
    if request_counter >= MAX_REQUESTS:
        return Response({"error": "Request limit exceeded"}, 
                       status=status.HTTP_429_TOO_MANY_REQUESTS)
    
    request_counter += 1
    
    concept = request.data.get("concept", "")
    context = request.data.get("context", "")
    difficulty = request.data.get("difficulty", "intermediate")
    explanation_type = request.data.get("type", "comprehensive")  # comprehensive, simple, example-based
    
    if not concept:
        return Response({"error": "Concept is required"}, 
                       status=status.HTTP_400_BAD_REQUEST)
    
    explanation_prompt = f"""Explain the concept: {concept}
    
    Context: {context if context else 'General education'}
    Difficulty Level: {difficulty}
    Explanation Type: {explanation_type}
    
    Provide a {explanation_type} explanation that includes:
    1. Clear definition
    2. Key principles or components
    3. Practical examples
    4. Common misconceptions (if any)
    5. Related concepts
    6. Practice suggestions
    
    Tailor the complexity to {difficulty} level.
    """
    
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            config=types.GenerateContentConfig(
                system_instruction="You are an expert educator providing clear, structured explanations.",
                temperature=0.6
            ),
            contents=explanation_prompt
        )
        
        explanation = response.text.strip()
        
        return Response({
            "concept": concept,
            "explanation": explanation,
            "difficulty": difficulty,
            "type": explanation_type
        })
        
    except Exception as e:
        return Response({"error": str(e)}, 
                       status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def get_exam_results(request, exam_id):
    """Get detailed exam results"""
    if exam_id not in exam_results:
        return Response({"error": "Exam not found"}, 
                       status=status.HTTP_404_NOT_FOUND)
    
    exam_result = exam_results[exam_id]
    
    if exam_result['score'] is None:
        return Response({"error": "Exam not yet graded"}, 
                       status=status.HTTP_400_BAD_REQUEST)
    
    return Response({
        "exam_id": exam_id,
        "topic": exam_result['exam_data']['topic'],
        "score": exam_result['score'],
        "grade": get_letter_grade(exam_result['score']),
        "correct_count": exam_result['correct_count'],
        "total_questions": exam_result['total_questions'],
        "detailed_results": exam_result['detailed_results'],
        "graded_at": exam_result['graded_at']
    })

def get_letter_grade(percentage):
    """Convert percentage to letter grade"""
    if percentage >= 90:
        return "A"
    elif percentage >= 80:
        return "B"
    elif percentage >= 70:
        return "C"
    elif percentage >= 60:
        return "D"
    else:
        return "F"

# Keep the original chat function for backwards compatibility
@api_view(['POST'])
def chat(request):
    """Original chat function (maintained for backwards compatibility)"""
    global request_counter
    
    if request_counter >= MAX_REQUESTS:
        return Response({"error": "Request limit exceeded. Max requests allowed."},
                        status=status.HTTP_429_TOO_MANY_REQUESTS)
    
    request_counter += 1
    
    user_message = request.data.get("message", "")
    if not user_message:
        return Response({"error": "Message field is required."}, 
                       status=status.HTTP_400_BAD_REQUEST)
    
    system_instruction = "You are a helpful assistant."
    
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                temperature=0.7
            ),
            contents=user_message
        )
        
        assistant_message = response.text.strip()
        
        return Response({"reply": assistant_message})
        
    except Exception as e:
        return Response({"error": str(e)}, 
                       status=status.HTTP_500_INTERNAL_SERVER_ERROR)