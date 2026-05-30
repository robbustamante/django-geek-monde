# Django Geek Monde

API REST de comercio electrónico para indumentaria y artículos geek, desarrollada en Django. Implementa modelos dinámicos para variantes de productos, manejo avanzado de stock con control de concurrencia y seguridad mediante middlewares.

## Características

- 🛍️ **Catálogo de Productos** - Gestión completa de productos, categorías y variantes
- 🛒 **Carrito de Compras** - Sistema de carrito con modificadores de precios
- 💳 **Sistema de Pagos** - Integración con múltiples métodos de pago
- 📦 **Gestión de Órdenes** - Seguimiento completo del ciclo de vida de pedidos
- 📍 **Gestión de Envíos** - Cálculo de costos y tracking
- 👤 **Gestión de Clientes** - Perfiles, direcciones y preferencias
- 📊 **Inventario** - Control de stock con manejo de concurrencia
- 🔐 **Autenticación** - Sistema de autenticación basado en email
- 📚 **API Documentation** - Documentación interactiva con Swagger/Redoc
- 🌐 **CMS integrado** - Django CMS para contenido editorial

## Requisitos

- Python 3.10+
- Django 4.2+
- PostgreSQL (recomendado para producción)
- Redis (opcional, para caché)

## Instalación

### 1. Clonar el repositorio

```bash
git clone https://github.com/robbustamante/django-geek-monde.git
cd django-geek-monde
```

### 2. Crear entorno virtual

```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

### 3. Instalar dependencias

```bash
make install
```

### 4. Configurar variables de entorno

```bash
cp .env.example .env
# Editar .env con tus valores
```

### 5. Crear base de datos

```bash
make migrate
```

### 6. Crear superusuario

```bash
make superuser
```

### 7. Ejecutar servidor de desarrollo

```bash
make run
```

El servidor estará disponible en `http://localhost:8000`

## Estructura del Proyecto

```
django-geek-monde/
├── config/                    # Configuración del proyecto
│   ├── settings/
│   │   ├── base.py           # Configuración base
│   │   ├── development.py    # Configuración desarrollo
│   │   └── production.py     # Configuración producción
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── apps/                      # Aplicaciones del proyecto
│   ├── core/                 # Funcionalidades centrales
│   ├── catalog/              # Gestión de productos
│   ├── cart/                 # Carrito de compras
│   ├── order/                # Órdenes
│   ├── payment/              # Pagos
│   ├── shipping/             # Envíos
│   ├── customer/             # Clientes
│   └── inventory/            # Inventario
├── email_auth/               # Autenticación por email
├── templates/                # Plantillas HTML
├── static/                   # Archivos estáticos
├── media/                    # Archivos de usuario
├── locale/                   # Traduciones
├── tests/                    # Tests del proyecto
├── manage.py
├── pytest.ini
├── requirements.txt
├── .env.example
├── Makefile
└── README.md
```

## API Endpoints

### Autenticación
- `POST /api/auth/login/` - Login
- `POST /api/auth/logout/` - Logout
- `POST /api/auth/registration/` - Registro
- `POST /api/auth/password/reset/` - Reset contraseña

### Catálogo
- `GET /api/v1/catalog/products/` - Listar productos
- `GET /api/v1/catalog/products/{id}/` - Detalle de producto
- `GET /api/v1/catalog/categories/` - Listar categorías

### Carrito
- `GET /api/v1/cart/` - Obtener carrito actual
- `POST /api/v1/cart/items/` - Agregar item al carrito
- `PATCH /api/v1/cart/items/{id}/` - Actualizar cantidad
- `DELETE /api/v1/cart/items/{id}/` - Eliminar item

### Órdenes
- `GET /api/v1/order/` - Listar órdenes del usuario
- `POST /api/v1/order/` - Crear orden
- `GET /api/v1/order/{id}/` - Detalle de orden

### Documentación completa
Visita `http://localhost:8000/api/docs/swagger/` para la documentación interactiva.

## Configuración de Base de Datos

### SQLite (Desarrollo)
Por defecto usa SQLite. Se crea automáticamente en `db.sqlite3`

### PostgreSQL (Producción)

Instala PostgreSQL y actualiza `.env`:

```
DATABASE_URL=postgresql://user:password@localhost:5432/geek_monde
```

Luego:
```bash
make migrate
```

## Testing

```bash
# Ejecutar todos los tests
make test

# Con cobertura
make test-cov
```

## Linting y Formateo

```bash
# Verificar lint
make lint

# Formatear código
make format
```

## Documentación

- [Django Documentation](https://docs.djangoproject.com/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [Django CMS](https://docs.django-cms.org/)

## Contribuir

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## Licencia

Este proyecto está bajo licencia MIT.

## Contacto

Robbustamante - [@robbustamante](https://github.com/robbustamante)

Proyecto Link: [https://github.com/robbustamante/django-geek-monde](https://github.com/robbustamante/django-geek-monde)
