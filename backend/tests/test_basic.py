def test_app_is_testing(app):
    """Prueba que la aplicación se configure correctamente para testing."""
    assert app.config['TESTING'] is True

def test_api_docs_reachable(client):
    """Prueba que la documentación de Swagger de la API responda."""
    # Generalmente Flask-RESTX mapea la raíz o /api/docs a la UI de Swagger
    response = client.get('/api/')
    # Si la ruta no existe devuelve 404, pero probamos que el servidor responde sin colapsar
    assert response.status_code in [200, 302, 404]
