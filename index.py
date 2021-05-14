#!/usr/bin/env python3

from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import Route
from jokeson import load_jokes
import random
import uvicorn

JOKES = load_jokes("jokes")


def error(err: str, code: int) -> JSONResponse:
    return JSONResponse({"error": err}, status_code=code)


async def joke_request(request):
    category = request.path_params.get("category", "oneliner")
    if category not in JOKES or not JOKES[category]:
        return error(f"category {category} not found or empty", 404)
    return JSONResponse(
        {"category": category, "content": random.choice(JOKES[category])["text"]}
    )


app = Starlette(
    debug=True, routes=[Route("/", joke_request), Route("/{category}", joke_request)]
)

if __name__ == "__main__":
    uvicorn.run("index:app", host="0.0.0.0", port=8081, log_level="info")
