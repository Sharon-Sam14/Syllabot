# Syllabot API Integration Documentation

This document describes how to integrate the frontend application with the Python FastAPI backend and SQLite/PostgreSQL database.

---

## 🚀 Running the Backend Server Locally

1. **Activate the Virtual Environment**:
   - On Windows:
     ```powershell
     .\backend\venv\Scripts\activate
     ```
   - On Unix/macOS:
     ```bash
     source backend/venv/bin/activate
     ```
2. **Install Dependencies**:
   ```bash
   pip install -r backend/requirements.txt
   ```
3. **Set Up Environment Variables**:
   A local `.env` file should be placed at the root of the project. Default settings:
   ```env
   PROJECT_NAME=Syllabot
   DATABASE_URL=sqlite:///./syllabot.db
   JWT_SECRET_KEY=9a1f2b3c4d5e6f7g8h9i0j1k2l3m4n5o6p7q8r9s0t1u2v3w4x5y6z7a8b9c0d1e
   JWT_ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=10080
   ```
4. **Run Database Migrations**:
   ```bash
   alembic upgrade head
   ```
5. **Start Uvicorn Development Server**:
   ```bash
   uvicorn backend.main:app --reload --port 8000
   ```

FastAPI automatically generates an interactive **Swagger UI** containing all models and schemas at:
👉 **[http://localhost:8000/docs](http://localhost:8000/docs)**

---

## 🔒 Authentication Flow

FastAPI uses standard OAuth2 Password Flow. Tokens must be sent in the header of all protected requests:
`Authorization: Bearer <access_token>`

### 1. User Signup
* **Endpoint**: `POST /api/v1/auth/signup`
* **Request Body (JSON)**:
  ```json
  {
    "email": "student@example.com",
    "password": "securepassword123",
    "name": "Alex Student"
  }
  ```
* **Response (JSON)**:
  ```json
  {
    "id": 1,
    "email": "student@example.com",
    "name": "Alex Student",
    "created_at": "2026-07-18T21:40:00.000"
  }
  ```

### 2. User Login (Retrieve Token)
* **Endpoint**: `POST /api/v1/auth/login`
* **Request Body (Form Data)**:
  - `username`: `student@example.com`
  - `password`: `securepassword123`
* **Response (JSON)**:
  ```json
  {
    "access_token": "eyJhbGciOiJIUzI1NiIsIn...",
    "token_type": "bearer"
  }
  ```

### 3. Fetch Active Profile
* **Endpoint**: `GET /api/v1/auth/me`
* **Headers**: `Authorization: Bearer <token>`
* **Response (JSON)**:
  ```json
  {
    "id": 1,
    "email": "student@example.com",
    "name": "Alex Student",
    "created_at": "2026-07-18T21:40:00.000"
  }
  ```

---

## 📚 Syllabus Ingestion & Parsing

### 1. Ingest Raw Syllabus Text
Converts raw syllabus input into a structured parent-child topic tree dynamically.
* **Endpoint**: `POST /api/v1/syllabi/`
* **Headers**: `Authorization: Bearer <token>`
* **Request Body (JSON)**:
  ```json
  {
    "raw_text": "Unit 1: Intro to Python\n- Variables\n- Loops\nUnit 2: OOP\n- Classes"
  }
  ```
* **Response (JSON)**:
  ```json
  {
    "id": 1,
    "user_id": 1,
    "raw_text": "...",
    "parsed_tree_json": [
      {
        "id": "node_1",
        "title": "Unit 1: Intro to Python",
        "parent_id": null,
        "level": 0,
        "confidence": 1.0,
        "importance_hint": 1.0,
        "children": [
          {
            "id": "node_2",
            "title": "Variables",
            "parent_id": "node_1",
            "level": 2,
            "confidence": 0.8,
            "importance_hint": 1.0,
            "children": []
          }
        ]
      }
    ],
    "created_at": "..."
  }
  ```

---

## 📅 Study Plan Generation

### 1. Create Study Plan
Automatically partitions the parsed syllabus into a day-by-day schedule.
* **Endpoint**: `POST /api/v1/plans/`
* **Headers**: `Authorization: Bearer <token>`
* **Request Body (JSON)**:
  ```json
  {
    "syllabus_id": 1,
    "start_date": "2026-07-19",
    "end_date": "2026-07-22"
  }
  ```
* **Response (JSON)**:
  Exposes a list of days in `plan_json`. If remaining days exceed topics, it schedules review days. If days are short, it groups topics.
  ```json
  {
    "id": 1,
    "syllabus_id": 1,
    "start_date": "2026-07-19",
    "end_date": "2026-07-22",
    "status": "active",
    "plan_json": [
      {
        "day_number": 1,
        "date": "2026-07-19",
        "topics": [
          {
            "id": "node_2",
            "title": "Variables",
            "full_path": "Unit 1: Intro to Python > Variables",
            "importance_hint": 1.0,
            "complexity": 1.0
          }
        ],
        "is_review": false,
        "notes": "Primary focus: Variables"
      }
    ],
    "created_at": "..."
  }
  ```

### 2. Manual Replan Trigger
* **Endpoint**: `POST /api/v1/plans/{plan_id}/replan`
* **Headers**: `Authorization: Bearer <token>`
* **Query Parameters (Optional)**:
  - `from_date`: date (e.g. `2026-07-20`). Defaults to tomorrow.
* **Response (JSON)**: Returns the updated `StudyPlanResponse` schedule.

---

## 📈 Daily Progress Logging (Auto-Replanning Trigger)

When a student checks in, if they did not complete the topics scheduled for today or earlier, the backend **automatically triggers a replan**, re-routing remaining topics starting from tomorrow onwards.

### 1. Log Daily Progress
* **Endpoint**: `POST /api/v1/progress/{plan_id}`
* **Headers**: `Authorization: Bearer <token>`
* **Request Body (JSON)**:
  ```json
  {
    "date": "2026-07-19",
    "completed_hours": 2.0,
    "completed_topics": ["node_2"],
    "check_in_note": "Finished basic variables, feeling confident."
  }
  ```
* **Response (JSON)**:
  ```json
  {
    "id": 1,
    "plan_id": 1,
    "date": "2026-07-19",
    "completed_hours": 2.0,
    "completed_topics": ["node_2"],
    "check_in_note": "Finished basic variables, feeling confident."
  }
  ```

### 2. Get Progress Logs History
* **Endpoint**: `GET /api/v1/progress/{plan_id}`
* **Headers**: `Authorization: Bearer <token>`
* **Response (JSON)**: Returns a list of daily check-ins.
