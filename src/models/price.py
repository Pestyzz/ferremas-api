from . import db
from datetime import datetime

class Precio(db.Model):
    __tablename__ = 'precios'
    
    id = db.Column(db.Integer, primary_key=True)
    fecha = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    valor = db.Column(db.Float, nullable=False)
    producto_id = db.Column(db.Integer, db.ForeignKey('productos.id'), nullable=False)
    
    def __repr__(self):
        return f'<Precio {self.valor} - {self.fecha}>'