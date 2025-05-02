from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.routes import budget

# from src.routers.userRouter import router as userRouter  

app = FastAPI()

app.include_router(budget.router) 

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "API is running"}