from functools import wraps
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity, decode_token
from flask import Flask, render_template, request, redirect, url_for, session, make_response
from models.user import User, Message, UserList
from flask import send_from_directory, url_for
from models.config import db
from models.database import r


app = Flask(__name__)
app.secret_key = "HBkhbkhbBHV8R8686TRVYHgvuvv8V"

# Configuración de Redis
redis_client = r

# Configuración de JWT
jwt = JWTManager(app)


# Estilos
@app.route('/static/<path:path>')
def serve_static(path):
    return send_from_directory('static', path)


@app.route('/')
def index():
    return redirect(url_for('login'))


# ----------------- RUTAS - LOGIN ----------------- #
# Decorador para requerir un token JWT en una ruta y verificar la cookie


def jwt_required_cookie(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.cookies.get('access_token')
        if not token:
            return redirect(url_for('login'))
        try:
            data = decode_token(token, app.config['JWT_SECRET_KEY'])
            current_user = db.query(User).filter_by(name=data['sub']).first()
        except:
            return redirect(url_for('login'))
        return f(current_user, *args, **kwargs)
    return decorated_function


# Función para generar el token JWT y almacenarlo en Redis
def generate_token(user_id):
    # Crear el token JWT
    access_token = create_access_token(identity=user_id)
    # Almacenar el token JWT en Redis con tiempo de expiración de 1 día
    redis_client.setex(user_id, 86400, access_token)
    return access_token

# Función para obtener el token JWT de Redis


def delete_token(user_id):
    redis_client.delete(user_id)

# Función para eliminar el token JWT de Redis


def delete_token(user_id):
    redis_client.delete(user_id.encode())

# Ruta para la página de inicio de sesión


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user_id = request.form['username']
        password = request.form['password']

        # Buscar el usuario en la base de datos
        user = db.query(User).filter_by(name=user_id, password=password).first()

        if user is not None:
            access_token = generate_token(user_id)
            # Crear respuesta con cookie que contiene el token JWT
            response = make_response(redirect(url_for('inicio')))
            response.set_cookie('access_token', access_token, httponly=True)
            return response

    return render_template('login.html')

# Ruta para cerrar sesión


@app.route('/logout', methods=['GET', 'POST'])
@jwt_required_cookie
def logout(current_user):
    # Obtener el ID del usuario y eliminar su token JWT de Redis
    user_id = current_user.name
    delete_token(user_id)
    # Eliminar la cookie que contiene el token JWT
    response = make_response(redirect('/login'))
    response.delete_cookie('access_token')
    return response

# ----------------- RUTAS - CHAT ----------------- #
@app.route('/inicio', methods=['GET', 'POST'])
@jwt_required_cookie
def inicio(current_user):
    user_list = UserList.query.all()
    users = [user_list.user for user_list in user_list]
    session['current_user'] = current_user.name
    error = None
    if request.method == "POST":
        user_id = request.form['user_id']
        user = User.query.filter_by(numero=user_id).first()

        if user:
            if not UserList.query.filter_by(user_id=user.numero).first():
                user_list = UserList(user=user)
                db.add(user_list)
                db.commit()
                users.append(user)
            else:
                error = "El ID del usuario ya existe"
        else:
            error = "El usuario no existe"

    return render_template('chat.html', current_user=current_user, users=users, error=error)


@app.route('/user/<int:user_id>/', methods=['GET', 'POST'])
def show_conversations(user_id):
    user = db.get(User, user_id)
    messages = db.query(Message).filter(Message.recipient_id == user_id)

    current_user = session.get('current_user')

    if request.method == "POST":
        message = request.form['message']
        sender_name = request.form['sender']
        recipient_name = request.form['recipient']
        sender = db.query(User).filter_by(name=sender_name).first()
        recipient = db.query(User).filter_by(name=recipient_name).first()
        message = Message(sender=sender, recipient=recipient, content=message)
        db.add(message)
        db.commit()
        return redirect(url_for('show_conversations', user_id=user_id, current_user=current_user))

    return render_template('conversations.html', current_user=current_user, user=user, messages=messages)


@app.route('/delete_chat', methods=['POST'])
def delete_chat():
    sender_name = request.form['sender']
    recipient_name = request.form['recipient']
    sender = User.query.filter_by(name=sender_name).first()
    recipient = User.query.filter_by(name=recipient_name).first()
    messages = Message.query.filter(
        (Message.sender == sender) & (Message.recipient == recipient)).all()
    for message in messages:
        db.session.delete(message)
    db.session.commit()
    return redirect(url_for('index'))


@app.route('/create_user', methods=['POST', 'GET'])
def create_user():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        number = request.form['number']
        email = request.form['email']
        user = User(name=username, password=password,
                    numero=number, correo=email)
        db.add(user)
        db.commit()
        return redirect(url_for('login'))

    return render_template('signUp.html')

@app.route('/profile')
@jwt_required_cookie
def ver_perfil(current_user):
    return render_template('profile.html', current_user=current_user)

@app.route('/delete_account', methods=['POST'])
@jwt_required_cookie
def eliminar_cuenta(current_user):
    user_id = current_user.numero
    # Eliminar mensajes del usuario
    db.query(Message).filter((Message.sender_id == user_id) | (Message.recipient_id == user_id)).delete(synchronize_session='fetch')
    # Eliminar usuario de la lista de usuarios
    db.query(UserList).filter(UserList.user_id == user_id).delete(synchronize_session='fetch')
    # Eliminar el usuario de la base de datos
    db.delete(current_user)
    db.commit()
    # Eliminar el token JWT de Redis
    delete_token(current_user.name)
    # Eliminar la cookie que contiene el token JWT y redirigir al inicio de sesión
    response = make_response(redirect('/login'))
    response.delete_cookie('access_token')
    return response

if __name__ == '__main__':
    app.run(debug=True, port=5555)
