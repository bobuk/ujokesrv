import json
import random
import time

from spin_http import Response
from parsed import JOKES


def resp(text: dict | list, code: int = 200) -> Response:
    return Response(
        code,
        {"content-type": "application/json; charset=utf-8"},
        bytes(json.dumps(text, ensure_ascii=False), "utf-8"),
    )


def error(err: str, code: int) -> Response:
    return resp({"error": err}, code)


def joke_request(category):
    return {
        "category": category,
        "content": random.choice(JOKES[category])["text"],
        # "size": len(JOKES[category]),
    }


def categories_request():
    categories = list(JOKES.keys())
    del categories[0]
    return categories


categories = categories_request()


def handle_request(request) -> Response:
    random.seed(int(time.time() * 1000))
    uri = request.uri[1:] if request.uri.startswith("/") else request.uri
    if "?" in uri:
        uri = uri.split("?")[0]
    if uri == "categories":
        return resp(categories, 200)
    if uri in categories:
        return resp(joke_request(uri), 200)
    elif len(uri) > 0:
        return error(f"database {uri} is not found (yet)", 404)
    return resp(joke_request("oneliner"), 200)
