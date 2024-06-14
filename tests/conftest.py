import os
import time

import pytest


@pytest.fixture(autouse=True)
def use_utc():
    # Store the original TZ environment variable if it exists
    original_tz = os.environ.get("TZ")
    os.environ["TZ"] = "UTC"
    # This makes the change effective immediately
    if hasattr(time, "tzset"):
        time.tzset()

    yield

    # Reset the TZ environment variable to its original value after the test
    if original_tz is not None:
        os.environ["TZ"] = original_tz
    else:
        del os.environ["TZ"]
    # Reset the timezone settings to the original
    if hasattr(time, "tzset"):
        time.tzset()
