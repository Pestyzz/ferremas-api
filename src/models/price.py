from . import db, Model, Column, Integer, Float, DateTime, ForeignKey

class Precio(Model):
    __tablename__ = 'precios'
    id = Column(Integer, primary_key=True)
    fecha = Column(DateTime, nullable=False)
    valor = Column(Float, nullable=False)
    producto_id = Column(Integer, ForeignKey('productos.id'), nullable=False)