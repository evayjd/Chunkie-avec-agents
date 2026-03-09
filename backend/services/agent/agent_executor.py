class AgentExecutor:
    """
    工具执行器

    职责：
    1. 根据 tool name 找到工具
    2. 调用 tool.run()
    3. 统一返回结果
    """

    def __init__(self, registry):
        self.registry = registry

    def execute(self, tool_name: str, arguments: dict):
        tool = self.registry.get(tool_name)

        if not tool:
            raise ValueError(f"Tool not found: {tool_name}")

        return tool.run(**arguments)