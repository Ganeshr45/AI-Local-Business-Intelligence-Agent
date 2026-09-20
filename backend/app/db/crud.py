from sqlalchemy.orm import Session
from app.db import models


def create_run(db: Session, query: str) -> models.Run:
    run = models.Run(query=query, status="planning")
    db.add(run)
    db.commit()
    db.refresh(run)
    return run


def update_run(db: Session, run_id: str, **fields):
    db.query(models.Run).filter(models.Run.id == run_id).update(fields)
    db.commit()


def get_run(db: Session, run_id: str) -> models.Run | None:
    return db.query(models.Run).filter(models.Run.id == run_id).first()


def save_business(db: Session, run_id: str, business: dict, is_target: bool) -> models.Business:
    row = models.Business(
        run_id=run_id,
        place_id=business.get("place_id"),
        name=business.get("name"),
        is_target=is_target,
        category=business.get("category"),
        address=business.get("address"),
        latitude=business.get("latitude"),
        longitude=business.get("longitude"),
        rating=business.get("rating"),
        review_count=business.get("review_count"),
        price_level=business.get("price_level"),
        website=business.get("website"),
        phone=business.get("phone"),
        raw_data=business,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def save_review(db: Session, business_id: str, review: dict) -> models.Review:
    row = models.Review(
        business_id=business_id,
        author=review.get("author"),
        rating=review.get("rating"),
        text=review.get("text"),
        sentiment=review.get("sentiment"),
        topics=review.get("topics", []),
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def save_website_audit(db: Session, business_id: str, audit: dict) -> models.WebsiteAudit:
    row = models.WebsiteAudit(
        business_id=business_id,
        has_online_ordering=audit.get("has_online_ordering"),
        has_menu_pricing=audit.get("has_menu_pricing"),
        mobile_friendly=audit.get("mobile_friendly"),
        seo_title=audit.get("seo_title"),
        seo_description=audit.get("seo_description"),
        contact_info_present=audit.get("contact_info_present"),
        load_time_ms=audit.get("load_time_ms"),
        raw_findings=audit,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def save_evidence(db: Session, run_id: str, label: str, source_type: str, content: str, source_id: str = None, metric_count: int = None, evidence_id: str = None) -> models.Evidence:
    row = models.Evidence(
        id=evidence_id if evidence_id else models.gen_uuid(),
        run_id=run_id,
        label=label,
        source_type=source_type,
        source_id=source_id,
        content=content,
        metric_count=metric_count,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def save_insight(db: Session, run_id: str, category: str, statement: str, supporting_evidence_ids: list, confidence: str, insight_id: str = None) -> models.Insight:
    row = models.Insight(
        id=insight_id if insight_id else models.gen_uuid(),
        run_id=run_id,
        category=category,
        statement=statement,
        supporting_evidence_ids=supporting_evidence_ids,
        confidence=confidence,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def save_recommendation(db: Session, run_id: str, statement: str, supporting_insight_ids: list, impact_score: int, effort_score: int, priority_rank: int) -> models.Recommendation:
    row = models.Recommendation(
        run_id=run_id,
        statement=statement,
        supporting_insight_ids=supporting_insight_ids,
        impact_score=impact_score,
        effort_score=effort_score,
        priority_rank=priority_rank,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def get_full_run_state(db: Session, run_id: str) -> dict:
    run = get_run(db, run_id)
    if not run:
        return None
    businesses = db.query(models.Business).filter(models.Business.run_id == run_id).all()
    evidence = db.query(models.Evidence).filter(models.Evidence.run_id == run_id).all()
    insights = db.query(models.Insight).filter(models.Insight.run_id == run_id).all()
    recommendations = db.query(models.Recommendation).filter(models.Recommendation.run_id == run_id).order_by(models.Recommendation.priority_rank).all()
    business_ids = [b.id for b in businesses]
    reviews = db.query(models.Review).filter(models.Review.business_id.in_(business_ids)).all() if business_ids else []
    audits = db.query(models.WebsiteAudit).filter(models.WebsiteAudit.business_id.in_(business_ids)).all() if business_ids else []
    return {
        "run": run,
        "businesses": businesses,
        "reviews": reviews,
        "audits": audits,
        "evidence": evidence,
        "insights": insights,
        "recommendations": recommendations,
    }
