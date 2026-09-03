import pytest
from mini_commerce_mcp import tooling

def test_unknown_command_cannot_be_executed():
    with pytest.raises(ValueError):tooling.run_suite("rm-everything")

def test_suite_commands_do_not_use_shell():
    assert set(tooling.SUITES)=={"backend-unit","backend-all","mcp"}
    assert all(isinstance(command,list) for command in tooling.SUITES.values())
