# Django Geek Monde

API REST de comercio electrónico para indumentaria y artículos geek, desarrollada en Django. Implementa modelos dinámicos para variantes de productos, manejo avanzado de stock con control de concurrencia y seguridad mediante middlewares. Proporciona una API limpia y documentada, además de un frontend moderno en Next.js.

## 📊 Composición técnica

| Lenguaje | Porcentaje |
|----------|-----------:|
| Python   | 70.4% |
| TypeScript | 13.8% |
| CSS | 8.1% |
| HTML | 7.3% |
| Otro | 0.4% |

## Características principales

- 🛍️ Catálogo de Productos: gestión de productos, categorías y variantes dinámicas
- 🛒 Carrito de Compras: sistema de carrito con modificadores de precios
- 💳 Sistema de Pagos: integración con múltiples gateways (configurable)
- 📦 Gestión de Órdenes: ciclo completo de pedidos y estados
- 📍 Envíos: cálculos de costo y tracking
- 👤 Gestión de Clientes: perfiles, direcciones y preferencias
- 📊 Inventario: control de stock con manejo de concurrencia
- 🔐 Autenticación: autenticación por email y seguridad mediante middlewares
- 📚 Documentación API: Swagger/Redoc para explorar la API
- 🌐 CMS integrado: Django CMS para contenido editorial
- 🎨 Frontend moderno: Next.js + TypeScript

## Requisitos

- Python 3.10+
- Django 4.2+
- PostgreSQL (recomendado para producción)
- Redis (opcional, para caché y colas)
- Node.js 18+ (para frontend)

## Instalación rápida

1. Clona el repositorio

```bash
git clone https://github.com/robbustamante/django-geek-monde.git
cd django-geek-monde
```

2. Crea y activa un entorno virtual

```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

3. Instala dependencias

```bash
make install
```

4. Copia y configura variables de entorno

```bash
cp .env.example .env
# Edita .env con tus valores (DATABASE_URL, SECRET_KEY, etc.)
```

5. Migraciones y superusuario

```bash
make migrate
make superuser
```

6. Ejecuta servidor de desarrollo

```bash
make run
```

El servidor estará disponible en `http://localhost:8000`.

### Frontend (opcional)

```bash
cd frontend
npm install
npm run dev
```

El frontend de desarrollo corre en `http://localhost:3000`.

## Estructura del proyecto (resumen)

```
django-geek-monde/
├── config/                    # Configuración del proyecto
├── apps/                      # Aplicaciones (catalog, cart, order, payment, etc.)
├── frontend/                  # Frontend Next.js con TypeScript
├── email_auth/                # Autenticación por email
├── templates/                 # Plantillas HTML
├── static/                    # Archivos estáticos
├── media/                     # Archivos de usuario
├── locale/                    # Traducciones
├── tests/                     # Tests del proyecto
├── manage.py
├── requirements.txt
├── .env.example
└── README.md
```

## Endpoints principales (resumen)

### Autenticación
- POST /api/auth/login/ - Login
- POST /api/auth/logout/ - Logout
- POST /api/auth/registration/ - Registro
- POST /api/auth/password/reset/ - Reset contraseña

### Catálogo
- GET /api/v1/catalog/products/ - Listar productos
- GET /api/v1/catalog/products/{id}/ - Detalle de producto
- GET /api/v1/catalog/categories/ - Listar categorías

### Carrito
- GET /api/v1/cart/ - Obtener carrito actual
- POST /api/v1/cart/items/ - Agregar item al carrito
- PATCH /api/v1/cart/items/{id}/ - Actualizar cantidad
- DELETE /api/v1/cart/items/{id}/ - Eliminar item

### Órdenes
- GET /api/v1/order/ - Listar órdenes del usuario
- POST /api/v1/order/ - Crear orden
- GET /api/v1/order/{id}/ - Detalle de orden

Para la documentación completa interactiva visite `http://localhost:8000/api/docs/swagger/`.

## Base de datos

### SQLite (desarrollo)
Por defecto usa SQLite y crea `db.sqlite3` automáticamente.

### PostgreSQL (producción)

Configurar en `.env`:

```
DATABASE_URL=postgresql://user:password@localhost:5432/geek_monde
```

Y luego:

```bash
make migrate
```

## Tests

```bash
make test
make test-cov
```

## Linting y formateo

```bash
make lint
make format
```

## Stack tecnológico

**Backend**: Django, Django REST Framework, PostgreSQL, Redis, Django CMS

**Frontend**: Next.js, TypeScript, CSS

## Contribuir

1. Fork del proyecto
2. Crea una rama para tu feature (`git checkout -b feature/mi-feature`)
3. Commit de tus cambios (`git commit -m "Add feature"`)
4. Push a tu rama (`git push origin feature/mi-feature`)
5. Abre un Pull Request

## Licencia

Proyecto bajo licencia MIT.

## Contacto

Robbustamante - [@robbustamante](https://github.com/robbustamante)

Repositorio: https://github.com/robbustamante/django-geek-monde
