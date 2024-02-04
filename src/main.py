from fastapi import FastAPI
from src.api.v1 import url_routes, users_routes


app = FastAPI()

app.include_router(url_routes.router)
app.include_router(users_routes.router)


"""
@app.get("/")
def read_root():
    return "Welcome to the URL shortener API :)"


@app.post("/url", response_model=schemas.URLInfo)
def create_url(url: schemas.URLBase, db: Session = Depends(get_db)):
    if not validators.url(url.target_url):
        raise_bad_request(message="Your provided URL is not valid")

    db_url = create_db_url(db=db, url=url)

    return get_admin_info(db_url)


@app.get("/{url_key}")
def forward_to_target_url(url_key: str, request: Request, db: Session = Depends(get_db)):
    if db_url := get_db_url_by_key(db=db, url_key=url_key):
        update_db_clicks(db=db, db_url=db_url)
        return RedirectResponse(db_url.target_url)
    else:
        raise_not_found(request)


@app.get("/admin/{secret_key}", name="administration info", response_model=schemas.URLInfo)
def get_url_info(secret_key: str, request: Request, db: Session = Depends(get_db)):
    if db_url := get_db_url_by_secret_key(db, secret_key=secret_key):
        return get_admin_info(db_url)
    else:
        raise_not_found(request)


@app.delete("/admin/{secret_key}")
def delete_url(secret_key: str, request: Request, db: Session = Depends(get_db)):
    if db_url := deactivate_db_url_by_secret_key(db, secret_key=secret_key):
        message = f"Successfully deleted shortened URL for " f"'{db_url.target_url}'"
        return {"detail": message}
    else:
        raise_not_found(request)
"""
