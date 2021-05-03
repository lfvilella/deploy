import uuid
import logging

import uvicorn
import fastapi
import pydantic

from google.cloud import storage
from google.cloud import firestore
from google.cloud import ndb


#############
# DataStore #
#############
class Author(ndb.Model):
    name = ndb.StringProperty()
    age = ndb.IntegerProperty()


class Book(ndb.Model):
    title = ndb.StringProperty()
    pages = ndb.IntegerProperty()
    author = ndb.KeyProperty(kind=Author)


class User(ndb.Model):
    name = ndb.StringProperty()
    hashed_password = ndb.StringProperty()


class APIKey(ndb.Model):
    token = ndb.StringProperty()
    user = ndb.KeyProperty(kind=User)


###########
# Schemas #
###########
class UserSchema(pydantic.BaseModel):
    name: str


class UserCreateSchema(UserSchema):
    password: str


class Authenticate(pydantic.BaseModel):
    user: UserSchema
    password: str


#######
# API #
#######
app = fastapi.FastAPI()


def _get_api_key_from_request(request: fastapi.Request):
    return request.query_params.get('api_key') or request.cookies.get(
        'api_key'
    )


@app.post('/signup', status_code=201)
def create_user(user: UserCreateSchema):
    user = UserCreateSchema(**user.dict())
    with ndb.Client().context():
        User(
            id=str(uuid.uuid4()),
            name=user.name,
            hashed_password=user.password,  # TODO: use secrets to hash it
        ).put()
        return {'detail': 'User created'}


@app.post('/login')
def login(response: fastapi.Response, auth: Authenticate):
    auth = Authenticate(**auth.dict())
    with ndb.Client().context():
        user = User.query(User.name == auth.user.name).get()
        if not user:
            return {'error': 'User not found'}

        if user.hashed_password != auth.password:
            return {'error': 'Invalid password'}

        api_key = APIKey.query(APIKey.user == user.key).get()
        if not api_key:
            api_key = APIKey(token=str(uuid.uuid4()), user=user.key)
            api_key.put()

        _token = api_key.token
        # response.set_cookie(key='api_key', value=_token)

        return {
            'result': 'User logged',
            'token': _token,
            'details': api_key.to_dict(),
        }


@app.delete('/logout', status_code=204)
def logout(request: fastapi.Request):
    api_key = _get_api_key_from_request(request)
    # TODO: Check this api_key
    with ndb.Client().context():
        api_key = APIKey.query(APIKey.token == api_key).get()
        if not api_key:
            return {'error': 'Token invalid'}

        APIKey.query(APIKey.user == api_key.user.key).delete()
        return {}


@app.get('/tokens')
def list_tokens():
    with ndb.Client().context():
        tokens = [token.to_dict() for token in APIKey.query().fetch()]
        return tokens


@app.get('/users')
def list_users():
    with ndb.Client().context():
        users = [user.to_dict() for user in User.query().fetch()]
        return users


@app.get('/')
def read_root():
    return {'Hello': 'World'}


@app.get('/raise')
def raises():
    raise ValueError('Testing error :/')
    return {'Hello': 'World'}


@app.get('/ndb')
def ndb_handler():
    logging.info('acessando ndb')
    with ndb.Client().context():
        Author(id=53, name='juca',).put()
        author = Author.query(Author.name == 'juca').get()
        Book(title=str(uuid.uuid4()), author=author.key).put()
        books = Book.query(Book.author == author.key).fetch()
        rvalue = author.to_dict()
        rvalue['books'] = [b.to_dict() for b in books]
        return f'{rvalue}'


if __name__ == '__main__':
    uvicorn.run(app, host='127.0.0.1', port=8080)
