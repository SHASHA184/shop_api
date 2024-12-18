from fastapi import FastAPI
from app.routers import products, categories, users, orders, reservations, auth
import uvicorn

app = FastAPI()

app.include_router(products.router, prefix="/api", tags=["products"])
app.include_router(categories.router, prefix="/api", tags=["categories"])
app.include_router(orders.router, prefix="/api", tags=["orders"])
app.include_router(users.router, prefix="/api", tags=["users"])
app.include_router(reservations.router, prefix="/api", tags=["reservations"])
app.include_router(auth.router, tags=["auth"])


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8003)