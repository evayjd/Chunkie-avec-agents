from typing import Dict, List, Any


class ToolRegistry:
    """
    工具注册中心

    职责：
    1. 注册所有可用工具
    2. 按名称获取工具
    3. 返回工具描述给 agent 用于决策
    """

    def __init__(self):
        self._tools: Dict[str, Any] = {}

    def register(self, tool) -> None:
        self._tools[tool.name] = tool

    def get(self, name: str):
        return self._tools.get(name)

    def list_tool_names(self) -> List[str]:
        return list(self._tools.keys())

    def get_tool_specs(self) -> List[dict]:
        """
        返回给 agent 的工具元信息
        """
        specs = []

        for tool in self._tools.values():
            specs.append({
                "name": tool.name,
                "description": tool.description,
                "input_schema": tool.input_schema
            })

        return specs