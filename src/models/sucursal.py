from . import db

class Sucursal(db.Model):
    __tablename__ = 'sucursales'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    direccion = db.Column(db.String(255), nullable=False)
    
    # Relaciones
    stocks = db.relationship('Stock', backref='sucursal', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Sucursal {self.nombre} - {self.direccion}>'