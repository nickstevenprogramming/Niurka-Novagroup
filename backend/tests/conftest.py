import os
import pytest
from app import create_app
from app.extensions import db

@pytest.fixture
def app():
    """Fixture para crear la aplicación en modo de pruebas."""
    os.environ['FLASK_ENV'] = 'testing'
    
    # Creamos la aplicación (asegúrate de tener un entorno "testing" en config.py)
    app = create_app('testing')
    
    # Usamos una base de datos en memoria para los tests o conectamos a una DB de test
    app.config.update({
        "TESTING": True,
        # Si config.py no define una DB de testing, podríamos forzar SQLite en memoria aquí:
        # "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:"
    })

    with app.app_context():
        # Aquí podrías ejecutar db.create_all() si usas SQLite en memoria
        yield app
        # Y luego db.drop_all()

@pytest.fixture
def client(app):
    """Fixture para obtener un cliente de pruebas de Flask."""
    return app.test_client()
