import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, Integer, Boolean, DateTime, JSON, ForeignKey, Text
from app.db.database import Base


def gen_uuid():
    return str(uuid.uuid4())


class Run(Base):
    __tablename__ = "runs"
    id = Column(String, primary_key=True, default=gen_uuid)
    query = Column(Text, nullable=False)
    location = Column(String)
    category = Column(String)
    status = Column(String, default="planning")
    created_at = Column(DateTime, default=datetime.utcnow)


class Business(Base):
    __tablename__ = "businesses"
    id = Column(String, primary_key=True, default=gen_uuid)
    run_id = Column(String, ForeignKey("runs.id"))
    place_id = Column(String)
    name = Column(String, nullable=False)
    is_target = Column(Boolean, default=False)
    category = Column(String)
    address = Column(String)
    latitude = Column(Float)
    longitude = Column(Float)
    rating = Column(Float)
    review_count = Column(Integer)
    price_level = Column(Integer)
    website = Column(String)
    phone = Column(String)
    raw_data = Column(JSON)


class Review(Base):
    __tablename__ = "reviews"
    id = Column(String, primary_key=True, default=gen_uuid)
    business_id = Column(String, ForeignKey("businesses.id"))
    author = Column(String)
    rating = Column(Integer)
    text = Column(Text)
    published_at = Column(DateTime)
    sentiment = Column(String)
    topics = Column(JSON)


class WebsiteAudit(Base):
    __tablename__ = "website_audits"
    id = Column(String, primary_key=True, default=gen_uuid)
    business_id = Column(String, ForeignKey("businesses.id"))
    has_online_ordering = Column(Boolean)
    has_menu_pricing = Column(Boolean)
    mobile_friendly = Column(Boolean)
    seo_title = Column(String)
    seo_description = Column(Text)
    contact_info_present = Column(Boolean)
    load_time_ms = Column(Integer)
    raw_findings = Column(JSON)


class Evidence(Base):
    __tablename__ = "evidence"
    id = Column(String, primary_key=True, default=gen_uuid)
    run_id = Column(String, ForeignKey("runs.id"))
    label = Column(String, nullable=False)
    source_type = Column(String, nullable=False)
    source_id = Column(String)
    content = Column(Text, nullable=False)
    metric_count = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)


class Insight(Base):
    __tablename__ = "insights"
    id = Column(String, primary_key=True, default=gen_uuid)
    run_id = Column(String, ForeignKey("runs.id"))
    category = Column(String, nullable=False)
    statement = Column(Text, nullable=False)
    supporting_evidence_ids = Column(JSON)
    confidence = Column(String)


class Recommendation(Base):
    __tablename__ = "recommendations"
    id = Column(String, primary_key=True, default=gen_uuid)
    run_id = Column(String, ForeignKey("runs.id"))
    statement = Column(Text, nullable=False)
    supporting_insight_ids = Column(JSON)
    impact_score = Column(Integer)
    effort_score = Column(Integer)
    priority_rank = Column(Integer)
