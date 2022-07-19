# Project «API for Yatube»

## Yandex Practicum. Python backend developer.

### About Yatube:
Yatube — is a social network. Users write, read and comment on articles. It is possible to subscribe to your favorite author. Mechanisms for registration, authentication, reset and password recovery are implemented.


### Description of the API project:
API Yatube was created to interact with the main functions of the service:

1. user authentication - getting / creating / changing / deleting publications
2. getting / creating / changing / deleting comments
3. subscription to the author

#### Request examples:
Receive list of the posts:
```
GET http://127.0.0.1:8000/api/v1/posts/
content-type: application/json
```

Create post:
```
GET http://127.0.0.1:8000/api/v1/posts/
content-type: application/json
Authorization: Bearer <токен>
```

Receive JWT-token:

```

POST http://127.0.0.1:8000/api/jwt/create/
content-type: application/json

{
    "username": "<login>",
    "password": "<password>"
}
```
A detailed list of all requests and examples of answers in the terms of reference (see below)

### Specification:
http://127.0.0.1:8000/redoc
* p.s. The link is active only when the local server is running. Start instructions below.

### Used technologies:
* Django REST Framework
* Simple-JWT

### How to start the project:
Clone repository:

```
git clone <link>
```
Create and activate virtual environment:
```
python -m venv env
```

Install requirements from requirements.txt:
```
python -m pip install --upgrade pip
pip install -r requirements.txt
```
Run migrations:
```
python manage.py migrate
```
Run local server:
```
python manage.py runserver
```
Dmitrii Kirsanov
