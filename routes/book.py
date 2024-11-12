from flask import Blueprint, request
from prisma.models import Book, User
from functools import wraps

book_blueprint = Blueprint('book', __name__)


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_id = request.headers.get('user-id')
        if not user_id:
            return {"error": "Authentication required"}, 401

        user = User.prisma().find_unique(where={'id': int(user_id)})
        if not user or user.role != "ADMIN":
            return {"error": "Admin access required"}, 403
        return f(*args, **kwargs)
    return decorated_function


@book_blueprint.route('/', methods=['GET'])
def list_books():
    # Query parameters
    status = request.args.get('status')
    genre = request.args.get('genre')
    search = request.args.get('search')

    where = {}
    if status:
        where['status'] = status
    if genre:
        where['genre'] = genre
    if search:
        where['OR'] = [
            {'title': {'contains': search}},
            {'author': {'contains': search}},
        ]

    books = Book.prisma().find_many(
        where=where,
        include={'addedBy': True}
    )
    return {"data": [book.model_dump() for book in books]}


@book_blueprint.route('/', methods=['POST'])
@admin_required
def add_book():
    data = request.json
    if not data:
        return {"error": "No data provided"}, 400

    required_fields = ['title', 'author', 'bookNumber', 'publishYear', 'genre']
    for field in required_fields:
        if field not in data:
            return {"error": f"Missing required field: {field}"}, 400

    user_id = int(request.headers.get('user-id'))

    try:
        book = Book.prisma().create(
            data={
                **data,
                'addedBy': {'connect': {'id': user_id}},
                'status': 'AVAILABLE'
            }
        )
        return {"data": book.model_dump()}, 201
    except Exception as e:
        return {"error": f"Book number already exists: {str(e)}"}, 400


@book_blueprint.route('/<int:book_id>', methods=['GET'])
def get_book(book_id):
    book = Book.prisma().find_unique(
        where={'id': book_id},
        include={
            'addedBy': True,
            'requests': {
                'include': {'user': True}
            }
        }
    )
    if not book:
        return {"error": "Book not found"}, 404
    return {"data": book.model_dump()}


@book_blueprint.route('/<int:book_id>', methods=['PUT'])
@admin_required
def update_book(book_id):
    data = request.json
    if not data:
        return {"error": "No data provided"}, 400

    try:
        book = Book.prisma().update(
            where={'id': book_id},
            data=data
        )
        return {"data": book.model_dump()}
    except Exception as e:
        return {"error": str(e)}, 400


@book_blueprint.route('/<int:book_id>', methods=['DELETE'])
@admin_required
def delete_book(book_id):
    try:
        Book.prisma().delete(where={'id': book_id})
        return {"message": "Book deleted successfully"}
    except Exception:
        return {"error": "Cannot delete book with active requests"}, 400


@book_blueprint.route('/stats', methods=['GET'])
@admin_required
def get_stats():
    total_books = Book.prisma().count()
    available_books = Book.prisma().count(where={'status': 'AVAILABLE'})
    borrowed_books = Book.prisma().count(where={'status': 'BORROWED'})

    return {
        "data": {
            "total": total_books,
            "available": available_books,
            "borrowed": borrowed_books
        }
    }
