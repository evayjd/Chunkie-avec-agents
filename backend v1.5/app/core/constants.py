"""
文件职责：业务常量定义
集中管理不变的业务常量，与配置（可变）区分。
"""

from enum import Enum


class DocumentStatus(str, Enum):
    """文档处理状态枚举"""
    PENDING = "pending"
    PROCESSING = "processing"
    INDEXED = "indexed"
    FAILED = "failed"
    DELETED = "deleted"


class FileType(str, Enum):
    """支持的文件类型"""
    PDF = "pdf"
    MARKDOWN = "md"
    TEXT = "txt"
    DOCX = "docx"


EXTENSION_MAP: dict[str, FileType] = {
    ".pdf": FileType.PDF,
    ".md": FileType.MARKDOWN,
    ".markdown": FileType.MARKDOWN,
    ".txt": FileType.TEXT,
    ".docx": FileType.DOCX,
}


class Language(str, Enum):
    """支持的语言"""
    CHINESE = "zh"
    ENGLISH = "en"
    FRENCH = "fr"
    UNKNOWN = "unknown"


class PersonaDimension(str, Enum):
    """人格分析维度"""
    BUILDER_ENERGY = "builder_energy"
    ACADEMIC_INTENSITY = "academic_intensity"
    PERFECTIONISM = "perfectionism"
    MULTILINGUAL_FLEX = "multilingual_flex"
    CAREER_SIGNALING = "career_signaling"
    AESTHETIC_OBSESSION = "aesthetic_obsession"
    CHAOS_FACTOR = "chaos_factor"
    OVERENGINEERING_RISK = "overengineering_risk"


class RetrievalStage(str, Enum):
    """检索管线阶段"""
    QUERY_PROCESSING = "query_processing"
    DENSE_RETRIEVAL = "dense_retrieval"
    SPARSE_RETRIEVAL = "sparse_retrieval"
    HYBRID_FUSION = "hybrid_fusion"
    METADATA_FILTER = "metadata_filter"
    DEDUPLICATION = "deduplication"
    RERANKING = "reranking"
    CONTEXT_PACKING = "context_packing"
    CITATION_ALIGNMENT = "citation_alignment"


GROUNDED_QA_SYSTEM_PROMPT_ZH = """你是一个严格基于文档内容回答问题的智能助手。

规则：
1. 只能基于提供的文档内容回答问题，不得使用文档范围之外的知识。
2. 每条信息必须引用其来源，格式为 [编号]（例如 [1]、[2]）。
3. 如果文档内容不足以回答问题，明确说明："根据现有文档，无法找到足够的信息来回答此问题。"
4. 回答要简洁、准确，直接回答用户的问题。
5. 不要编造任何未在文档中出现的信息。

以下是相关文档内容：
{context}
"""

GROUNDED_QA_SYSTEM_PROMPT_EN = """You are an intelligent assistant that strictly answers questions based on document content.

Rules:
1. Only answer based on the provided document content.
2. Every piece of information must be cited with its source in [number] format (e.g., [1], [2]).
3. If the document content is insufficient, clearly state: "Based on the available documents, there is not enough information to answer this question."
4. Be concise and accurate.
5. Do not fabricate any information not in the documents.

Relevant document content:
{context}
"""

GROUNDED_QA_PROMPT = {
    "zh": GROUNDED_QA_SYSTEM_PROMPT_ZH,
    "en": GROUNDED_QA_SYSTEM_PROMPT_EN,
}


ROAST_SYSTEM_PROMPT_ZH = """
你是一位观察力极强、嘴很毒但逻辑严谨的吐槽型人格分析师。

你的任务是：基于用户提供的文档内容，对这个人的行为模式和性格特点进行犀利但有证据的吐槽分析。

写作风格：
- 像一个文化水平很高但忍不住想吐槽朋友的人
- 语气可以讽刺、挖苦、调侃，但不要粗俗或恶意辱骂
- 吐槽要精准、有画面感，而不是泛泛而谈
- 优先抓住文档中反复出现的行为模式、兴趣偏好、表达方式

严格规则：
1. 每一个吐槽点必须有文档证据支撑。
2. 所有引用必须使用格式：[编号]。
3. 不允许凭空编造信息。
4. 不要写成心理学报告，要像“看穿一个人之后的调侃式点评”。
5. 允许稍微夸张，但不能脱离文档事实。
6. 总长度控制在 {max_length} 字以内。

输出风格示例（仅示例语气，不要照抄）：

“从这些记录来看，你这个人的人生结构其实非常稳定：  
一边对各种新东西充满好奇，一边又对真正需要长期坚持的事情表现出惊人的拖延能力。[2][4]

很多人是‘想得多做得少’，而你似乎升级到了一个更精致的版本——  
你会非常认真地思考、规划、分析，但最终的行动量看起来依然像是在给未来的自己留作业。[3]

更有意思的是，你经常在深夜突然开始思考宏大的问题：AI、人生方向、效率系统、甚至世界结构。[5]  
这种行为模式通常意味着两件事：  
第一，你确实很爱思考；  
第二，你的大脑似乎只在夜深人静的时候才决定开始认真上班。”

文档内容：
{context}
"""

ROAST_SYSTEM_PROMPT = {
    "zh": ROAST_SYSTEM_PROMPT_ZH
}

INSUFFICIENT_EVIDENCE_MSG = {
    "zh": "根据现有文档，无法找到足够的信息来回答此问题。",
    "en": "Based on the available documents, there is not enough information to answer this question.",
    "fr": "D'après les documents disponibles, il n'y a pas suffisamment d'informations pour répondre à cette question.",
}
