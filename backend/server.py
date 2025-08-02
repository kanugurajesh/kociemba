import os
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from cube_engine import polyhedron_api_router

# Renamed variables
api_gateway = FastAPI()

# Renamed variables
deployment_profile = os.getenv("ENV", "development")
if deployment_profile == "production":
    allowed_origins = ["https://irisxu.me/rubik"]
else:
    allowed_origins = ["http://127.0.0.1:5500"]

# Using renamed variables
api_gateway.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Using renamed router
api_gateway.include_router(polyhedron_api_router)

if __name__ == "__main__":
    server_port = int(os.getenv("PORT", "8080"))
    
    # Using renamed variable
    if deployment_profile == "production":
        uvicorn.run("server:api_gateway", host="0.0.0.0", port=server_port, workers=1)
    else:
        uvicorn.run("server:api_gateway", host="127.0.0.1", port=server_port, reload=True)