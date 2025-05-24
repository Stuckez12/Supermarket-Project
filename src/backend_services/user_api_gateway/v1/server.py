import os
import uvicorn

from fastapi import FastAPI

from src.backend_services.user_api_gateway.v1.account.routes import router as account_router

app = FastAPI(redirect_slashes=False)

collective_routes = FastAPI(deprecated=False)

# All routers for the gateway server
collective_routes.include_router(account_router, prefix='/account')

# Force app routes to start with '/api/v1' for version control
app.mount('/api/v1', collective_routes)

if __name__ == "__main__":
    uvicorn.run(
        app,
        host=os.environ.get('CW_API_GWAY_HOST'),
        port=int(os.environ.get('CW_API_GWAY_PORT')),
        ssl_certfile='localhost-cert.pem',
        ssl_keyfile='localhost-key.pem'
    )
