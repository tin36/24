import os
import re
from flask import Flask, request, Response
from typing import Iterator

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")


def build_query(it: Iterator, cmd1: str, value1: str, cmd2: str, value2: str) -> Iterator:
    res: Iterator = map(lambda v: v.strip(), it)
    res = apply_cmd(res, cmd1, value1)
    return apply_cmd(res, cmd2, value2)


def slice_limit(it: Iterator, limit: int) -> Iterator:
    i = 0
    for item in it:
        if i < limit:
            yield item
        else:
            break
        i += 1


def apply_cmd(it: Iterator, cmd: str, value: str) -> Iterator:
    if cmd == "filter":
        return filter(lambda v: value in v, it)

    if cmd == "map":
        idx = int(value)
        return map(lambda v: v.split(" ")[idx], it)

    if cmd == "unique":
        return iter(set(it))

    if cmd == "sort":
        if value == 'desc':
            reverse = True
        else:
            reverse = False
        return iter(sorted(it, reverse=reverse))

    if cmd == "limit":
        arg = int(value)
        return slice_limit(it, arg)

    if cmd == "regex":
        regex = re.compile(value)
        return filter(lambda v: regex.search(v), it)
    return it


@app.post("/perform_query")
def perform_query() -> Response:
    file_name = request.args["file_name"]
    cmd1 = request.args["cmd1"]
    value1 = request.args["value1"]
    cmd2 = request.args["cmd2"]
    value2 = request.args["value2"]

    file_path = os.path.join(DATA_DIR, file_name)
    if not os.path.exists(file_path):
        return Response(f"{file_name} was not found")

    with open(file_path) as fd:
        res = build_query(fd, cmd1, value1, cmd2, value2)
        print(fd)
        content = '\n'.join(res)
    return app.response_class(content, content_type="text/plain")


if __name__ == '__main__':
    app.run()