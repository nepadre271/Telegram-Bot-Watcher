from . import callback, start, search, instruction

routes = [
    start.router,
    instruction.router,
    search.router,
    callback.router,
]
