  # Library Service App

A small library management REST API built with Python, Flask, and PostgreSQL.

## Features
- list/Create/update books & members
- Record book borrow operations & returns
- Query borrowings by member, book, or outstanding loans
- simple UI

## Files
- `app.py` - Flask application and REST API endpoints
- `models.py` - SQLAlchemy models for books, members, and borrowings
- `db.py` - SQLAlchemy database initialization
- `schema.sql` - PostgreSQL schema for database setup
- `requirements.txt` - Python dependencies
- `static/index.html` - Minimal frontend for basic operations
- `.env.example` - Example environment variables

## Setup

1. Install Python 3.10+ and PostgreSQL.
2. Create a database and user in PostgreSQL.

Example using `psql`:

```bash
CREATE DATABASE library_db;
CREATE USER library_user WITH PASSWORD 'library_pass';
GRANT ALL PRIVILEGES ON DATABASE library_db TO library_user;
```

3. Create a Python virtual environment and install dependencies:

```bash
cd library_service
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
```

4. Configure environment variables.

Copy `.env.example` to `.env` or set the variables directly:

```bash
set DB_HOST=localhost
set DB_PORT=5432
set DB_NAME=library_db
set DB_USER=library_user
set DB_PASSWORD=library_pass
```

Optionally, use `DATABASE_URL` instead:

```bash
set DATABASE_URL=postgresql://library_user:library_pass@localhost:5432/library_db
```

5. Initialize the database.

You can run the SQL schema directly:

```bash
psql -h localhost -U library_user -d library_db -f schema.sql
```

The app will also create missing tables automatically when started.

## Run server

```bash
python app.py
```

Open `http://127.0.0.1:5000` to view the minimal frontend.

## API Endpoints

- `GET /books`
- `GET /books/<id>`
- `POST /books`
- `PUT /books/<id>`
- `GET /members`
- `GET /members/<id>`
- `POST /members`
- `PUT /members/<id>`
- `GET /borrowings`
- `GET /members/<id>/borrowings`
- `POST /borrowings`
- `POST /borrowings/<id>/return`

## Example requests

Create a book:

```bash
curl -X POST http://127.0.0.1:5000/books -H "Content-Type: application/json" -d "{\"title\": \"1984\", \"author\": \"George Orwell\"}"
```

Borrow a book:

```bash
curl -X POST http://127.0.0.1:5000/borrowings -H "Content-Type: application/json" -d "{\"member_id\": 1, \"book_id\": 1}"
```

Return a borrowed book:

```bash
curl -X POST http://127.0.0.1:5000/borrowings/1/return
```
