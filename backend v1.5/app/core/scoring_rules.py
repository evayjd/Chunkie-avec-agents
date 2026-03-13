"""
Roast dimension scoring rules (0-100 per dimension).

Score = evidence_score (0-80) + peak_bonus (0-20)

Evidence score
--------------
Uses dense_score (cosine similarity, range [0,1]) rather than the RRF
rank-position score.  RRF is rank-normalised: rank #1 always contributes
the same value regardless of query, so every dimension would produce
identical scores (the original bug).  Cosine similarity is query-dependent,
so a chunk about academic papers scores high for ACADEMIC_INTENSITY but low
for CHAOS_FACTOR.

Tier thresholds (cosine similarity):
  Strong   >= 0.75  -> +20 pts  (max 4 chunks)
  Moderate >= 0.55  -> +10 pts  (max 4 chunks)
  Weak     >= 0.35  -> +3  pts  (max 6 chunks)
  Skip     <  0.35  -> 0   pts  (below retrieval threshold, treated as noise)

Max evidence score = 80

Peak bonus
----------
  peak_bonus = min(20, round(peak_sim / 1.0 * 20))

  where peak_sim = highest cosine similarity among returned chunks.

Final score
-----------
  final_score = min(100, evidence_score + peak_bonus)

Interpretation:
   0-20   almost no relevant content
  21-40   occasional mentions
  41-60   clear trait
  61-80   strong trait
  81-100  dominant personality dimension
"""
 

# -- Cosine similarity thresholds for tier classification ----------------
# Cosine similarity range [0, 1]; higher = more relevant to this query.

SIM_STRONG: float = 0.75    # highly relevant: almost certainly this dimension
SIM_MODERATE: float = 0.55  # moderately relevant
SIM_WEAK: float = 0.35      # marginally relevant; below this = noise

# -- Points per chunk ----------------------------------------------------

PTS_STRONG: int = 20
PTS_MODERATE: int = 10
PTS_WEAK: int = 3

# -- Chunk count caps (prevent bulk-weak-signal inflation) ---------------

MAX_STRONG_CHUNKS = 4
MAX_MODERATE_CHUNKS = 4
MAX_WEAK_CHUNKS = 6

MAX_EVIDENCE_SCORE: int = 80

# -- Peak bonus ----------------------------------------------------------

SIMILARITY_MAX: float = 1.0  # theoretical max cosine similarity
MAX_PEAK_BONUS: int = 20

# -- Final cap -----------------------------------------------------------

MAX_SCORE: int = 100


def calculate_dimension_score(chunks: list[dict]) -> int:
    """Calculate score for a single persona dimension (0-100).

    Parameters
    ----------
    chunks
        Chunks returned by the hybrid retrieval pipeline, each dict must
        contain a ``dense_score`` field (cosine similarity written by
        retrieval Stage 9).  Chunks should be ordered by descending score.

    Returns
    -------
    int
        Dimension score.
    """

    

    if not chunks:
        return 0

    evidence_score = 0
    strong_count = 0
    moderate_count = 0
    weak_count = 0

    for chunk in chunks:
        # Use cosine similarity, NOT the RRF rank-fusion score.
        # RRF reflects rank position only (rank #1 always yields ~1/61 * weight),
        # making it query-independent and causing all dimensions to score identically.
        sim = chunk.get("dense_score", 0.0)

        if sim >= SIM_STRONG and strong_count < MAX_STRONG_CHUNKS:
            evidence_score += PTS_STRONG
            strong_count += 1
            tier = "STRONG"
        elif sim >= SIM_MODERATE and moderate_count < MAX_MODERATE_CHUNKS:
            evidence_score += PTS_MODERATE
            moderate_count += 1
            tier = "MODERATE"
        elif sim >= SIM_WEAK and weak_count < MAX_WEAK_CHUNKS:
            evidence_score += PTS_WEAK
            weak_count += 1
            tier = "WEAK"
        else:
            tier = "SKIP"

        print(
            f"  chunk {chunk.get('chunk_id', '?')[:8]}"
            f"  sim={sim:.4f}  tier={tier}  evidence_score={evidence_score}"
        )

        if evidence_score >= MAX_EVIDENCE_SCORE:
            break

    evidence_score = min(evidence_score, MAX_EVIDENCE_SCORE)

    # -- Peak bonus --------------------------------------------------
    # The top chunk's cosine similarity signals how strongly this
    # dimension is represented at its best in the knowledge base.
    peak_sim = chunks[0].get("dense_score", 0.0)
    peak_bonus = min(
        MAX_PEAK_BONUS,
        round(peak_sim / SIMILARITY_MAX * MAX_PEAK_BONUS),
    )

    final = min(MAX_SCORE, evidence_score + peak_bonus)

    print(
        f"  evidence_score={evidence_score}  peak_sim={peak_sim:.4f}"
        f"  peak_bonus={peak_bonus}  FINAL={final}"
    )
    print("---- scoring end ----")

    return final
