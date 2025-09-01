# Smart-Education-Coach

# Ed Coach - Personalized Learning Platform

A comprehensive Django REST API backend for an AI-powered tutoring platform with personalized learning sessions and automated exam generation.

## 🚀 Features

- **Personalized Tutoring Sessions**: Interactive AI tutoring with adaptive difficulty levels
- **Automated Exam Generation**: Create MCQ exams based on tutoring content
- **Auto-Grading System**: Instant grading with detailed feedback
- **Learning Analytics**: Track progress and performance across sessions
- **User Authentication**: Token-based authentication system
- **Learning Path Recommendations**: Personalized study plans based on user performance

## 📋 Prerequisites

- Python 3.8+
- Django 4.0+
- Django REST Framework
- Google Generative AI SDK
- python-dotenv

## ⚙️ Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd tutoring-platform
   ```

2. **Install dependencies**
   ```bash
   pip install django djangorestframework google-genai python-dotenv
   ```

3. **Environment Setup**
   Create a `.env` file in the root directory:
   ```env
   GEMINI_API_KEY=gemini_api_key
   ```

4. **Django Setup**
   ```bash
   python manage.py migrate
   python manage.py runserver
   ```

## 🔗 API Endpoints

### Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/signup/` | Register new user |
| POST | `/api/auth/login/` | User login |

### Tutoring System
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/tutoring/start/` | Start new tutoring session |
| POST | `/api/tutoring/chat/` | Continue tutoring conversation |
| GET | `/api/tutoring/session/{session_id}/progress/` | Get session progress |

### Exam System
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/exam/generate/` | Generate MCQ exam from session |
| POST | `/api/exam/submit/` | Submit exam answers |
| GET | `/api/exam/{exam_id}/results/` | Get detailed exam results |

### Learning Support
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/learning/path/` | Get personalized learning path |
| POST | `/api/learning/explain/` | Get detailed concept explanation |
| GET | `/api/user/{user_id}/profile/` | Get user profile and history |

### Legacy
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/chat/` | Simple chat (backwards compatibility) |

## 📝 API Usage Examples

### 1. User Registration
```bash
curl -X POST http://localhost:8000/api/auth/signup/ \
  -H "Content-Type: application/json" \
  -d '{"username": "jaydeep_biswas", "password": "securepassword"}'
```

**Response:**
```json
{
  "message": "Signup successful.",
  "user_id": 1,
  "username": "jaydeep_biswas",
  "token": "a9b8c7d1234..."
}
```

### 2. Start Tutoring Session
```bash
curl -X POST http://localhost:8000/api/tutoring/start/ \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "1",
    "topic": "Calculus",
    "learning_goals": ["derivatives", "integrals"],
    "difficulty_level": "intermediate"
  }'
```

**Response:**
```json
{
  "session_id": "uuid-here",
  "topic": "Calculus",
  "message": "Hello! I'm excited to help you learn Calculus...",
  "learning_objectives": ["derivatives", "integrals"],
  "difficulty_level": "intermediate"
}
```

### 3. Continue Tutoring Chat
```bash
curl -X POST http://localhost:8000/api/tutoring/chat/ \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "uuid-here",
    "message": "Can you explain derivatives?"
  }'
```

**Response:**
```json
{
  "session_id": "uuid-here",
  "reply": "Derivatives measure the rate of change...",
  "concepts_covered": ["derivatives", "limits"]
}
```

### 4. Generate Exam
```bash
curl -X POST http://localhost:8000/api/exam/generate/ \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "uuid-here",
    "num_questions": 5,
    "difficulty": "medium"
  }'
```

**Response:**
```json
{
  "exam_id": "exam-uuid",
  "topic": "Calculus",
  "difficulty": "medium",
  "questions": [
    {
      "question_id": 1,
      "question": "What is the derivative of x²?",
      "options": ["A) 2x", "B) x", "C) x²", "D) 2"]
    }
  ]
}
```

### 5. Submit Exam
```bash
curl -X POST http://localhost:8000/api/exam/submit/ \
  -H "Content-Type: application/json" \
  -d '{
    "exam_id": "exam-uuid",
    "answers": {"1": "A", "2": "B", "3": "C"}
  }'
```

**Response:**
```json
{
  "exam_id": "exam-uuid",
  "score": 80.0,
  "correct_count": 4,
  "total_questions": 5,
  "grade": "B",
  "detailed_results": [...],
  "feedback": "Great job! You showed strong understanding...",
  "graded_at": "2024-01-15T10:30:00"
}
```

### 6. Get Learning Path
```bash
curl -X POST http://localhost:8000/api/learning/path/ \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "1",
    "subject": "Mathematics",
    "current_level": "intermediate",
    "goals": ["master calculus", "prepare for exams"]
  }'
```

**Response:**
```json
{
  "learning_path": [
    {
      "module": "Advanced Calculus",
      "topics": ["Integration by parts", "Partial derivatives"],
      "estimated_duration": "2-3 hours",
      "difficulty": "intermediate",
      "prerequisites": ["Basic calculus knowledge"]
    }
  ],
  "recommended_next_session": "Integration techniques",
  "study_tips": ["Practice daily", "Focus on problem-solving"]
}
```

## 📊 Data Models

### Tutoring Session
```json
{
  "session_id": "uuid",
  "user_id": "user_id",
  "topic": "subject_name",
  "conversation_history": [
    {
      "role": "user|assistant",
      "content": "message_content",
      "timestamp": "ISO_datetime"
    }
  ],
  "learning_objectives": ["goal1", "goal2"],
  "concepts_covered": ["concept1", "concept2"],
  "difficulty_level": "beginner|intermediate|advanced",
  "status": "active|completed",
  "created_at": "ISO_datetime"
}
```

### Exam Structure
```json
{
  "exam_id": "uuid",
  "session_id": "uuid",
  "topic": "subject_name",
  "difficulty": "easy|medium|hard",
  "questions": [
    {
      "question_id": 1,
      "question": "Question text?",
      "options": ["A) Option1", "B) Option2", "C) Option3", "D) Option4"],
      "correct_answer": "A",
      "explanation": "Explanation text"
    }
  ],
  "created_at": "ISO_datetime"
}
```

### User Profile
```json
{
  "user_id": "user_id",
  "sessions": ["session_id1", "session_id2"],
  "exam_history": [
    {
      "exam_id": "uuid",
      "topic": "subject",
      "score": 85.0,
      "graded_at": "ISO_datetime"
    }
  ],
  "learning_progress": {},
  "strengths": ["topic1", "topic2"],
  "weaknesses": ["topic3", "topic4"]
}
```

## 🏗️ Architecture

### Key Components

1. **Session Management**: Handles tutoring session lifecycle
2. **AI Integration**: Google Gemini API for content generation
3. **Exam Engine**: Automated MCQ generation and grading
4. **Analytics**: Progress tracking and performance analysis
5. **Authentication**: Token-based user management

### Storage

- **In-Memory Storage**: Current implementation uses dictionaries
- **Production Ready**: Easily replaceable with database models
- **Data Persistence**: Sessions, exams, and user profiles stored temporarily

## ⚡ Performance Features

- **Request Limiting**: Maximum 100 requests per session
- **Context Management**: Maintains last 10 conversation messages
- **Efficient Grading**: Instant automated scoring
- **Smart Caching**: Reuses session data for performance

## 🔒 Security

- **Token Authentication**: Secure API access
- **Input Validation**: All endpoints validate required parameters
- **Error Handling**: Comprehensive error responses
- **Rate Limiting**: Prevents API abuse

## 🚀 Production Considerations

1. **Database Migration**: Replace in-memory storage with PostgreSQL/MySQL
2. **Redis Caching**: Add caching layer for improved performance
3. **Celery Tasks**: Async processing for AI generation
4. **API Versioning**: Version control for API endpoints
5. **Monitoring**: Add logging and metrics collection

## 📈 Scalability

- **Stateless Design**: Easy horizontal scaling
- **API-First Architecture**: Frontend agnostic
- **Microservice Ready**: Modular component design
- **Cloud Deployment**: AWS/GCP/Azure compatible

---

**Built with ❤️ using Django REST Framework and Google Gemini AI**
