import hashlib

from fastapi import FastAPI, Request, Response
from contextlib import asynccontextmanager
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from redis import asyncio as aioredis
from fastapi.middleware.cors import CORSMiddleware
from src.api.routers.users import router
from src.api.routers.training import router_training, router_training_exercises, router_sets
from src.api.routers.exercises import router_exercise, router_category, router_type
from src.api.routers.body import router_body, router_body_measurements
from src.api.routers.auth import router as auth_router

def custom_key_builder(
    func,
    namespace: str = "",
    request: Request = None,
    response: Response = None,
    *args,
    **kwargs,
):
    cache_kwargs = kwargs.copy()
    
    cache_kwargs.pop("session", None)
    cache_kwargs.pop("current_user", None)
    
    prefix = FastAPICache.get_prefix()
    cache_key = f"{prefix}:{namespace}:{func.__module__}:{func.__name__}:{args}:{cache_kwargs}"
    return hashlib.md5(cache_key.encode("utf-8")).hexdigest()

@asynccontextmanager
async def lifespan(app: FastAPI):
    redis = aioredis.from_url("redis://localhost:6379")
    FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache", key_builder=custom_key_builder)
    yield
    await redis.close()

app = FastAPI(title="FitTrack API", lifespan=lifespan)

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