import os
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'clave_secreta_sistema_gestion'

def get_db():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            rol TEXT DEFAULT 'admin',
            activo INTEGER DEFAULT 1
        )
    ''')
    conn.commit()
    conn.close()

# Crear tabla al iniciar
try:
    init_db()
except Exception as e:
    print("Error inicializando DB:", e)

@app.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        usuario = request.form.get('usuario')
        password = request.form.get('password')
        db = get_db()
        user = db.execute('SELECT * FROM usuarios WHERE usuario = ?', (usuario,)).fetchone()
        
        if user and check_password_hash(user['password'], password):
            session.clear()
            session['user_id'] = user['id']
            session['usuario'] = user['usuario']
            return redirect(url_for('index'))
        else:
            flash('Usuario o contraseña incorrectos', 'danger')
            return render_template('login.html')
            
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        usuario = request.form.get('usuario')
        password = request.form.get('password')
        db = get_db()
        
        if db.execute('SELECT id FROM usuarios WHERE usuario = ?', (usuario,)).fetchone():
            flash('El usuario ya existe. Intenta con otro.', 'danger')
        else:
            hashed_pw = generate_password_hash(password)
            db.execute('INSERT INTO usuarios (usuario, password, rol, activo) VALUES (?, ?, ?, ?)', (usuario, hashed_pw, 'admin', 1))
            db.commit()
            flash('¡Cuenta creada con éxito! Ahora puedes iniciar sesión.', 'success')
            return redirect(url_for('login'))
            
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)