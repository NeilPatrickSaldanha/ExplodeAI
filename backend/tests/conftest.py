import pytest
from fastapi.testclient import TestClient
from sqlmodel import SQLModel, create_engine
from sqlmodel.pool import StaticPool

from app import db
from app.config import get_settings

# claim id -> test names that technically validate it (Pass 3).
VALIDATED_CLAIMS: dict[str, list[str]] = {}
# claim ids whose evidence tests actually ran and passed in this session.
PASSED_CLAIMS: set[str] = set()


def validates(*claim_ids: str):
    """Mark a test as Pass 3 technical evidence for lesson claims."""

    def deco(fn):
        for cid in claim_ids:
            VALIDATED_CLAIMS.setdefault(cid, []).append(fn.__name__)
        return pytest.mark.claims(*claim_ids)(fn)

    return deco


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    marker = item.get_closest_marker("claims")
    if marker and report.when == "call" and report.passed:
        PASSED_CLAIMS.update(marker.args)


def pytest_configure(config):
    config.addinivalue_line("markers", "claims(*ids): Pass 3 evidence for lesson claims")


@pytest.fixture
def engine():
    eng = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    SQLModel.metadata.create_all(eng)
    db.set_engine(eng)
    yield eng
    db.set_engine(None)


@pytest.fixture
def client(engine, monkeypatch):
    # The lesson is a draft until all three verification passes complete.
    monkeypatch.setattr(get_settings(), "show_draft_lessons", True)
    from app.main import create_app

    with TestClient(create_app()) as c:
        yield c
