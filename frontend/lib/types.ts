export type Business = {
  id: string
  name: string
  category: string | null
  address: string | null
  latitude: number | null
  longitude: number | null
  rating: number | null
  review_count: number | null
  price_level: number | null
  website: string | null
  phone: string | null
  is_target: boolean
}

export type Review = {
  id: string
  author: string | null
  rating: number | null
  text: string | null
  sentiment: string | null
  topics: string[]
}

export type WebsiteAudit = {
  has_online_ordering: boolean | null
  has_menu_pricing: boolean | null
  mobile_friendly: boolean | null
  seo_title: string | null
  contact_info_present: boolean | null
  load_time_ms: number | null
}

export type Insight = {
  id: string
  category: string
  statement: string
  supporting_evidence_ids: string[]
  confidence: string
}

export type Recommendation = {
  id: string
  statement: string
  supporting_insight_ids: string[]
  impact_score: number
  effort_score: number
  priority_rank: number
}

export type Evidence = {
  id: string
  label: string
  source_type: string
  content: string
  metric_count: number | null
}

export type RunReport = {
  run_id: string
  query: string
  location: string | null
  category: string | null
  status: string
  target_business: Business | null
  competitors: Business[]
  reviews: Review[]
  website_audit: WebsiteAudit | null
  insights: Insight[]
  recommendations: Recommendation[]
  evidence_count: number
}

export type AgentEvent = {
  node: string
  status: "started" | "completed" | "failed" | "skipped"
  detail: string
}
