BRIEF_PROMPT = """Given company={company}, competitor={competitor}, and these market signals: {signals_json}, produce a JSON object with:
- summary: 2-3 sentence strategic summary of competitor threat level
- signals: the top 5 most impactful signals (reuse input format)
- actions: 3 specific actions the sales/product team should take this week or month
Always return valid JSON only, no markdown."""

PRIORITIZE_PROMPT = """Given company={company} trying to close accounts={accounts_json}, and these signals={signals_json}, rank each account by buying likelihood this quarter. Return JSON array of {{ name, score (0-100), reason (1 sentence), signals (top 2 relevant signals) }}. JSON only."""

BATTLECARD_PROMPT = """Given company={company} competing against {competitor} with these signals={signals_json}, write a sales battle card in markdown. Sections: Overview (2 sentences), Their Strengths (3 bullets), Their Weaknesses (3 bullets, from review/signal data), Our Angle (how to position against them), Objection Handlers (2 common objections + responses). Be specific and actionable."""
