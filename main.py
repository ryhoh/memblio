from fastapi import FastAPI, Form, HTTPException, Request, status
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uvicorn

from src import db


app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


@app.get("/")
async def root(request: Request):
    return templates.TemplateResponse("index.html", {
        "request": request,
        "books": db.select_existing_books(),
        "user_name": None,
        "media_names": db.media_names,
        "user_names": db.user_names,
    })


@app.get("/{user_name}")
async def root(request: Request, user_name: str):
    return templates.TemplateResponse("index.html", {
        "request": request,
        "books": db.select_existing_books_with_user(user_name),
        "user_name": user_name,
        "media_names": db.media_names,
        "user_names": db.user_names,
    })


@app.post("/api/v1/register/book/")
def register_book(isbn13: str = Form(...), media: str = Form(...), owner: str = Form(...)):
    isbn13 = isbn13.replace('-', '')
    if len(isbn13) != 13:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Invalid ISBN (use 13-digit)")
    
    try:
        db.register_book(isbn13)
        db.register_own(isbn13, media, owner)
    except Exception as e:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Exception throwed:", e)

    return RedirectResponse('/', status.HTTP_301_MOVED_PERMANENTLY)


@app.post("/api/v1/update/read_book/")
def register_book(user_name: str = Form(...), own_id: str = Form(...), is_read: str = Form(...)):
    db.upsert_read_book(user_name, int(own_id), bool(int(is_read)))
    return RedirectResponse('/%s' % user_name, status.HTTP_301_MOVED_PERMANENTLY)


if __name__ == '__main__':
    uvicorn.run(app, debug=True, host='127.0.0.1', port=50000)
