"""Test utilities and helpers."""

from decimal import Decimal


def assert_decimal_close(
    actual: Decimal | None,
    expected: Decimal | None,
    places: int = 2,
) -> None:
    """Assert two Decimal values are close (within rounding error)."""
    if actual is None and expected is None:
        return
    if actual is None or expected is None:
        raise AssertionError(f"Expected {expected}, got {actual}")

    # Compare to specified decimal places
    actual_rounded = actual.quantize(Decimal(10) ** -places)
    expected_rounded = expected.quantize(Decimal(10) ** -places)
    assert actual_rounded == expected_rounded, (
        f"Decimals not close: {actual} != {expected}"
    )
