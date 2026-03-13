"""
文件职责：统一异常定义
"""
from typing import Any


class PersonaKBError(Exception):
    def __init__(self, message: str, status_code: int = 500, details: dict[str, Any] | None = None):
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(message)


class DocumentNotFoundError(PersonaKBError):
    def __init__(self, document_id: str):
        super().__init__(message=f"文档不存在: {document_id}", status_code=404, details={"document_id": document_id})


class DocumentProcessingError(PersonaKBError):
    def __init__(self, filename: str, reason: str):
        super().__init__(message=f"文档处理失败: {filename} - {reason}", status_code=422, details={"filename": filename, "reason": reason})


class UnsupportedFileTypeError(PersonaKBError):
    def __init__(self, file_type: str, supported: list[str]):
        super().__init__(message=f"不支持的文件类型: {file_type}，支持: {', '.join(supported)}", status_code=415, details={"file_type": file_type, "supported": supported})


class FileSizeExceededError(PersonaKBError):
    def __init__(self, size_mb: float, max_mb: int):
        super().__init__(message=f"文件大小 {size_mb:.1f}MB 超出限制 {max_mb}MB", status_code=413, details={"size_mb": size_mb, "max_mb": max_mb})


class EmbeddingError(PersonaKBError):
    def __init__(self, reason: str):
        super().__init__(message=f"嵌入计算失败: {reason}", status_code=500, details={"reason": reason})


class LLMError(PersonaKBError):
    def __init__(self, reason: str, provider: str | None = None):
        super().__init__(message=f"LLM 调用失败: {reason}", status_code=503, details={"reason": reason, "provider": provider})


class RetrievalError(PersonaKBError):
    def __init__(self, stage: str, reason: str):
        super().__init__(message=f"检索管线失败（阶段: {stage}）: {reason}", status_code=500, details={"stage": stage, "reason": reason})


class ConversationNotFoundError(PersonaKBError):
    def __init__(self, conversation_id: str):
        super().__init__(message=f"会话不存在: {conversation_id}", status_code=404, details={"conversation_id": conversation_id})


class InsufficientEvidenceError(PersonaKBError):
    def __init__(self, query: str):
        super().__init__(message=f"证据不足: {query[:100]}", status_code=200, details={"query": query})
