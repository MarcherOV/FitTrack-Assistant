from fastapi import FastAPI
from src.api.users import router
from src.api.training import router_training, router_training_exercises, router_sets
from src.api.exercises import router_exercise, router_category, router_type
from src.api.body import router_body, router_body_measurements

app = FastAPI()

app.include_router(router)
app.include_router(router_training)
app.include_router(router_training_exercises)
app.include_router(router_sets)
app.include_router(router_exercise)
app.include_router(router_category)
app.include_router(router_type)
app.include_router(router_body)
app.include_router(router_body_measurements)