from fastapi import HTTPException

def raise_bad_request(message: str):
    raise HTTPException(status_code=400, detail=message)

def raise_not_found(request_url: str):
    message = f"URL '{request_url}' doesn't exist"
    raise HTTPException(status_code=404, detail=message)
