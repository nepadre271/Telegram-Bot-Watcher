from aiogram import Router, Dispatcher

from bot.database.models import Subscribe


class BaseSubscribePayment:
    router: Router | None = None

    def registry_router(self, dp: Dispatcher):
        if self.router is None:
            return

        dp.include_router(self.router)

    async def execute(self, subscribe: Subscribe, *args, **kwargs):
        raise NotImplementedError
