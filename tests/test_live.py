"""Tests for the live CPU-load delta — pure, no hardware needed."""

from lib.parse import cpu_load


def test_first_sample_is_calm():
    # no previous sample yet -> calm
    assert cpu_load(None, (100, 90)) == 0.0


def test_fully_idle():
    # the entire interval was idle
    assert cpu_load((100, 90), (200, 190)) == 0.0


def test_fully_busy():
    # none of the interval was idle
    assert cpu_load((100, 90), (200, 90)) == 1.0


def test_half_load():
    assert cpu_load((0, 0), (100, 50)) == 0.5


def test_arbitrary_fraction():
    assert abs(cpu_load((0, 0), (100, 30)) - 0.7) < 1e-9


def test_counter_reset_is_safe():
    # non-monotonic counters (e.g. after a reset) must not blow up
    assert cpu_load((500, 400), (100, 90)) == 0.0


def test_zero_interval_is_safe():
    assert cpu_load((100, 90), (100, 90)) == 0.0


def test_result_always_bounded():
    assert 0.0 <= cpu_load((0, 0), (100, 0)) <= 1.0
