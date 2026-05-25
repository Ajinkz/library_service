 # API Documentation

This document describes the REST API endpoints available in the `library_service` Flask app.

Base URL: `http://127.0.0.1:5000`

All endpoints return JSON and use standard HTTP status codes. Error responses use the format:

```json
{ "error": "..." }
```

---

## Root

### `GET /`
- Description: Serve the main static HTML page.
- Response: HTML page content.

---

## Books

### `GET /books`
- Description: List books.
- Query parameters:
  - `author` (optional) - filter by author name substring, case-insensitive
  - `title` (optional) - filter by title substring, case-insensitive
- Response: array of book objects.

### `GET /books/<id>`
- Description: Get a single book by ID.
- Path parameters:
  - `id` - book ID
- Response: book object
- Possible errors:
  - `404` if book not found

### `POST /books`
- Description: Create a new book.
- Request body (JSON):
  - `title` (string, required)
  - `author` (string, required)
  - `isbn` (string, optional)
  - `publisher` (string, optional)
  - `publication_year` (integer, optional)
  - `total_copies` (integer, optional, defaults to `1`)
  - `available_copies` (integer, optional, defaults to `total_copies` or `1`)
- Response: created book object
- Status: `201` on success
- Possible errors:
  - `400` if title or author is missing
  - `400` if database constraints are violated (for example duplicate ISBN)

### `PUT /books/<id>`
- Description: Update an existing book.
- Path parameters:
  - `id` - book ID
- Request body (JSON): any of the following fields:
  - `title`
  - `author`
  - `isbn`
  - `publisher`
  - `publication_year`
  - `total_copies`
  - `available_copies`
- Notes:
  - `total_copies` and `available_copies` must be non-negative.
  - If `total_copies` is decreased below the previous value and `available_copies` is greater than `total_copies`, the server adjusts `available_copies` downward to match `total_copies`.
- Response: updated book object
- Possible errors:
  - `404` if book not found
  - `400` if payload missing or copy counts are invalid
  - `400` if database constraints are violated

---

## Members

### `GET /members`
- Description: List members.
- Query parameters:
  - `name` (optional) - filter by member name substring, case-insensitive
- Response: array of member objects.

### `GET /members/<id>`
- Description: Get a single member by ID.
- Path parameters:
  - `id` - member ID
- Response: member object
- Possible errors:
  - `404` if member not found

### `POST /members`
- Description: Create a new member.
- Request body (JSON):
  - `name` (string, required)
  - `email` (string, optional)
  - `phone` (string, optional)
  - `address` (string, optional)
- Response: created member object
- Status: `201` on success
- Possible errors:
  - `400` if name is missing
  - `400` if database constraints are violated (for example duplicate email)

### `PUT /members/<id>`
- Description: Update an existing member.
- Path parameters:
  - `id` - member ID
- Request body (JSON): any of the following:
  - `name`
  - `email`
  - `phone`
  - `address`
- Response: updated member object
- Possible errors:
  - `404` if member not found
  - `400` if payload missing or database constraints are violated

---

## Borrowings

### `GET /borrowings`
- Description: List borrowing records.
- Query parameters:
  - `member_id` (integer, optional) - filter by member ID
  - `book_id` (integer, optional) - filter by book ID
  - `outstanding` (optional) - include only borrowings not yet returned when set to `1`, `true`, or `yes`
- Response: array of borrowing records.

### `GET /members/<id>/borrowings`
- Description: List borrowings for a specific member.
- Path parameters:
  - `id` - member ID
- Response: array of borrowing records for that member
- Possible errors:
  - `404` if member not found

### `POST /borrowings`
- Description: Create a borrowing record and decrement available copies for the book.
- Request body (JSON):
  - `member_id` (integer, required)
  - `book_id` (integer, required)
  - `due_days` (integer, optional, defaults to `14`)
  - `notes` (string, optional)
- Response: created borrowing object
- Status: `201` on success
- Possible errors:
  - `400` if member_id or book_id is missing
  - `404` if member or book is not found
  - `400` if no copies are available to borrow
  - `400` if database constraints prevent creation

### `POST /borrowings/<id>/return`
- Description: Mark a borrowing as returned and increment the book's available copies.
- Path parameters:
  - `id` - borrowing ID
- Response: updated borrowing object
- Possible errors:
  - `404` if borrowing record not found
  - `400` if the borrowing record is already returned

---

## Request Examples

Create a book:

```bash
curl -X POST http://127.0.0.1:5000/books \
  -H "Content-Type: application/json" \
  -d '{"title": "1984", "author": "George Orwell", "isbn": "9780451524935", "total_copies": 3}'
```

Create a member:

```bash
curl -X POST http://127.0.0.1:5000/members \
  -H "Content-Type: application/json" \
  -d '{"name": "Alice Smith", "email": "alice@example.com"}'
```

Borrow a book:

```bash
curl -X POST http://127.0.0.1:5000/borrowings \
  -H "Content-Type: application/json" \
  -d '{"member_id": 1, "book_id": 1, "due_days": 14}'
```

Return a book:

```bash
curl -X POST http://127.0.0.1:5000/borrowings/1/return
```

List outstanding borrowings:

```bash
curl http://127.0.0.1:5000/borrowings?outstanding=true
```
