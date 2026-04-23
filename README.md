# Sistema de Reservas · Hotel Anacaona & Spa

Este es el backend para el sistema de reservas y gestión del Hotel Anacaona & Spa, desarrollado con **Flask** y **MySQL**. Incluye una API RESTful completa con JWT, envío de correos, autenticación basada en roles, y manejo de múltiples módulos (Habitaciones, Huéspedes, Reservas, Empleados, Restaurante, Spa, etc.).

## 📋 Requisitos

* **Python 3.10+**
* **MySQL 8.0+**

## 🚀 Instalación y Configuración

Sigue estos pasos para levantar el proyecto de forma local:

### 1. Clonar el repositorio
```bash
git clone https://github.com/nickstevenprogramming/Niurka-Novagroup.git
cd Niurka-Novagroup
```

### 2. Importar la Base de Datos
En la raíz del proyecto, encontrarás el archivo `hotel_sistema_completo.sql`. Debes importarlo en tu servidor MySQL local para crear las tablas, relaciones y datos de prueba.
```bash
mysql -u root -p < hotel_sistema_completo.sql
```

### 3. Configurar el entorno virtual
Es recomendable usar un entorno virtual para las dependencias de Python.
```bash
cd backend
python -m venv venv
```
Activa el entorno virtual:
* **Windows**: `venv\Scripts\activate`
* **macOS / Linux**: `source venv/bin/activate`

### 4. Instalar las dependencias
```bash
pip install -r requirements.txt
```

### 5. Configurar las Variables de Entorno
Copia el archivo `.env.example` y renómbralo a `.env`.
```bash
cp .env.example .env
```
Luego, edita el archivo `.env` y asegúrate de configurar correctamente:
* Credenciales de acceso a MySQL (`DB_USER`, `DB_PASSWORD`, `DB_NAME`, etc.)
* Semilla secreta de JWT (`JWT_SECRET_KEY`)
* Credenciales de Gmail (App Password) para los envíos de correo.

### 6. Ejecutar el Servidor
Levanta el servidor local de desarrollo con:
```bash
python run.py
```
Por defecto, la API estará disponible en: `http://localhost:5000/` y la documentación de Swagger en `http://localhost:5000/api/docs`.

## 🧪 Pruebas (Testing)

El proyecto incluye pruebas unitarias implementadas con `pytest`.
Para ejecutar los tests, asegúrate de tener tu entorno virtual activo y ejecuta:
```bash
pytest
```
