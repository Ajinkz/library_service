import os
from datetime import datetime, timedelta, timezone, UTC
from flask import Flask, jsonify, request
from sqlalchemy.exc import IntegrityError
from db import db, init_db
from models import Book, Member, Borrowing


def create_app():
    """Create/configure the Flask application"""

    app = Flask(__name__, static_folder="static", static_url_path="")

    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        user = os.getenv("DB_USER", "postgres")
        password = os.getenv("DB_PASSWORD", "*********")
        host = os.getenv("DB_HOST", "localhost")
        port = os.getenv("DB_PORT", "5432")
        name = os.getenv("DB_NAME", "library_db")
        database_url = f"postgresql://{user}:{password}@{host}:{port}/{name}"

    app.config["SQLALCHEMY_DATABASE_URI"] = database_url
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # Initialize the database with the Flask app
    db.init_app(app)

    @app.errorhandler(404)
    def not_found(error):
        """Handle 404 errors with a JSON response."""
        return jsonify({"error": "Not found"}), 404

    @app.errorhandler(400)
    def bad_request(error):
        """Handle 400 errors with a JSON response."""
        return jsonify({"error": "Bad request"}), 400

    @app.route("/", methods=["GET"])
    @app.route("/home", methods=["GET"])
    def index():
        """Serve the main HTML page."""
        return app.send_static_file("index.html")

    def json_error(message, status=400):
        """Helper function to return JSON error responses."""
        return jsonify({"error": message}), status

    def update_model_from_json(model, data, fields):
        for field in fields:
            if field in data:
                setattr(model, field, data[field])

    @app.route("/books", methods=["GET"])
    def list_books():
        """List books with optional filtering by author and title."""

        author = request.args.get("author")
        title = request.args.get("title")
        query = Book.query
        if author:
            query = query.filter(Book.author.ilike(f"%{author}%"))
        if title:
            query = query.filter(Book.title.ilike(f"%{title}%"))
        return jsonify([book.to_dict() for book in query.order_by(Book.id).all()])

    @app.route("/books/<int:book_id>", methods=["GET"])
    def get_book(book_id):
        """Get details of a specific book by ID."""

        book = Book.query.get(book_id)
        if not book:
            return json_error("Book not found", 404)
        return jsonify(book.to_dict())

    @app.route("/books", methods=["POST"])
    def create_book():
        """Create a new book record from JSON payload."""

        payload = request.get_json(force=True)
        if not payload or not payload.get("title") or not payload.get("author"):
            return json_error("A book must include title and author")

        book = Book(
            title=payload["title"],
            author=payload["author"],
            isbn=payload.get("isbn"),
            publisher=payload.get("publisher"),
            publication_year=payload.get("publication_year"),
            total_copies=payload.get("total_copies", 1),
            available_copies=payload.get("available_copies", payload.get("total_copies", 1)),
        )
        db.session.add(book)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            return json_error("Book data violates integrity constraints (duplicate ISBN?)", 400)
        return jsonify(book.to_dict()), 201

    @app.route("/books/<int:book_id>", methods=["PUT"])
    def update_book(book_id):
        """Update an existing book record with JSON payload."""

        book = Book.query.get(book_id)
        if not book:
            return json_error("Book not found", 404)
        payload = request.get_json(force=True)
        if not payload:
            return json_error("Missing JSON payload")
        previous_total = book.total_copies
        update_model_from_json(book, payload, ["title", "author", "isbn", "publisher", 
                                               "publication_year", "total_copies", "available_copies"])
        if book.total_copies < 0 or book.available_copies < 0:
            return json_error("Copy counts must be non-negative")
        if book.total_copies < previous_total and book.available_copies > book.total_copies:
            book.available_copies = book.total_copies
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            return json_error("Book update violates database constraints", 400)
        return jsonify(book.to_dict())

    @app.route("/members", methods=["GET"])
    def list_members():
        """List members with optional filtering by name."""
        name = request.args.get("name")
        query = Member.query
        if name:
            query = query.filter(Member.name.ilike(f"%{name}%"))
        return jsonify([member.to_dict() for member in query.order_by(Member.id).all()])

    @app.route("/members/<int:member_id>", methods=["GET"])
    def get_member(member_id):
        """Get details of a specific member by ID."""
        member = Member.query.get(member_id)
        if not member:
            return json_error("Member not found", 404)
        return jsonify(member.to_dict())

    @app.route("/members", methods=["POST"])
    def create_member():
        payload = request.get_json(force=True)
        if not payload or not payload.get("name"):
            return json_error("A member must include a name")

        member = Member(
            name=payload["name"],
            email=payload.get("email"),
            phone=payload.get("phone"),
            address=payload.get("address"),
        )
        db.session.add(member)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            return json_error("Member data violates integrity constraints (duplicate email?)", 400)
        return jsonify(member.to_dict()), 201

    @app.route("/members/<int:member_id>", methods=["PUT"])
    def update_member(member_id):
        member = Member.query.get(member_id)
        if not member:
            return json_error("Member not found", 404)
        payload = request.get_json(force=True)
        if not payload:
            return json_error("Missing JSON payload")
        update_model_from_json(member, payload, ["name", "email", "phone", "address"])
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            return json_error("Member update violates database constraints", 400)
        return jsonify(member.to_dict())

    @app.route("/borrowings", methods=["GET"])
    def list_borrowings():
        member_id = request.args.get("member_id", type=int)
        book_id = request.args.get("book_id", type=int)
        outstanding = request.args.get("outstanding")
        query = Borrowing.query
        if member_id:
            query = query.filter(Borrowing.member_id == member_id)
        if book_id:
            query = query.filter(Borrowing.book_id == book_id)
        if outstanding and outstanding.lower() in ["1", "true", "yes"]:
            query = query.filter(Borrowing.returned_at.is_(None))
        return jsonify([borrow.to_dict() for borrow in query.order_by(Borrowing.id).all()])

    @app.route("/members/<int:member_id>/borrowings", methods=["GET"])
    def member_borrowings(member_id):
        member = Member.query.get(member_id)
        if not member:
            return json_error("Member not found", 404)
        borrowings = Borrowing.query.filter_by(member_id=member_id).order_by(Borrowing.id).all()
        return jsonify([borrow.to_dict() for borrow in borrowings])

    @app.route("/borrowings", methods=["POST"])
    def borrow_book():
        payload = request.get_json(force=True)
        if not payload:
            return json_error("Missing JSON payload")
        member_id = payload.get("member_id")
        book_id = payload.get("book_id")
        if not member_id or not book_id:
            return json_error("member_id and book_id are required")

        member = Member.query.get(member_id)
        book = Book.query.get(book_id)
        if not member:
            return json_error("Member not found", 404)
        if not book:
            return json_error("Book not found", 404)
        if book.available_copies < 1:
            return json_error("No copies available to borrow", 400)

        due_days = payload.get("due_days", 14)
        borrowed_at = datetime.utcnow()
        due_at = borrowed_at + timedelta(days=due_days)
        borrowing = Borrowing(
            member_id=member_id,
            book_id=book_id,
            borrowed_at=borrowed_at,
            due_at=due_at,
            notes=payload.get("notes"),
        )
        book.available_copies = max(0, book.available_copies - 1)
        db.session.add(borrowing)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            return json_error("Borrowing operation failed due to data constraints", 400)
        return jsonify(borrowing.to_dict()), 201

    @app.route("/borrowings/<int:borrowing_id>/return", methods=["POST"])
    def return_book(borrowing_id):
        borrowing = Borrowing.query.get(borrowing_id)
        if not borrowing:
            return json_error("Borrowing record not found", 404)
        if borrowing.returned_at is not None:
            return json_error("This borrowing record is already returned", 400)

        borrowing.returned_at = datetime.utcnow()
        borrowing.book.available_copies += 1
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            return json_error("Return operation failed due to data constraints", 400)
        # db.session.commit()
        return jsonify(borrowing.to_dict())

    return app


if __name__ == "__main__":
    application = create_app()
    with application.app_context():
        init_db()
    application.run(host="0.0.0.0", port=5000, debug=True)
