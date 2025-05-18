from . import db, Model, Column, Integer, ForeignKey

class Stock(Model):
    __tablename__ = 'stock'
    id = Column(Integer, primary_key=True)
    producto_id = Column(Integer, ForeignKey('productos.id'), nullable=False)
    sucursal_id = Column(Integer, ForeignKey('sucursales.id'), nullable=False)
    cantidad = Column(Integer, nullable=False)