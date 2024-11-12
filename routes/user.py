from flask import Blueprint, request
from prisma.models import User

user_blueprint = Blueprint('user', __name__)


@user_blueprint.route('/', methods=['GET', 'POST'])
def list_create():
    if request.method == 'GET':
        users = User.prisma().find_many()
        return {
            "data": [user.model_dump() for user in users]
        }

    if request.method == 'POST':
        data = request.json

        if data is None:
            return {"error": "No data provided"}, 400

        name = data.get('name')
        email = data.get('email')
        username = data.get('username')
        age = data.get('age')

        if name is None or email is None or username is None:
            return {"error": "You need to provide name, email, and username"}, 400

        try:
            user = User.prisma().create(
                data={
                    'name': name,
                    'email': email,
                    'username': username,
                    'age': age
                }
            )
        except Exception as e:
            return {"error": str(e)}, 400

        return {"data": user.model_dump()}, 201


@user_blueprint.route('/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user = User.prisma().find_first(where={'id': user_id})
    if user:
        return {"data": user.model_dump()}
    return {"error": "User not found"}, 404


@user_blueprint.route('/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    data = request.json
    user = User.prisma().update(where={'id': user_id}, data=data)
    return {"data": user.model_dump()}


@user_blueprint.route('/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    User.prisma().delete(where={'id': user_id})
    return {"message": "User deleted"}
