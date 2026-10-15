"""CORS allowlist: Firebase preview channels allowed, everything else rejected."""
import main


def test_preview_channel_allowed():
    assert main._is_allowed_origin("https://numista-vault--p7-v8-gate-ibg4oycd.web.app")


def test_live_origins_allowed():
    for o in ("https://numista.ai", "https://www.numista.ai", "https://numista-vault.web.app"):
        assert main._is_allowed_origin(o)


def test_evil_origins_rejected():
    for o in (
        "https://evil.com",
        "https://numista-vault--x.web.app.evil.com",
        "https://evil--numista-vault--x.web.app",
        "http://numista-vault--x.web.app",
        "https://other-site--x.web.app",
        "",
    ):
        assert not main._is_allowed_origin(o)
