#!/usr/bin/env python3
import pathlib
from typing import Dict, List, Optional, Union
from copy import copy


try:
    import ujson as json
except ModuleNotFoundError:
    import json  # type: ignore

JokeType = Dict[str, List[Dict[str, str]]]
JOKES: JokeType = {"default": []}


class JsonError(Exception):
    pass


def load_jokes(
    filename: Union[str, pathlib.Path], jokes: Optional[JokeType] = None
) -> JokeType:
    fl = pathlib.Path(filename)
    res_jokes: JokeType = copy(jokes) if jokes else copy(JOKES)
    if fl.exists():
        if fl.is_dir():
            for file in fl.iterdir():
                res_jokes = load_jokes(file, res_jokes)
        else:
            try:
                data = json.load(open(fl))
            except ValueError as e:
                raise JsonError(f"malformed json ({e})")

            if "jokes" not in data or type(data["jokes"]) is not list:
                raise JsonError("`jokes` must be a list of joke objects")

            category = data["category"] if "category" in data else "default"
            author = data["author"] if "author" in data else None

            for joke in data["jokes"]:
                if "text" not in joke:
                    raise JsonError("no `text` in joke object")
                if category not in res_jokes.keys():
                    res_jokes[category] = []
                res_jokes[category].append(
                    {
                        "text": joke["text"],
                        "author": author if "author" not in joke else joke["author"],
                    }
                )
    return res_jokes


if __name__ == "__main__":
    jokes = load_jokes("jokes")
    print(jokes)
