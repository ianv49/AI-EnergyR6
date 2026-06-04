import time


class Failer:
    def __init__(self, fails_before_success=2):
        self.counter = 0
        self.fails_before_success = fails_before_success

    def unstable(self):
        self.counter += 1
        if self.counter <= self.fails_before_success:
            raise RuntimeError(f"failed attempt {self.counter}")
        return "ok"


def test_retry_decorator_succeeds_after_retries():
    from azure_storage import AzureStorage

    storage = AzureStorage.__new__(AzureStorage)

    # Access the retry decorator
    retry = storage._retry(max_attempts=4, initial_delay=0.01, backoff=1.5)

    f = Failer(fails_before_success=2)

    decorated = retry(f.unstable)

    result = decorated()

    assert result == "ok"


def test_retry_decorator_raises_after_max_attempts():
    from azure_storage import AzureStorage

    storage = AzureStorage.__new__(AzureStorage)

    retry = storage._retry(max_attempts=3, initial_delay=0.01, backoff=1.5)

    f = Failer(fails_before_success=5)

    decorated = retry(f.unstable)

    try:
        decorated()
        assert False, "Expected RuntimeError after retries exhausted"
    except RuntimeError:
        assert True
