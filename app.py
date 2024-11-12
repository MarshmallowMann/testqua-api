
from flask import Flask
from prisma import Prisma, register
from routes.user import user_blueprint
from routes.book import book_blueprint
from routes.request import request_blueprint

db = Prisma()
db.connect()
register(db)
app = Flask(__name__)


@app.route('/', methods=['GET'])
def index():
    return {
        "ping": "pong"
    }


app.register_blueprint(user_blueprint, url_prefix='/user')
app.register_blueprint(book_blueprint, url_prefix='/book')
app.register_blueprint(request_blueprint, url_prefix='/request')

if __name__ == "__main__":
    app.run(debug=True, port=5000, host='0.0.0.0', threaded=True)
