import nonebot


def _plugin():
    plugin = nonebot.get_plugin("nonebot_plugin_ernie")
    assert plugin is not None
    return plugin


def test_plugin_loads_and_registers_commands() -> None:
    plugin = _plugin()

    assert plugin.metadata is not None
    assert plugin.metadata.name == "文心一言"
    assert plugin.metadata.type == "application"

    commands = {matcher.command().name for matcher in plugin.matcher}
    assert commands == {"一言", "绘图"}


def test_commands_parse_multi_word_arguments() -> None:
    plugin = _plugin()

    expected_args = {"一言": "content", "绘图": "prompt"}
    for matcher in plugin.matcher:
        command = matcher.command()
        arg_name = expected_args[command.name]
        result = command.parse(f"{command.name} 你好 世界")

        assert result.matched
        assert result.all_matched_args[arg_name] == ("你好", "世界")
