from . import callback, start, search, instruction, account, subscribe, blackhole, payment

routes = [
    start.router,
    instruction.router,
    account.router,
    subscribe.router,
    search.router,
    callback.router,
]
