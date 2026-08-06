from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.api.routers.users import router
from src.api.routers.training import router_training, router_training_exercises, router_sets
from src.api.routers.exercises import router_exercise, router_category, router_type
from src.api.routers.body import router_body, router_body_measurements
from src.api.routers.auth import router as auth_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*", "https://property-nemeses-encroach.ngrok-free.dev", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)
app.include_router(router_training)
app.include_router(router_training_exercises)
app.include_router(router_sets)
app.include_router(router_exercise)
app.include_router(router_category)
app.include_router(router_type)
app.include_router(router_body)
app.include_router(router_body_measurements)
app.include_router(auth_router)