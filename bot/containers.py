from dependency_injector import containers, providers
from ayoomoney import YooMoneyWalletAsync

from core import repositories, services, cache
from bot import database, payment


class Container(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(modules=[
        ".handlers.admin.op",
        ".handlers.user.start",
        ".handlers.user.search",
        ".handlers.user.callback",
        ".handlers.user.subscribe",
        ".handlers.user.payment.telegram",
        ".handlers.user.payment.yoomoney",
        ".middleware.user",
        ".dialogs.selected",
        ".dialogs.getters",
        ".utils",
        ".main",
        __name__
    ])
    config = providers.Configuration()
    
    redis_client = providers.Resource(
        cache.init_redis,
        redis_dsn=config.redis_dsn
    )
    database_pool = providers.Resource(
        database.create_connection_pool,
        database_dsn=config.database_dsn
    )
    database_session = providers.Factory(
        database.create_connection,
        session_pool=database_pool
    )

    yoomoney_client = providers.Factory(
        YooMoneyWalletAsync,
        access_token=config.yoomoney_token
    )
    kinopoisk_api = providers.Factory(
        repositories.KinoPoiskAPI,
        redis=redis_client,
        token=config.kinopoisk_token
    )
    kinoclub_api = providers.Factory(
        repositories.KinoClubAPI,
        redis=redis_client,
        token=config.kinoclub_token
    )
    movie_repository = providers.Factory(
        repositories.MovieRepository,
        kinoclub_api=kinoclub_api,
        kinopoisk_api=kinopoisk_api
    )
    user_repository = providers.Factory(
        repositories.UserRepository,
        session=database_session
    )
    user_action_repository = providers.Factory(
        repositories.UserActionRepository,
        session=database_session
    )
    subscribe_repository = providers.Factory(
        repositories.SubscribeRepository,
        session=database_session
    )
    payments_history_repository = providers.Factory(
        repositories.PaymentHistoryRepository,
        session=database_session
    )
    
    movie_service = providers.Factory(
        services.MovieService,
        movie_repository=movie_repository
    )
    uploader_service = providers.Factory(
        services.UploaderService,
        uploader_url=config.uploader_url
    )

    yoomoney_payment = providers.Singleton(
        payment.YooMoneySubscribePayment,
        client=yoomoney_client
    )
    telegram_payment = providers.Singleton(
        payment.TelegramSubscribePayment
    )

    payment = providers.Selector(
        config.payment.type,
        telegram=telegram_payment,
        yoomoney=yoomoney_payment
    )
    