try:
    import sys
    import pysqlite3 as sqlite3  # type: ignore

    sys.modules["sqlite3"] = sqlite3
    sys.modules["sqlite3.dbapi2"] = sqlite3.dbapi2
except Exception:
    pass

import os
import pytest
import tenacity

from pathlib import Path
from deepeval.config.settings import get_settings, reset_settings


@pytest.fixture(autouse=True)
def _ensure_hidden_store_dir(tmp_path: Path):
    d = tmp_path / ".deepeval"
    d.mkdir(exist_ok=True)
    # some code expects the file to be there after a run,
    # but at minimum the directory must exist to avoid FileNotFoundError
    yield


# Silence telemetry for all tests so we don't have to deal with the noise
@pytest.fixture(autouse=True)
def _telemetry_opt_out(monkeypatch):
    monkeypatch.setenv("DEEPEVAL_TELEMETRY_OPT_OUT", "1")
    yield


# Run every test in its own temp CWD so .deepeval/.deepeval is sandboxed
@pytest.fixture(autouse=True)
def _isolate_cwd(tmp_path: Path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    yield


# Default dotenv path most tests can reuse; override in tests as needed
@pytest.fixture
def env_path(tmp_path: Path) -> Path:
    return tmp_path / ".env.local"


@pytest.fixture
def hidden_store_dir(tmp_path: Path) -> Path:
    d = tmp_path / ".deepeval"
    d.mkdir(parents=True, exist_ok=True)
    return d


@pytest.fixture(autouse=True)
def no_sleep(monkeypatch):
    monkeypatch.setattr(tenacity.nap, "sleep", lambda _: None, raising=True)


@pytest.fixture()
def settings():
    settings = get_settings()
    yield settings


@pytest.fixture(autouse=True)
def _env_sandbox():
    from deepeval.config.settings import reset_settings

    before = os.environ.copy()
    # ensure clean singleton before the test runs
    reset_settings(reload_dotenv=False)
    try:
        yield
    finally:
        # restore env
        to_remove = [k for k in list(os.environ.keys()) if k not in before]
        for k in to_remove:
            os.environ.pop(k, None)
        for k, v in before.items():
            if os.environ.get(k) != v:
                os.environ[k] = v
        # ensure fresh Settings for the next test
        reset_settings(reload_dotenv=False)


@pytest.fixture(autouse=True)
def _core_mode_no_confident(monkeypatch):
    # Ensure no Confident keys come from the process env in this test
    for key in ("CONFIDENT_API_KEY", "CONFIDENTAI_API_KEY"):
        monkeypatch.delenv(key, raising=False)

    # Prevent dotenv from re-injecting keys from files during the test
    # core tests shouldn’t depend on local .env anyway
    monkeypatch.setenv("DEEPEVAL_DISABLE_DOTENV", "1")

    # Rebuild the Settings singleton from the now-clean process env
    reset_settings(reload_dotenv=False)

    # Clear the in-memory Settings fields (no persistence)
    s = get_settings()
    with s.edit(persist=False) as ctx:
        ctx.s.API_KEY = None
        ctx.s.CONFIDENT_API_KEY = None

    # Yield control to the test
    yield
