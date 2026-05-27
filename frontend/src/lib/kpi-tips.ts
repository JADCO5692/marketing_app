/**
 * Central KPI tooltip dictionary.
 * Every label with data-tip="KEY" in the UI renders this tooltip.
 * AGENTS.md §0.3: add key here FIRST before adding data-tip to any component.
 */
export const KPI_TIPS: Record<string, { title: string; body: string }> = {
  icp_score: {
    title: "ICP Score",
    body: "Ideal Customer Profile fit score (0–100). Higher means the lead closely matches the target customer. 70+ is Hot, 40–70 Warm, below 40 Cold.",
  },
  intent_score: {
    title: "Intent Score",
    body: "Signals of active buying intent (0–100). Based on hiring activity, funding news, tool-switching signals, and recent company news.",
  },
  engagement_readiness: {
    title: "Engagement Readiness",
    body: "Likelihood of responding to a cold outreach (0–100). Based on seniority, email validity, company activity, and decision-maker status.",
  },
  email_verified: {
    title: "Email Verified",
    body: "Whether the email address has been confirmed deliverable by Hunter.io. Only verified emails should be used in campaigns.",
  },
  email_deliverability: {
    title: "Email Deliverability",
    body: "'deliverable' means the email can receive mail. 'risky' means uncertain. 'undeliverable' means the address will bounce.",
  },
  is_decision_maker: {
    title: "Decision Maker",
    body: "Whether this contact has authority to make purchasing decisions, inferred from job title and seniority level.",
  },
  budget_authority: {
    title: "Budget Authority",
    body: "Whether this contact likely controls or influences budget, based on title (e.g. CFO, VP Finance, Director).",
  },
  seniority_level: {
    title: "Seniority Level",
    body: "Normalised seniority: C-Suite, VP, Director, Manager, or IC (Individual Contributor).",
  },
  campaign_type_match: {
    title: "Campaign Type",
    body: "Best-fit campaign for this lead: educational (awareness), demo (product interest), case_study (proof), offer (incentive), or nurture (long-cycle).",
  },
  research_status: {
    title: "Research Status",
    body: "Whether the company has been researched. 'pending' = not yet started, 'done' = fully enriched.",
  },
  funding_stage: {
    title: "Funding Stage",
    body: "Investment stage of the company: Bootstrap, Seed, Series A/B/C+, or Public. Useful for sizing and budget-readiness signals.",
  },
  company_size: {
    title: "Company Size",
    body: "SME = 1–200 employees, Mid-market = 200–1000, Enterprise = 1000+. Affects deal size and buying process complexity.",
  },
  hiring_velocity: {
    title: "Hiring Velocity",
    body: "How actively the company is hiring: High (10+ open roles), Medium, Low, or None. A strong growth signal.",
  },
  website_quality_score: {
    title: "Website Quality",
    body: "Score 0–10 for the quality of the company's website: design, content depth, and professional appearance.",
  },
  social_presence_score: {
    title: "Social Presence",
    body: "Score 0–10 for how active and established the company is on social media and professional networks.",
  },
  lead_count: {
    title: "Lead Count",
    body: "Number of leads currently matching this segment's filter rules.",
  },
}
