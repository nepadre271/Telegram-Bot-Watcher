from . import callback, start, search, instruction

routes = [start.router, search.router, instruction.router, callback.router]