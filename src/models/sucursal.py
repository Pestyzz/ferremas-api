from . import db, Model, Column, String, Integer, relationship

class Sucursal(Model):
    __tablename__ = 'sucursales'
    id = Column(Integer, primary_key=True)
    nombre = Column(String(100), nullable=False)
    direccion = Column(String(255), nullable=False)
    stocks = relationship('Stock', backref='sucursal', lazy=True)