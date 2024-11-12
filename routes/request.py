from flask import Blueprint, request
from datetime import datetime, timedelta
from prisma.models import User, Book, Request

request_blueprint = Blueprint('request', __name__)


@request_blueprint.route('/', methods=['GET', 'POST'])
def list_create():
    if request.method == 'GET':
        requests = Request.prisma().find_many(
            include={
                'user': True,
                'book': True
            }
        )
        return {
            "data": [req.model_dump() for req in requests]
        }

    if request.method == 'POST':
        data = request.json
        if data is None:
            return {"error": "No data provided"}, 400

        user_id = data.get('userId')
        book_id = data.get('bookId')
        borrow_date = datetime.now()
        # Default 14 days borrowing period
        return_date = borrow_date + timedelta(days=14)

        # Check if book is available
        book = Book.prisma().find_unique(where={'id': book_id})
        if not book or book.status != "AVAILABLE":
            return {"error": "Book is not available"}, 400

        # Create request
        new_request = Request.prisma().create(
            data={
                'user': {'connect': {'id': user_id}},
                'book': {'connect': {'id': book_id}},
                'borrowDate': borrow_date,
                'returnDate': return_date
            }
        )
        return {"data": new_request.model_dump()}, 201


@request_blueprint.route('/user/<int:user_id>', methods=['GET'])
def get_user_requests(user_id):
    requests = Request.prisma().find_many(
        where={'userId': user_id},
        include={
            'book': True
        }
    )
    return {"data": [req.model_dump() for req in requests]}


@request_blueprint.route('/book/<int:book_id>', methods=['GET'])
def get_book_requests(book_id):
    requests = Request.prisma().find_many(
        where={'bookId': book_id},
        include={
            'user': True
        }
    )
    return {"data": [req.model_dump() for req in requests]}


@request_blueprint.route('/<int:request_id>', methods=['GET', 'PUT'])
def handle_request(request_id):
    if request.method == 'GET':
        req = Request.prisma().find_unique(
            where={'id': request_id},
            include={
                'user': True,
                'book': True
            }
        )
        if not req:
            return {"error": "Request not found"}, 404
        return {"data": req.model_dump()}

    if request.method == 'PUT':
        data = request.json
        if data is None:
            return {"error": "No data provided"}, 400

        action = data.get('action')
        if action not in ['APPROVED', 'REJECTED', 'RETURNED']:
            return {"error": "Invalid action"}, 400

        req = Request.prisma().update(
            where={'id': request_id},
            data={'status': action}
        )

        # Update book status
        if action == 'APPROVED':
            Book.prisma().update(
                where={'id': req.bookId},
                data={'status': 'BORROWED'}
            )
        elif action == 'RETURNED':
            Book.prisma().update(
                where={'id': req.bookId},
                data={'status': 'AVAILABLE'}
            )

        return {"data": req.model_dump()}
