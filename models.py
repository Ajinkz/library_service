from datetime import UTC, datetime, timedelta
from time import timezone
from db import db

class Book(db.Model):
    """Model representing a book in the library."""
    __tablename__ = "books"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(256), nullable=False)
    author = db.Column(db.String(256), nullable=False)
    isbn = db.Column(db.String(64), unique=True)
    publisher = db.Column(db.String(256))
    publication_year = db.Column(db.Integer)
    total_copies = db.Column(db.Integer, nullable=False, default=1)
    available_copies = db.Column(db.Integer, nullable=False, default=1)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now(UTC))

    borrowings = db.relationship("Borrowing", back_populates="book")

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "author": self.author,
            "isbn": self.isbn,
            "publisher": self.publisher,
            "publication_year": self.publication_year,
            "total_copies": self.total_copies,
            "available_copies": self.available_copies,
            "created_at": self.created_at.isoformat(),
        }

class Member(db.Model):
    """Model representing a library member."""
    __tablename__ = "members"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256), nullable=False)
    email = db.Column(db.String(256), unique=True)
    phone = db.Column(db.String(64))
    address = db.Column(db.String(512))
    joined_at = db.Column(db.DateTime, nullable=False, default=datetime.now(UTC))

    borrowings = db.relationship("Borrowing", back_populates="member")

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "phone": self.phone,
            "address": self.address,
            "joined_at": self.joined_at.isoformat(),
        }

class Borrowing(db.Model):
    """Model representing a borrowing record of a book by a member."""
    __tablename__ = "borrowings"

    id = db.Column(db.Integer, primary_key=True)
    member_id = db.Column(db.Integer, db.ForeignKey("members.id"), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey("books.id"), nullable=False)
    borrowed_at = db.Column(db.DateTime, nullable=False, default=datetime.now(UTC))
    due_at = db.Column(db.DateTime, nullable=False)
    returned_at = db.Column(db.DateTime, nullable=True)
    notes = db.Column(db.String(512))

    member = db.relationship("Member", back_populates="borrowings")
    book = db.relationship("Book", back_populates="borrowings")

    def to_dict(self):
        return {
            "id": self.id,
            "member_id": self.member_id,
            "book_id": self.book_id,
            "borrowed_at": self.borrowed_at.isoformat(),
            "due_at": self.due_at.isoformat(),
            "returned_at": self.returned_at.isoformat() if self.returned_at else None,
            "notes": self.notes,
        }
