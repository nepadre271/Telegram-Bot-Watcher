from dependency_injector import containers, providers

from core import repositories, services, cache
from bot import database


class Container(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(modules=[
        ".handlers.admin.op",
        ".handlers.user.start",
        ".handlers.user.search",
        ".handlers.user.callback",
        ".handlers.user.subscribe",
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
    