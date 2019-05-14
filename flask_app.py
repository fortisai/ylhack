from database import *
from flask import abort
from werkzeug.security import generate_password_hash, check_password_hash
import datetime
from telegram_ import get_valid, send_code

# Main page


@app.route('/')
@app.route('/index')
def main():
    if 'user_id' not in session:
        return redirect('/not_logged')
    return render_template('main.html', problems=Problem.query.filter(Problem.author_id == session['user_id'], ).all())


@app.route('/delegated')
def delegated():
    if 'user_id' not in session:
        return redirect('/not_logged')
    problems = Problem.query.filter(Problem.solver_id == session['user_id']).all()
    return render_template('delegated.html', problems=problems)


# User logout


@app.route('/logout')
def logout():
    session.pop('username', 0)
    session.pop('user_id', 0)
    session.pop('admin', 0)
    return redirect('/')


@app.route('/not_logged')
def unlog():
    return render_template('unlogged.html')


# User login


@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect('/')
    if request.method == "GET":
        return render_template('login.html', title=': Вход', fixed_footer=True)
    elif request.method == "POST":
        login = request.form["login"]
        password = request.form["u_password"]
        correct = User.query.filter(User.login == login).first()
        if correct is None:
            correct1 = User.query.filter(User.email == login).first()
            if not correct1 is None:
                correct = correct1
        if correct is None:
            error = 'Такого пользователя нет в системе'
        elif not (login and password):
            error = "Одно из полей не заполнено"
        elif not check_password_hash(correct.password, password):
            error = "Неправильный пароль"
        else:
            if correct.tid:
                send_code(correct.tid)
                session['tid'] = correct.tid
                return redirect('/oauth')
            session['username'] = correct.login
            session['user_id'] = correct.id
            session['admin'] = correct.admin
            return redirect('/')
        return render_template('login.html', title=': Вход', fixed_footer=True, error=error)


@app.route('/oauth', methods=['GET', 'POST'])
def oauth():
    if 'user_id' in session:
        return redirect('/')
    if 'tid' not in session:
        return '2FA Spoofing attempt detected.'
    if request.method == "GET":
        return render_template('oauth.html', title='2FA', fixed_footer=True)
    elif request.method == "POST":
        code = request.form["code"]
        user = User.query.filter(User.tid == session['tid']).first()
        if code != get_valid(user.tid):
            return 'Login failed.'
        session['username'] = user.login
        session['user_id'] = user.id
        session['admin'] = user.admin
        return redirect('/')

# User registration


@app.route('/registration', methods=['GET', 'POST'])
def registration():
    if request.method == "GET":
        return render_template('registration.html', title=': Регистрация', fixed_footer=True)
    elif request.method == "POST":
        login = request.form["login"]
        password = request.form["u_password"]
        password_conf = request.form["u_password_once_again"]
        email = request.form["email"]
        if not (login and password):
            error = "Одно из полей не заполнено"
        elif password != password_conf:
            error = 'Пароли не совпадают'
        elif User.query.filter(User.login == login).first():
            error = "Пользователь с таким именем уже зарегистрирован в системе. Исправьте данные"
        elif User.query.filter(User.email == email).first():
            error = "Пользователь с таким e-mail уже зарегистрирован в системе. Исправьте данные"
        else:
            if not request.form["email"]:
                email = ''
            password = generate_password_hash(password)
            user = User(password=password, login=login, email=email, admin=0)
            db.session.add(user)
            db.session.commit()
            return render_template('registration_success.html')
        return render_template('registration.html', title=': Регистрация', fixed_footer=True, error=error)


@app.route('/add-task', methods=['GET', 'POST'])
def add_task():
    if 'user_id' not in session:
        return redirect('/')
    if request.method == "GET":
        users = User.query.all()
        print(len(users))
        problem = Problem(name='Новая задача', statement='', time_end=(datetime.datetime.now() + datetime.timedelta(days=1)).strftime("%d/%m/%Y %H:%M:%S"),
                          author_id=session['user_id'], completion_stage=0)
        session['problem_id'] = problem.id
        return render_template('edit_task.html', title='Добавление задачи', problem=problem, users=users)
    elif request.method == "POST":
        name = request.form["name"]
        end_time = request.form["time_end"]
        description = request.form["description"]
        completion = request.form["completion_stage"]
        solver = request.form["solver"]
        print(solver)
        user = Problem(name=name, statement=description, time_end=end_time, author_id=session['user_id'], completion_stage=completion, solver_id=solver)
        Problem.query.filter(Problem.id == session['problem_id']).delete()
        db.session.add(user)
        session['problem_id'] = user.id
        db.session.commit()
        return redirect(f'/edit-task/{user.id}')


@app.route('/edit-task/<int:task_id>', methods=['GET', 'POST'])
def edit_task(task_id):
    if 'user_id' not in session:
        return abort(404)
    if request.method == "GET":
        problem = Problem.query.filter(Problem.id == task_id).first()
        if problem is None:
            return 'Not found :('
        if str(problem.author_id) != str(session['user_id']):
            return 'Forbidden!!'
        if problem.deleted:
            return 'Scheduled delete.'
        users = User.query.all()
        print(len(users))
        session['problem_id'] = problem.id
        return render_template('edit_task.html', title='Редактирование задачи', problem=problem, users=users)
    elif request.method == "POST":
        name = request.form["name"]
        end_time = request.form["time_end"]
        description = request.form["description"]
        completion = request.form["completion_stage"]
        solver = request.form.get('solver', session['user_id'])
        print(solver)
        user = Problem(name=name, statement=description, time_end=end_time, author_id=session['user_id'],
                       completion_stage=completion, solver_id=solver)
        Problem.query.filter(Problem.id == session['problem_id']).delete()
        db.session.add(user)
        session['problem_id'] = user.id
        db.session.commit()
        return render_template('edit_task.html', problem=user)


@app.route('/full/<int:task_id>', methods=['GET', 'POST'])
def full(task_id):
    if 'user_id' not in session:
        return abort(404)
    problem = Problem.query.filter(Problem.id == task_id).first()
    if problem is None:
        return 'Not found :('
    if str(problem.author_id) != str(session['user_id']):
        return 'Forbidden!!'
    if problem.deleted:
        return 'Scheduled delete.'
    return render_template('full_info.html', title='Информация о задаче', problem=problem)


@app.route('/del-task/<int:task_id>', methods=['GET', 'POST'])
def del_task(task_id):
    if 'user_id' not in session:
        return abort(404)
    problem = Problem.query.filter(Problem.id == task_id).first()
    if problem is None:
        return 'Not found :('
    if str(problem.id) != str(session['user_id']):
        return 'Forbidden!!'
    problem.deleted = True
    db.session.commit()
    return redirect('/')


@app.errorhandler(404)
def not_found(error):
    return render_template("error_404.html", title=": Страница не найдена", fixed_footer=True)


if __name__ == '__main__':
    app.run('127.0.0.1', port=5000, debug=True)
