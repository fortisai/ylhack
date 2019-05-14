from flask_restful import abort, Api, Resource
from werkzeug.security import check_password_hash, generate_password_hash
from database import *


tokens = {}


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
        user = User.query.filter(User.login == login).first()
        if not user:
            return jsonify({"error": "no such user"})
        if not check_password_hash(user.password, password):
            return jsonify({"error": "wrong pass"})
        token = generate_password_hash(login + password)
        tokens[token] = login
        return jsonify({"token": token})


REQ = ["statement", "time_end", "author_id"]


class Tasks(Resource):
    def get(self):
        token = request.form.get("token", None)
        if token is None:
            return jsonify({"error": "no token"})
        elif token not in tokens:
            return jsonify({"error": "invalid token"})
        tasks = Problem.query.filter(Problem.solver_id == tokens[token]).all()
        return jsonify(tasks=[remove_sa(t.__dict__) for t in tasks])

    def post(self):
        nargs = dict(request.form)
        args = {}
        for i in nargs:
            args[i] = nargs[i][0]
        if "token" in args:
            args["author_id"] = tokens[args["token"]]
            del args["token"]
        print(args)
        if all([i in args for i in REQ]):
            try:
                print(args)
                new_task = Problem(**args)
            except TypeError as e:
                print(e)
                return jsonify({"error": "wrong args"})
            else:
                db.session.add(new_task)
                db.session.commit()
                return jsonify({"success": "OK"})
        return jsonify({"error": "Not enough params"})


class Task(Resource):
    def get(self, task_id):
        token = request.form.get("token", None)
        task = Problem.query.filter(Problem.id == task_id).first()
        if not task:
            return jsonify({"error": "no such task"})
        return jsonify(task=remove_sa(task))

    def delete(self, task_id):
        token = request.form.get("token", None)
        if not token in tokens:
            return jsonify({"error": "inv. token"})
        task = Problem.query.filter(Problem.id == task_id).first()
        if not task:
            return jsonify({"error": "no such task"})
        elif not task.author_id == tokens[token]:
            return jsonify({"error": "that's not yours, pal"})
        db.session.delete(task)
        db.session.commit()
        return jsonify({"success": "OK"})

# comment



