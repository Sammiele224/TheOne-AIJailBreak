from core.rate_limiter import InMemoryRateLimiter


def test_rate_limiter_blocks_after_limit_is_reached() -> None:
    limiter = InMemoryRateLimiter(requests=2, window_seconds=60)

    assert limiter.allow("client-1") is True
    assert limiter.allow("client-1") is True
    assert limiter.allow("client-1") is False
