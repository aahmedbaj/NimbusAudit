from nimbusaudit.cli import parse_menu_check_selection, CheckSelectionError
from pathlib import Path
from unittest.mock import MagicMock

import pytest


def test_parse_menu_check_selection_exits_on_zero() -> None:
    assert parse_menu_check_selection("0") is None


def test_parse_menu_check_selection_accepts_all_with_star() -> None:
    assert parse_menu_check_selection("*") == "all"


def test_parse_menu_check_selection_accepts_single_number() -> None:
    assert parse_menu_check_selection("2") == "ec2"


def test_parse_menu_check_selection_accepts_multiple_numbers() -> None:
    assert parse_menu_check_selection("1,3") == "security-groups,ebs"


def test_parse_menu_check_selection_ignores_spaces() -> None:
    assert parse_menu_check_selection(" 1 , 3 ") == "security-groups,ebs"


def test_parse_menu_check_selection_rejects_empty_input() -> None:
    with pytest.raises(
            CheckSelectionError,
            match="no menu options were selected",
    ):
        parse_menu_check_selection("")


def test_parse_menu_check_selection_rejects_invalid_number() -> None:
    with pytest.raises(
            CheckSelectionError,
            match="unsupported menu option",
    ):
        parse_menu_check_selection("9")


def test_parse_menu_check_selection_rejects_exit_combined_with_other_options() -> None:
    with pytest.raises(
            CheckSelectionError,
            match="'0' cannot be combined",
    ):
        parse_menu_check_selection("0,2")


def test_parse_menu_check_selection_rejects_all_combined_with_other_options() -> None:
    with pytest.raises(
            CheckSelectionError,
            match="'\\*' cannot be combined",
    ):
        parse_menu_check_selection("*,2")