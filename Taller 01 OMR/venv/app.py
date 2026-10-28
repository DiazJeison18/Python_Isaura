from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = Flask(__name__)

# 1. CONFIGURACIÓN DE LA BASE DE DATOS (MIGRADO A MYSQL)
USER_DB = 'root'        # Cambia por tu usuario de MySQL
PASS_DB = ''  # Cambia por tu contraseña de MySQL
URL_DB = 'localhost'
NAME_DB = 'flask_sqlalchemy'

# Usamos el driver mysql+pymysql para una conexión segura y limpia
FULL_URL_DB = f'mysql+pymysql://{USER_DB}:{PASS_DB}@{URL_DB}/{NAME_DB}'

app.config['SQLALCHEMY_DATABASE_URI'] = FULL_URL_DB
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicialización de extensiones
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# 2. DEFINICIÓN DEL MODELO (CORREGIDO Y OPTIMIZADO)
class Person(db.Model):
    __tablename__ = 'person'

    # Definimos el ID como llave primaria autoincrementable nativa en MySQL
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(250), nullable=True)
    apellido = db.Column(db.String(250), nullable=True)
    correo = db.Column(db.String(250), nullable=True)

    # Corrección del constructor original: en Python es __init__ (no __int__)
    def __init__(self, nombre, apellido, correo, id=None):
        if id is not None:
            self.id = id
        self.nombre = nombre
        self.apellido = apellido
        self.correo = correo

    def json(self):
        return {'id': self.id, 'nombre': self.nombre, 'apellido': self.apellido, 'correo': self.correo}

    def __str__(self):
        return f"Person(id={self.id}, nombre={self.nombre}, apellido={self.apellido}, correo={self.correo})"

    # 3. MANEJO DE RUTAS Y API REST (CORREGIDO PARA EVITAR ERRORES DE SESIÓN)
@app.route("/api/")
def home():
    app.logger.info(f'Solicitud en la ruta {request.path}')
    return "<p>API del proyecto de persona en MySQL</p>"

# 2.1 Listar los registros de la tabla person
@app.get("/api/project/person/")
def getListPerson():
    app.logger.info(f'Solicitud en la ruta {request.path}')
    persons = Person.query.all()
    listPerson = [persona.json() for persona in persons]
    return jsonify(listPerson)

# 2.2 Listar una persona por id
@app.get("/api/project/person/<int:idPersona>")
def getPersonById(idPersona):
    app.logger.info(f'Solicitud en la ruta {request.path}')
    person = Person.query.filter_by(id=idPersona).first()
    if not person:
        return jsonify({"error": "Persona no encontrada"}), 404
    return jsonify(person.json())

# 2.3 Crear una persona
@app.post("/api/project/person/")
def createPerson():
    app.logger.info(f'Solicitud en la ruta {request.path}')
    data = request.get_json()

    # Nota: Si el id viene en 0 o vacío, no se lo pasamos al modelo
    # para dejar que MySQL asigne el autoincremental de forma correcta.
    if data.get('id') == 0 or 'id' not in data:
        person = Person(nombre=data['nombre'], apellido=data['apellido'], correo=data['correo'])
    else:
        person = Person(id=data['id'], nombre=data['nombre'], apellido=data['apellido'], correo=data['correo'])

    db.session.add(person)
    db.session.commit()

    # Retornamos el objeto tal como quedó guardado con su ID real generado
    return jsonify(person.json()), 201

# 2.4 Actualizar una persona
@app.put("/api/project/person/<int:idPersona>")
def updatePerson(idPersona):
    app.logger.info(f'Solicitud en la ruta {request.path}')
    data = request.get_json()

    personUpdate = Person.query.filter_by(id=idPersona).first()
    if not personUpdate:
        return jsonify({"error": "Persona no encontrada"}), 404

    personUpdate.nombre = data['nombre']
    personUpdate.apellido = data['apellido']
    personUpdate.correo = data['correo']

    db.session.commit()
    return jsonify(personUpdate.json())

# 2.5 Eliminar una persona
@app.delete("/api/project/person/<int:idPersona>")
def deletePerson(idPersona):
    app.logger.info(f'Solicitud en la ruta {request.path}')
    personDelete = Person.query.filter_by(id=idPersona).first()
    if not personDelete:
        return jsonify({"error": "Persona no encontrada"}), 404

    person_data = personDelete.json()
    db.session.delete(personDelete)
    db.session.commit()
    return jsonify(person_data)