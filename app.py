from flask import Flask, request, redirect, url_for, render_template, flash, session
import os
import sqlite3
from werkzeug.utils import secure_filename
from functools import wraps
from datetime import timedelta  

app = Flask(__name__)
app.secret_key = 'supersecretkey'
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Configuración de expiración de sesión al cerrar el navegador
app.config['SESSION_COOKIE_NAME'] = 'flask_session'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=20)

# Función para inicializar la base de datos
def init_db():
    with sqlite3.connect('database.db') as conn:
        c = conn.cursor()
        c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
        ''')
        c.execute('''
        CREATE TABLE IF NOT EXISTS files (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL,
            filepath TEXT NOT NULL,
            folder TEXT NOT NULL
        )
        ''')
        conn.commit()

init_db()

# verificar si el usuario ha iniciado sesión
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            flash('Debes iniciar sesión para acceder a esta página.', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Ruta para la página de inicio
@app.route('/')
def index():
    return render_template('index.html')

# Ruta para mostrar archivos de una carpeta específica
@app.route('/folder/<folder_name>')
 
# Proteger esta ruta
def folder(folder_name):
    with sqlite3.connect('database.db') as conn:
        c = conn.cursor()
        c.execute("SELECT * FROM files WHERE folder=?", (folder_name,))
        files = c.fetchall()
    return render_template('folder.html', files=files, folder_name=folder_name)

# Ruta para la página de login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        with sqlite3.connect('database.db') as conn:
            c = conn.cursor()
            c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
            user = c.fetchone()
        if user:
            session['logged_in'] = True  # Iniciar sesión correctamente
            session.permanent = True  # Marcar la sesión como permanente (expirará al cerrar el navegador)
            flash('Inicio de sesión exitoso!', 'success')
            return redirect(url_for('upload'))
        else:
            flash('Credenciales incorrectas. Inténtalo de nuevo.', 'error')
    return render_template('login.html')

# Ruta para cerrar sesión manualmente
@app.route('/logout', methods=['POST'])
def logout():
    session.clear()  # Limpiar toda la sesión
    flash('¡Has cerrado sesión correctamente!', 'info')
    return redirect(url_for('index'))

# Ruta para la subida de archivos (protegida por login_required)
@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    if request.method == 'POST':
        folder = request.form['folder']
        file = request.files['file']
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], folder, filename)
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        file.save(filepath)
        with sqlite3.connect('database.db') as conn:
            c = conn.cursor()
            c.execute("INSERT INTO files (filename, filepath, folder) VALUES (?, ?, ?)", (filename, filepath, folder))
            conn.commit()
        flash('Archivo subido correctamente.', 'success')
    return render_template('upload.html')

# Ruta para servir archivos subidos
@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
