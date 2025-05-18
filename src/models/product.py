from . import db, Model, Column, String, Integer, relationship

class Producto(Model):
    __tablename__ = 'productos'
    id = Column(Integer, primary_key=True)
    codigo_producto = Column(String(50), unique=True, nullable=False)
    marca = Column(String(100), nullable=False)
    codigo = Column(String(50), unique=True, nullable=False)
    nombre = Column(String(100), nullable=False)
    precios = relationship('Precio', backref='producto', lazy=True)
    stocks = relationship('Stock', backref='producto', lazy=True)