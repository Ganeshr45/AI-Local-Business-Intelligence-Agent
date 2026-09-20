from app.agents.state import BusinessIntelState, make_evidence, emit_event
from app.tools import scraper


def _describe_audit(audit: dict) -> str:
    if audit.get("fetch_failed"):
        return "Website could not be reached for analysis"
    parts = []
    parts.append("has online ordering" if audit.get("has_online_ordering") else "no online ordering detected")
    parts.append("has menu/pricing info" if audit.get("has_menu_pricing") else "no visible menu or pricing")
    parts.append("mobile friendly" if audit.get("mobile_friendly") else "not confirmed mobile friendly")
    parts.append("contact info present" if audit.get("contact_info_present") else "no clear contact info")
    if audit.get("load_time_ms") is not None:
        parts.append(f"loaded in {audit['load_time_ms']}ms")
    return ", ".join(parts)


def website_analyzer_node(state: BusinessIntelState) -> BusinessIntelState:
    emit_event(state, "website_analyzer", "started")

    target = state["target_business"]
    website = target.get("website") if target else None

    if not website:
        state["errors"].append("No website found for the target business, website audit unavailable")
        emit_event(state, "website_analyzer", "skipped", "no website")
        return state

    fetch_result = scraper.fetch(website)
    audit = scraper.analyze(fetch_result)
    state["website_audit"] = audit

    state["evidence"].append(make_evidence("FACT", "website_scrape", website, _describe_audit(audit)))

    emit_event(state, "website_analyzer", "completed")
    return state
