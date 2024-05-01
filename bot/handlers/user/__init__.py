from . import callback, start, search, instruction, watch

routes = [
    start.router,
    search.router,
    instruction.router,
    callback.router,
    watch.router
]
