from typing import List, Optional, Dict, Any

from sqlalchemy.orm import Session

from backend.core.retrieval_config import RETRIEVAL_METHOD
from backend.services.retrieval.retriever_factory import get_retriever
from backend.services.roast.contradiction_finder import find_contradictions
from backend.services.roast.data_builder import build_user_data
from backend.services.roast.persona_analyzer import analyze_persona
from backend.services.roast.score_generator import generate_scores
from backend.services.roast.tag_generator import generate_tags
from backend.services.roast.roast_writer import write_roast



def run_roast_pipeline(
    query: str,
    db: Session,
    document_ids: Optional[List[str]] = None,
    top_k: int = 6,
) -> Dict[str, Any]:
    """
    Roast pipeline

    Steps
    -----
    1. Retrieval
    2. Build user data
    3. Persona analysis
    4. Score generation
    5. Tag generation
    6. Roast writing
    """

    if not query or not query.strip():
        raise ValueError("Query cannot be empty")

    retriever = get_retriever(RETRIEVAL_METHOD, db)

    retrieved_chunks = retriever.retrieve(
        question=query.strip(),
        document_ids=document_ids,
        top_k=top_k,
    )

    chunks: List[Dict[str, Any]] = []

    for i, r in enumerate(retrieved_chunks, start=1):
        chunks.append(
            {
                "citation_id": r.get("citation_id", i),
                "doc_id": r.get("doc_id"),
                "chunk_id": r.get("chunk_id"),
                "chunk_index": r.get("chunk_index"),
                "content": r.get("content", ""),
                "page_start": r.get("page_start"),
                "page_end": r.get("page_end"),
                "section": r.get("section"),
            }
        )

    user_data = build_user_data(chunks)

    persona = analyze_persona(user_data)

    score_result = generate_scores(persona, user_data)

    tags = generate_tags(persona, user_data)

    roast_text = write_roast(persona, user_data)
    
    contradictions = find_contradictions(persona, user_data)

    roast_text = write_roast(
        persona,
        contradictions,
        user_data,
    )

    return {
        "persona": persona,
        "scores": score_result["scores"],
        "diagnosis_rate": score_result["diagnosis_rate"],
        "tags": tags,
        "roast_text": roast_text,
        "citations": chunks,
    }