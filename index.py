#!/usr/bin/env python3

from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import Route
from jokeson import load_jokes
import random
import uvicorn  # type: ignore

JOKES = load_jokes("jokes")
for category in JOKES:
    random.shuffle(JOKES[category]) 


def error(err: str, code: int) -> JSONResponse:
    return JSONResponse({"error": err}, status_code=code)


async def joke_request(request):
    category = request.path_params.get("category", "oneliner")
    if category not in JOKES:
        return error(f"category {category} not found", 404)
    if not JOKES[category]:
        TEMP_JOKES = load_jokes("jokes")
        random.shuffle(TEMP_JOKES[category])
        JOKES[category] = TEMP_JOKES[category]
        del TEMP_JOKES
    return JSONResponse(
        {"category": category, "content": (JOKES[category].pop())["text"]}
    )


async def categories_request(request):
    categories = list(JOKES.keys())
    del categories[0]
    return JSONResponse(categories)


app = Starlette(
    debug=True,
    routes=[
        Route("/", joke_request),
        Route("/categories", categories_request),
        Route("/{category}", joke_request),
    ],
)

if __name__ == "__main__":
    uvicorn.run("index:app", host="0.0.0.0", port=8081, log_level="info")
