import re
from sqlalchemy.orm import Session
from app.db import models
from app.tools import llm

SYSTEM_PROMPT = """Answer the user's question about their local market using ONLY the evidence snippets provided below.
Quote specific numbers where available. If the evidence does not contain an answer, say so directly instead of guessing.
Keep the answer to 2-4 sentences."""

STOPWORDS = {"the", "a", "an", "is", "are", "what", "why", "how", "should", "i", "my", "of", "to", "in", "for", "and", "or", "do", "does"}


def _tokenize(text: str) -> set:
    words = re.findall(r"[a-z0-9]+", text.lower())
    return {w for w in words if w not in STOPWORDS}


def _score(query_tokens: set, content: str) -> int:
    content_tokens = _tokenize(content)
    return len(query_tokens & content_tokens)


def retrieve_relevant_evidence(db: Session, run_id: str, question: str, top_k: int = 8) -> list[models.Evidence]:
    query_tokens = _tokenize(question)
    all_evidence = db.query(models.Evidence).filter(models.Evidence.run_id == run_id).all()
    scored = [(e, _score(query_tokens, e.content)) for e in all_evidence]
    scored = [pair for pair in scored if pair[1] > 0]
    scored.sort(key=lambda pair: pair[1], reverse=True)
    if not scored:
        scored = [(e, 0) for e in all_evidence[:top_k]]
    return [e for e, _ in scored[:top_k]]


def ask(db: Session, run_id: str, question: str) -> dict:
    relevant = retrieve_relevant_evidence(db, run_id, question)

    insights = db.query(models.Insight).filter(models.Insight.run_id == run_id).all()
    relevant_insights = [i for i in insights if _score(_tokenize(question), i.statement) > 0]

    if not relevant and not relevant_insights:
        return {"answer": "This report does not contain evidence to answer that question.", "citations": []}

    if llm.is_live():
        evidence_text = "\n".join(f"[{e.label}] {e.content}" for e in relevant)
        insight_text = "\n".join(f"[AI_INSIGHT] {i.statement}" for i in relevant_insights)
        user_prompt = f"QUESTION: {question}\n\nEVIDENCE:\n{evidence_text}\n\n{insight_text}"
        try:
            answer = llm.call_text(SYSTEM_PROMPT, user_prompt)
            return {"answer": answer, "citations": [e.id for e in relevant] + [i.id for i in relevant_insights]}
        except Exception:
            pass

    lines = [f"{e.label}: {e.content}" for e in relevant[:4]]
    lines += [f"AI INSIGHT: {i.statement}" for i in relevant_insights[:2]]
    fallback_answer = "Based on the collected evidence: " + " | ".join(lines) if lines else "No matching evidence found for this question."
    return {"answer": fallback_answer, "citations": [e.id for e in relevant] + [i.id for i in relevant_insights]}
