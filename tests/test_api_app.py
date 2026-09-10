from backend.app.main import APP_DESCRIPTION, APP_TITLE, APP_VERSION, create_app


def test_create_app_returns_fastapi_instance() -> None:
    application = create_app()

    assert application.title == APP_TITLE
    assert application.description == APP_DESCRIPTION
    assert application.version == APP_VERSION


def test_module_level_app_is_created() -> None:
    from backend.app.main import app

    assert app.title == APP_TITLE
    assert app.version == APP_VERSION
