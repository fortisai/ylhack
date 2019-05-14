from flask_restful import abort, Api, Resource
from database import *
from werkzeug.security import check_password_hash, generate_password_hash

tokens = {}
app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
api = Api(app)


def remove_sa(d):
    d.pop('_sa_instance_state', None)
    return d


class Auth(Resource):
    def post(self):
        login, password = request.form.get("login", None), request.form.get("password", None)
        if login is None:
            return jsonify({"error": "no login"})
        elif password is None:
            return jsonify({"error": "no password"})
        user = User.query.filter_by(User.login == login).first()
        if not user:
            return jsonify({"error": "no such user"})
        if not check_password_hash(password, user.password):
            return jsonify({"error": "wrong pass"})
        token = generate_password_hash(login + password)
        tokens[token] = login
        return jsonify({"token": token})


class Tasks(Resource):
    def get(self):
        token = request.form.get("token", None)
        if token is None:
            return jsonify({"error": "no token"})
        elif token not in tokens:
            return jsonify({"error": "invalid token"})
        tasks = Problem.query.filter_by(Problem.solver_id == tokens[token]).all()
        return jsonify(tasks=[remove_sa(t.__dict__) for t in tasks])


class Task(Resource):
    def get(self, task_id):
        token = request.form.get("token", None)
        task = Problem.query.filter_by(Problem.id == task_id).first()
        if not task:
            return jsonify({"error": "no such task"})
        return jsonify(task=remove_sa(task))


api.add_resource(Task, '/api/task/<int:task_id>')
api.add_resource(Tasks, '/api/task')
api.add_resource(Auth, '/api/auth')
