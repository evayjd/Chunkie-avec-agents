from abc import ABC, abstractmethod
from typing import Any, Dict


class BaseParser(ABC):
    @abstractmethod
    def parse(self, file_path: str) -> Dict[str, Any]:
        """
        Return a unified parsed structure:
        {
            "text": str,
            "pages": [
                {
                    "page_num": int,
                    "content": str,
                    "section": str | None
                }
            ],
            "metadata": {
                ...
            }
        }
        """
        raise NotImplementedError