#!/usr/bin/env python3

import uvicorn
from fastapi import FastAPI
from app.api.v1.endpoints.suppliers import router as suppliers_router

# Create a minimal test app
app = FastAPI()
app.include_router(suppliers_router, prefix="/suppliers")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
