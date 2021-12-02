from datetime import timedelta
from typing import Optional, Union

from fastapi import Depends, FastAPI, Form, HTTPException, Request, status
from fastapi.responses import FileResponse, JSONResponse, RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uvicorn

from src import db
import src.user_authorization as user_auth


app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


@app.get("/")
async def root():
    return FileResponse('static/index.html')


@app.get("/api/v1/get/books/")
async def get_books():
    books = db.select_existing_books()
    books = [
        {
            'title': book[0],
            'isbn13': book[1],
            'media_name': book[2],
            'own_id': book[3],
            # is_read,
            'thumbnail': book[5],
            'address': book[6],
        }
    for book in books]
    return {
        "books": books,
        "media_names": db.media_names,
        "user_names": db.user_names,
        "address_names": db.address_names,
    }


@app.post("/api/v1/get/books/byuser")
async def get_books_by_user(
    user: user_auth.UserInDB = Depends(user_auth.get_current_user),
):
    books = db.select_existing_books_with_user(user.username)
    books = [
        {
            'title': book[0],
            'isbn13': book[1],
            'media_name': book[2],
            'own_id': book[3],
            'is_read': book[4],
            'thumbnail': book[5],
            'address': book[6],
        }
    for book in books]
    return {
        "books": books,
        "user_name": user.username,
        "media_names": db.media_names,
        "user_names": db.user_names,
        "address_names": db.address_names,
    }


@app.post("/api/v1/register/book/")
def register_book(
    isbn13: str = Form(...),
    media: str = Form(...),
    owner: str = Form(...),
    address: Optional[str] = Form(...),
):
    isbn13 = isbn13.replace('-', '')
    if len(isbn13) != 13:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Invalid ISBN (use 13-digit)")
    
    try:
        db.register_book(isbn13)
        db.register_own(isbn13, media, owner, address)
    except Exception as e:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Exception throwed:" + str(e))

    return {'result': 'success'}


@app.post("/api/v1/update/read_book/")
def read_book(user_name: str = Form(...), own_id: str = Form(...), is_read: str = Form(...)):
    db.upsert_read_book(user_name, int(own_id), int(is_read))
    return {'result': 'success'}


# for user authorization
@app.post('/api/token')
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends()
) -> Union[JSONResponse, HTTPException]:
    user: Union[user_auth.UserInDB, bool] = user_auth.authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=user_auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = user_auth.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )

    return JSONResponse ({
        "access_token": access_token,
        "token_type": "bearer",
        "username": user.username,
    })


if __name__ == '__main__':
    uvicorn.run(app, debug=True, host='127.0.0.1', port=50000)
