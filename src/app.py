from flask import Flask
from models import db
from routes.products import products_bp
from routes.branches import branches_bp

app = Flask(__name__)

#Configuración de la base de datos
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///ferreteria.db"  # Usamos SQLite para simplicidad
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

#Inicializa la instancia de SQLAlchemy
db.init_app(app)

#Registra los Blueprints
app.register_blueprint(products_bp)
app.register_blueprint(branches_bp)

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)