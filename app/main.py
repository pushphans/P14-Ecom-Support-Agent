from fastapi import FastAPI
from app.api.router import router

# Create FastAPI app instance
app = FastAPI(title="Ecom Support Agent API", version="0.1.0")

# Include the router
app.include_router(router)

if __name__ == "__main__":
    print("Hello from p14-ecom-support-agent!")
