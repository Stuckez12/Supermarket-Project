'''
The root file to run the FastAPI user_api_gateway server v1
'''

import os
import uvicorn

from fastapi import FastAPI

from src.backend_services.common.gRPC.connection_objects import account_client

from src.backend_services.user_api_gateway.v1.routes.account.authentication import router as account_router

app = FastAPI(redirect_slashes=False)


app.state.account_grpc_client = account_client


# All routers for the gateway server
app.include_router(account_router, prefix='/api/v1/account')


if __name__ == "__main__":
    uvicorn.run(
        app,
        host=os.environ.get('CW_API_GWAY_HOST'),
        port=int(os.environ.get('CW_API_GWAY_PORT')),
        ssl_certfile=os.environ.get('CW_API_GWAY_CERT'),
        ssl_keyfile=os.environ.get('CW_API_GWAY_PKEY')
    )
