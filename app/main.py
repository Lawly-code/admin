from flask import Flask, request, redirect, url_for, render_template_string, session
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin, AdminIndexView, expose
from flask_admin.contrib.sqla import ModelView
import os

db_host = os.getenv('db_host')
db_port = os.getenv('db_port')
db_name = os.getenv('db_name')
db_login = os.getenv('db_login')
db_password = os.getenv('db_password')

DATABASE_URL = f"postgresql://{db_login}:{db_password}@{db_host}:{db_port}/{db_name}"


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'supersecretkey')

db = SQLAlchemy(app)

# =====================
# Авторизация
# =====================
ADMIN_USERNAME = os.getenv('ADMIN_USERNAME', 'admin')
ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', 'admin')

def is_logged_in():
    return session.get('logged_in')

# =====================
# Кастомная страница админки
# =====================
class MyAdminIndexView(AdminIndexView):
    @expose('/')
    def index(self):
        if not is_logged_in():
            return redirect(url_for('login'))
        return super(MyAdminIndexView, self).index()

class BaseAdmin(ModelView):
    def is_accessible(self):
        return is_logged_in()

# =====================
# Страница логина
# =====================
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if (request.form.get('username') == ADMIN_USERNAME and
                request.form.get('password') == ADMIN_PASSWORD):
            session['logged_in'] = True
            return redirect('/admin')
        return render_template_string(LOGIN_PAGE_HTML, error="Неверный логин или пароль")
    return render_template_string(LOGIN_PAGE_HTML)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect('/login')

# Простейший HTML шаблон логина
LOGIN_PAGE_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Login</title>
</head>
<body>
    <h2>Login</h2>
    {% if error %}
    <p style="color:red;">{{ error }}</p>
    {% endif %}
    <form method="post">
        <label>Username:</label><br>
        <input type="text" name="username"><br><br>
        <label>Password:</label><br>
        <input type="password" name="password"><br><br>
        <input type="submit" value="Login">
    </form>
</body>
</html>
"""

# =====================
# Импорт моделей
# =====================
from lawly_db.db_models import (
    Document,
    DocumentCreation,
    DocumentReview,
    Field,
    Lawyer,
    LawyerRequest,
    Message,
    Payment,
    RefreshSession,
    Subscribe,
    Tariff,
    Template,
    User
)

# =====================
# Инициализация Flask-Admin
# =====================
admin = Admin(app, name='Admin Panel', template_mode='bootstrap4', index_view=MyAdminIndexView())

# =====================
# Регистрация моделей
# =====================
admin.add_view(BaseAdmin(Document, db.session))
admin.add_view(BaseAdmin(DocumentCreation, db.session))
admin.add_view(BaseAdmin(DocumentReview, db.session))
admin.add_view(BaseAdmin(Field, db.session))
admin.add_view(BaseAdmin(Lawyer, db.session))
admin.add_view(BaseAdmin(LawyerRequest, db.session))
admin.add_view(BaseAdmin(Message, db.session))
admin.add_view(BaseAdmin(Payment, db.session))
admin.add_view(BaseAdmin(RefreshSession, db.session))
admin.add_view(BaseAdmin(Subscribe, db.session))
admin.add_view(BaseAdmin(Tariff, db.session))
admin.add_view(BaseAdmin(Template, db.session))
admin.add_view(BaseAdmin(User, db.session))

# =====================
# Точка входа
# =====================
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5051)