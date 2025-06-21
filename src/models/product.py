from . import db
from sqlalchemy import Column, Integer, String

class Producto(db.Model):
    __tablename__ = 'productos'
    
    id = db.Column(db.Integer, primary_key=True)
    codigo_producto = db.Column(db.String(50), unique=True, nullable=False)
    marca = db.Column(db.String(100), nullable=False)
    codigo = db.Column(db.String(50), unique=True, nullable=False)
    nombre = db.Column(db.String(100), nullable=False)
    
    # Relaciones
    precios = db.relationship('Precio', backref='producto', lazy=True, cascade='all, delete-orphan')
    stocks = db.relationship('Stock', backref='producto', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Producto {self.codigo} - {self.nombre}>'