from fastapi import FastAPI, Security
from fastapi.middleware.cors import CORSMiddleware

# from src.routers.userRouter import router as userRouter  
from src.routes.payment.create import router as payment_router

app = FastAPI()

# app.include_router(userRouter)  
app.include_router(payment_router)

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