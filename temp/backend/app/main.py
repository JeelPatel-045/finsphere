from fastapi import FastAPI
from app.api.router import api_router

app = FastAPI(title="FinSphere AI")

app.include_router(api_router)

@app.get("/")
def root():
    return {"message": "FinSphere AI Backend Running"}