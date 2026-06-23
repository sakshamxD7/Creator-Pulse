import random

CPM_RATES = {
    "tech": (6.0, 10.0),
    "gaming": (3.0, 6.0),
    "finance": (10.0, 20.0),
    "lifestyle": (2.0, 5.0),
    "education": (4.0, 8.0),
    "india_general": (0.8, 2.0),
    "entertainment": (2.0, 4.0)
}

# CPM multipliers to scale Western standard CPMs down to local market realities
COUNTRY_CPM_MULTIPLIERS = {
    "IN": 0.20,      # Indian CPM is roughly 20% of US rates
    "US": 1.00,      # Baseline (United States)
    "GB": 0.90,      # United Kingdom
    "CA": 0.92,      # Canada
    "AU": 0.95,      # Australia
    "DE": 0.85,      # Germany
}

def estimate_revenue(views, niche, country="US"):
    """
    Estimates minimum and maximum revenue based on views, niche CPM, and country.
    Applies country-specific CPM multipliers and converts currency:
    - If IN: scales CPM by 0.20, converts USD to INR (83x), uses ₹ symbol
    - Else: uses standard CPM scale, outputs in USD, uses $ symbol
    """
    if niche not in CPM_RATES:
        niche = "india_general"  # Safe fallback
        
    cpm_min, cpm_max = CPM_RATES[niche]
    
    # Apply country CPM multiplier (defaults to 1.0 if not listed)
    country_code = country.upper() if country else "US"
    multiplier = COUNTRY_CPM_MULTIPLIERS.get(country_code, 1.0)
    
    cpm_min_usd = cpm_min * multiplier
    cpm_max_usd = cpm_max * multiplier
    
    # Calculate revenue in USD first
    min_revenue_usd = (views / 1000.0) * cpm_min_usd
    max_revenue_usd = (views / 1000.0) * cpm_max_usd
    
    # Perform currency conversion if country is India
    if country_code == "IN":
        USD_TO_INR = 83.0
        min_revenue = min_revenue_usd * USD_TO_INR
        max_revenue = max_revenue_usd * USD_TO_INR
        currency = {"symbol": "₹", "code": "INR"}
    else:
        min_revenue = min_revenue_usd
        max_revenue = max_revenue_usd
        currency = {"symbol": "$", "code": "USD"}
        
    return round(min_revenue, 2), round(max_revenue, 2), currency

def project_next_month(monthly_views_history, niche, country="US"):
    """
    Projects next month's views and estimates revenue.
    Takes average of the last 3 months views, applies a 10% trend factor 
    if the last month views grew compared to the previous month, and runs 
    through estimate_revenue.
    Returns: { min, max, trend_positive }
    """
    if not monthly_views_history or len(monthly_views_history) < 2:
        min_rev, max_rev, _ = estimate_revenue(0, niche, country)
        return {"min": min_rev, "max": max_rev, "trend_positive": True}
        
    last_3_months = monthly_views_history[-3:]
    avg_views = sum(last_3_months) / len(last_3_months)
    
    trend_positive = monthly_views_history[-1] > monthly_views_history[-2]
    
    if trend_positive:
        projected_views = avg_views * 1.10
    else:
        projected_views = avg_views
        
    min_proj, max_proj, _ = estimate_revenue(projected_views, niche, country)
    
    return {
        "min": min_proj,
        "max": max_proj,
        "trend_positive": trend_positive
    }

def generate_monthly_history(channel_id, total_views, recent_views):
    """
    Generates a deterministic but realistic history of monthly views for the last 6 months
    based on the channel ID, total views, and views from the last 30 days.
    """
    import hashlib
    # Use stable, process-independent seed based on MD5 of channel ID
    h = int(hashlib.md5(channel_id.encode("utf-8")).hexdigest(), 16) % 2**32
    rng = random.Random(h)
    
    # Estimate baseline monthly views
    if recent_views > 0:
        # Anchor baseline to recent performance (adding 15% to 30% for legacy videos)
        baseline = recent_views * rng.uniform(1.15, 1.30)
    else:
        # Fallback if no recent uploads (estimate views based on total views / channel age in months)
        channel_age_months = rng.uniform(48.0, 96.0)
        baseline = total_views / channel_age_months
        
    # Ensure baseline is within reasonable bounds
    baseline = max(baseline, 500)
    baseline = min(baseline, total_views / 6.0)  # Ceiling
        
    monthly_history = []
    # Random but stable trend direction (slight growth, decline, or flat)
    trend = rng.choice([-0.02, 0.0, 0.03, 0.06])
    
    for i in range(6):
        # Trend scaling over 6 months
        trend_factor = 1.0 + (i - 2.5) * trend
        # Add random fluctuations (from -8% to +8%)
        fluctuation = rng.uniform(0.92, 1.08)
        views = int(baseline * trend_factor * fluctuation)
        views = max(views, 100)  # Floor views
        monthly_history.append(views)
        
    # Set the most recent month (index 5) to represent the total overall views of the last 30 days
    if recent_views > 0:
        monthly_history[-1] = int(recent_views * rng.uniform(1.15, 1.25))
    else:
        monthly_history[-1] = int(baseline)
        
    return monthly_history
