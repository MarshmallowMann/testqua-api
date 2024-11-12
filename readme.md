# Library Management System API

A Flask-based REST API for managing a library system with book requests, user management, and role-based access control.

## Setup Guide

### Prerequisites
- Python 3.8 or higher
- Git
- SQLite

### Windows Setup

1. Clone the repository
2. Create and activate virtual environment
   
    ```bash
    python -m venv venv
    .\venv\Scripts\activate
    ```

3. Install dependencies

    ```bash
    pip install -r requirements.txt
    ```

4. Initialize Prisma
    ```bash
    prisma db push
    prisma generate
    ```
5. Run the application

    ```bash
    python app.py
    ```
6. Access the API at `http://http://localhost:5000`

## API Documentation

### User Management (`/user`)
- `GET /user` - List all users
- `POST /user` - Create new user
  ```json
  {
    "name": "string",
    "email": "string",
    "username": "string",
    "age": "number",
    "role": "string"
  }
  ```
- `GET /user/{id}` - Get user by ID
- `PUT /user/{id}` - Update user
- `DELETE /user/{id}` - Delete user

### Book Management (`/book`)
- `GET /book` - List all books
  - Query params: 
    - status (AVAILABLE/BORROWED)
    - genre
    - search (searches title and author)
- `POST /book` - Add new book (Admin only)
  ```json
  {
    "title": "string",
    "author": "string",
    "bookNumber": "string",
    "publishYear": "number",
    "genre": "string",
    "description": "string"
  }
  ```
- `GET /book/{id}` - Get book details
- `PUT /book/{id}` - Update book details (Admin only)
- `DELETE /book/{id}` - Delete book (Admin only)
- `GET /book/stats` - Get library statistics (Admin only)

### Book Requests (`/request`)
- `GET /request` - List all requests
- `POST /request` - Create borrow request
  ```json
  {
    "userId": "number",
    "bookId": "number"
  }
  ```
- `GET /request/user/{userId}` - Get user's requests
- `GET /request/book/{bookId}` - Get book's requests
- `PUT /request/{id}` - Update request status
  ```json
  {
    "action": "APPROVED" | "REJECTED" | "RETURNED"
  }
  ```

## Authentication
Headers required for authenticated endpoints:
```
user-id: <user_id>
```

## Project Structure
```
testqua-api/
├── app.py              # Application entry point
├── requirements.txt    # Project dependencies
├── schema.prisma      # Database schema
├── database.db        # SQLite database
└── routes/
    ├── book.py        # Book management endpoints
    ├── request.py     # Book request endpoints
    └── user.py        # User management endpoints
```

### Status Codes
- 200: Success
- 201: Created
- 400: Bad Request
- 401: Unauthorized
- 403: Forbidden
- 404: Not Found

## Database Models

### User Model
- id: Int (Primary Key)
- email: String (Unique)
- name: String
- username: String (Unique)
- age: Int (Optional)
- role: String (Default: "REGULAR")
- requests: Request[]
- booksAdded: Book[]

### Book Model
- id: Int (Primary Key)
- title: String
- description: String (Optional)
- author: String
- bookNumber: String (Unique)
- publishYear: Int
- genre: String
- status: String (Default: "AVAILABLE")
- requests: Request[]
- addedBy: User

### Request Model
- id: Int (Primary Key)
- status: String (Default: "PENDING")
- borrowDate: DateTime
- returnDate: DateTime
- userId: Int (Foreign Key)
- bookId: Int (Foreign Key)

## Business Rules
1. User Management
   - Email and username must be unique
   - Only ADMIN users can perform certain operations
   - User roles: "ADMIN", "REGULAR"

2. Book Management
   - Book number must be unique
   - Book status: "AVAILABLE", "BORROWED"
   - Only ADMIN can add/edit/delete books

3. Request Management
   - Default loan period: 14 days
   - Request status flow: PENDING → APPROVED/REJECTED → RETURNED
   - Books must be AVAILABLE to be requested