import os
import sys
import pytest

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from server.stabilizer import Stabilizer


def test_drift_and_recovery():
    stab = Stabilizer(n_history=2)

    # Initial hypothesis becomes stable immediately
    assert stab.get_delta("hello world ") == "hello world "
    assert stab.stable_prefix == "hello world "

    # Drift: hypothesis changes earlier word, stable prefix shrinks
    assert stab.get_delta("hello there ") == ""
    assert stab.stable_prefix == "hello "

    # New words become stable after drift
    assert stab.get_delta("hello there general") == "there "
    assert stab.stable_prefix == "hello there "

    # Repeating hypothesis confirms additional word
    stab.get_delta("hello there general ")
    assert stab.get_delta("hello there general ") == "general "
    assert stab.stable_prefix == "hello there general "


def test_multiple_drifts():
    stab = Stabilizer(n_history=2)

    stab.get_delta("foo bar ")
    stab.get_delta("foo bar baz ")
    assert stab.stable_prefix == "foo bar "

    # Drift backward
    stab.get_delta("foo baz ")
    assert stab.stable_prefix == "foo "

    # Another drift forward and confirmation
    assert stab.get_delta("foo baz qux") == "baz "
    stab.get_delta("foo baz qux ")
    assert stab.get_delta("foo baz qux ") == "qux "
    assert stab.stable_prefix == "foo baz qux "
