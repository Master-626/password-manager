"""Pytest coverage for generation, CLI safety, and the count option."""

import inspect
import string
from importlib.metadata import version
from unittest.mock import patch

import pytest
from click.testing import CliRunner

from password_manager import generator
from password_manager.cli import main
from password_manager.generator import generate_password

ALPHANUMERIC = string.ascii_letters + string.digits
WITH_SYMBOLS = ALPHANUMERIC + string.punctuation


def _classes(symbols):
    groups = [string.ascii_lowercase, string.ascii_uppercase, string.digits]
    if symbols:
        groups.append(string.punctuation)
    return groups


def _shown(result):
    """Return stdout plus stderr.

    Click 8.1's ``Result.output`` is stdout only when the streams are split.
    Click 8.2+ mixes them in ``output``. Checking both keeps the assertions
    on the text a person would actually see.
    """
    text = result.stdout
    try:
        text += result.stderr
    except ValueError:
        pass
    return text


@pytest.fixture
def runner():
    # Click 8.1 mixes stderr into stdout unless asked not to. Click 8.2+
    # always keeps the streams separate and dropped the mix_stderr argument.
    if "mix_stderr" in inspect.signature(CliRunner).parameters:
        return CliRunner(mix_stderr=False)
    return CliRunner()


@pytest.mark.parametrize("length", [8, 20, 32, 1024])
@pytest.mark.parametrize("symbols", [True, False])
def test_password_meets_length_and_class_rules(length, symbols):
    password = generate_password(length, symbols=symbols)
    allowed = WITH_SYMBOLS if symbols else ALPHANUMERIC
    assert len(password) == length
    assert set(password) <= set(allowed)
    assert not any(char.isspace() for char in password)
    for group in _classes(symbols):
        assert any(char in group for char in password)


@pytest.mark.parametrize(
    ("length", "message"),
    [
        (-1, "between 8 and 1024"),
        (0, "between 8 and 1024"),
        (7, "between 8 and 1024"),
        (1025, "between 8 and 1024"),
        (True, "integer"),
        (1.5, "integer"),
        ("20", "integer"),
        (None, "integer"),
    ],
)
def test_invalid_length_explains_the_problem(length, message):
    with pytest.raises(ValueError, match=message):
        generate_password(length)


def test_symbols_flag_must_be_boolean():
    with pytest.raises(ValueError, match="boolean"):
        generate_password(symbols="false")


def test_draws_from_secrets_and_rejects_a_class_gap():
    with patch(
        "password_manager.generator.secrets.choice",
        side_effect="aaaaaaaaaB3!cD5?",
    ) as choose:
        assert generate_password(8) == "aB3!cD5?"
    assert choose.call_count == 16
    alphabet = WITH_SYMBOLS
    assert all(call.args == (alphabet,) for call in choose.call_args_list)


def test_stops_when_a_required_class_never_appears(monkeypatch):
    monkeypatch.setattr(generator, "_MAX_ATTEMPTS", 4)
    monkeypatch.setattr(generator.secrets, "choice", lambda alphabet: "a")
    with pytest.raises(RuntimeError, match="character class"):
        generate_password(8)


def test_distinct_calls_are_not_the_old_hardcoded_password():
    old = "xY7#kL2$mN9!pQ4@"
    passwords = [generate_password() for _ in range(30)]
    assert all(password != old for password in passwords)
    assert len(set(passwords)) > 1


def test_default_cli_output_is_one_plain_line(runner):
    result = runner.invoke(main, ["generate"])
    assert result.exit_code == 0, result.output
    assert result.stderr == ""
    assert result.stdout.endswith("\n")
    assert result.stdout.count("\n") == 1
    assert len(result.stdout.rstrip("\n")) == 20


def test_count_prints_one_password_per_line(runner):
    samples = ["aaaaaaA1", "bbbbbbB2", "ccccccC3"]
    with patch(
        "password_manager.cli.generate_password", side_effect=samples
    ) as generate:
        result = runner.invoke(
            main, ["generate", "--count", "3", "--no-symbols", "-l", "8"]
        )
    assert result.exit_code == 0, result.output
    assert result.stdout == "aaaaaaA1\nbbbbbbB2\nccccccC3\n"
    assert generate.call_count == 3
    assert [call.kwargs for call in generate.call_args_list] == [
        {"length": 8, "symbols": False}
    ] * 3


@pytest.mark.parametrize("count", ["0", "101", "nope"])
def test_count_is_limited(runner, count):
    result = runner.invoke(main, ["generate", "-n", count])
    assert result.exit_code == 2
    assert result.stdout == ""


def test_piped_output_keeps_escape_characters(runner):
    # Click strips ANSI-looking text when stdout is not a terminal unless color
    # is forced. Capturing a password must not drop characters.
    sample = "aB3!\x1b[31mX!"
    with patch("password_manager.cli.generate_password", return_value=sample):
        result = runner.invoke(main, ["generate", "-l", "8"])
    assert result.exit_code == 0, result.output
    assert result.stdout == sample + "\n"


def test_generation_failure_is_an_error_without_a_traceback(runner):
    with patch(
        "password_manager.cli.generate_password",
        side_effect=RuntimeError("Could not generate a password"),
    ):
        result = runner.invoke(main, ["generate", "-n", "2"])
    assert result.exit_code == 1
    assert result.stdout == ""
    assert "Could not generate a password" in result.stderr
    assert "Traceback" not in _shown(result)


@pytest.mark.parametrize(
    "args",
    [
        ["hunter2"],
        ["generate", "hunter2"],
        ["generate", "hunter2", "othersecret"],
        ["add", "example", "hunter2"],
        ["get", "example", "hunter2"],
        ["generate", "--hunter2"],
        ["--hunter2"],
    ],
)
def test_rejected_user_text_is_not_echoed(runner, args):
    result = runner.invoke(main, args)
    assert result.exit_code == 2
    assert result.stdout == ""
    shown = _shown(result)
    assert "hunter2" not in shown
    assert "othersecret" not in shown


def test_unknown_names_still_suggest_real_ones(runner):
    command = runner.invoke(main, ["generat"])
    option = runner.invoke(main, ["generate", "--lenght", "12"])
    assert command.exit_code == 2
    assert option.exit_code == 2
    command_text = _shown(command)
    option_text = _shown(option)
    assert "'generat'" not in command_text
    assert "--lenght" not in option_text
    # Long-option suggestions exist on every supported Click. Command
    # suggestions were added with NoSuchCommand in Click 8.4; 3.8/3.9 stay
    # on Click 8.1, which only reports that the command is unknown.
    assert "length" in option_text
    click_version = tuple(int(part) for part in version("click").split(".")[:2])
    if click_version >= (8, 4):
        assert "generate" in command_text


def test_username_is_not_echoed_when_storage_is_refused(runner):
    result = runner.invoke(main, ["add", "example", "-u", "hunter2"])
    assert result.exit_code == 1
    assert "hunter2" not in _shown(result)
    assert "Nothing was saved" in result.stderr
    assert result.stdout == ""
