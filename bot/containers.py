from dependency_injector import containers, providers

from core import repositories, services, cache


class Container(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(modules=[
        ".handlers.user.watch",
        ".handlers.user.search",
        ".handlers.user.callback",
        ".dialogs.getters",
        ".dialogs.selected",
        ".main",
        __name__
    ])
    config = providers.Configuration()
    
    redis_client = providers.Resource(
        cache.init_redis,
        redis_dsn=config.redis_dsn
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
    
    movie_service = providers.Factory(
        services.MovieService,
        movie_repository=movie_repository
    )
    uploader_service = providers.Factory(
        services.UploaderService,
        uploader_url=config.uploader_url
    )
    