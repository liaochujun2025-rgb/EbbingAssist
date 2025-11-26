import pytest

from backend.app import create_app
from backend.extensions import db
# ensure models are registered before create_all
import backend.modules.plan.models  # noqa: F401
import backend.modules.knowledge.models  # noqa: F401
import backend.modules.study_log.models  # noqa: F401


@pytest.fixture(scope="session")
def app():
    app = create_app("testing")
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()


@pytest.fixture()
def client(app):
    return app.test_client()
