import uvicorn
from fastapi import FastAPI
from contextlib import asynccontextmanager
from strawberry.fastapi import GraphQLRouter
from schema import schema
from fastapi.middleware.cors import CORSMiddleware

graphql_app = GraphQLRouter(schema)

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Démarrage de GraphSQL...")
    yield
    print("Arrêt du serveur GraphSQL")

app = FastAPI(lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(graphql_app, prefix="/graphql")

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8001, reload=True)