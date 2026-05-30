# Django Geek Monde API Documentation

## Base URL

```
http://localhost:8000/api/v1/
```

## Authentication

The API uses token-based authentication. Include your token in the Authorization header:

```
Authorization: Token YOUR_TOKEN_HERE
```

## Endpoints

### Products

#### List Products
```
GET /catalog/products/
```

#### Get Product Details
```
GET /catalog/products/{id}/
```

### Cart

#### Get Current Cart
```
GET /cart/
```

#### Add Item to Cart
```
POST /cart/items/
```

### Orders

#### List Orders
```
GET /order/
```

#### Create Order
```
POST /order/
```

## Error Handling

The API returns standard HTTP status codes:

- `200 OK` - Request successful
- `201 Created` - Resource created
- `400 Bad Request` - Invalid request
- `401 Unauthorized` - Authentication required
- `404 Not Found` - Resource not found
- `500 Internal Server Error` - Server error
