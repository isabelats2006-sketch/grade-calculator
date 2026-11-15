"""Tests for showing numbers exactly (used in messages and when saving a class)."""

from fractions import Fraction

import pytest

from grades import show_number


@pytest.mark.parametrize(
    "text",
    ["20", "0", "100", "27.5", "20.25", "20.123456", "0.001", "33.3333333"],
)
def test_numbers_are_shown_exactly_as_typed(text):
    assert show_number(Fraction(text)) == text


def test_trailing_zeros_typed_by_the_user_are_dropped():
    assert show_number(Fraction("27.50")) == "27.5"
