from flask import Flask, jsonify, render_template, request
from utils.youtube_api import search_channels, get_channel_stats, get_recent_videos, QuotaExceededError, is_demo_mode
from utils.analytics import aggregate_last_30_days, calculate_growth, infer_niche
from utils.revenue import estimate_revenue, project_next_month, generate_monthly_history

app = Flask(__name__)

# Register general error handlers for custom exceptions
@app.errorhandler(QuotaExceededError)
def handle_quota_exceeded(e):
    return jsonify({
        "error": "quota_exceeded",
        "message": "The YouTube API quota limit has been reached for today. Please try again later."
    }), 403

@app.errorhandler(ValueError)
def handle_value_error(e):
    return jsonify({
        "error": "config_error",
        "message": str(e)
    }), 400

@app.route("/")
def index():
    """Serves the dashboard home page."""
    return render_template("index.html")

@app.route("/api/search")
def search():
    """
    Search endpoint that finds channels matching a query.
    Returns: JSON list of up to 3 channel summaries.
    """
    query = request.args.get("q", "").strip()
    if not query:
        return jsonify([])
        
    try:
        results = search_channels(query)
        return jsonify(results)
    except QuotaExceededError as e:
        return handle_quota_exceeded(e)
    except ValueError as ve:
        return handle_value_error(ve)
    except Exception as e:
        return jsonify({
            "error": "search_failed",
            "message": f"An error occurred during search: {str(e)}"
        }), 500

@app.route("/api/channel/<channel_id>")
def channel_details(channel_id):
    """
    Fetches full analytics data for a selected channel.
    Accepts optional 'niche' query parameter to calculate revenue estimation.
    """
    niche_param = request.args.get("niche", "").strip().lower()
    
    try:
        # 1. Fetch channel profile statistics
        profile = get_channel_stats(channel_id)
        if not profile:
            return jsonify({
                "error": "not_found",
                "message": "Channel was not found or is private."
            }), 404

        # 2. Fetch recent videos (last 60 days to allow growth calculation)
        videos = get_recent_videos(channel_id)

        # 3. Aggregate video analytics for the last 30 days
        analytics_data = aggregate_last_30_days(videos)

        # 4. Calculate growth metrics (subscribers, views, uploads)
        growth_data = calculate_growth(channel_id, videos)

        # 5. Automatically infer the channel's niche from video categories and keywords
        inferred_niche = infer_niche(videos, profile.get("title", ""), profile.get("description", ""))
        
        # Use niche parameter if specified and valid, otherwise fallback to auto-inferred niche
        niche = niche_param if niche_param and niche_param != "auto" else inferred_niche

        # 6. Generate deterministic monthly views history for the last 6 months
        monthly_history = generate_monthly_history(
            channel_id=channel_id,
            total_views=profile.get("total_views", 0),
            recent_views=analytics_data.get("views", 0)
        )

        # 7. Estimate revenues
        country = profile.get("country", "US")
        # Last month estimate (based on total overall views in the last 30 days)
        last_month_min, last_month_max, currency = estimate_revenue(monthly_history[-1], niche, country)

        # Next month projection (using 6 months history and growth trends)
        projection = project_next_month(monthly_history, niche, country)

        # Create detailed monthly history list for the bar chart
        monthly_revenue_history = []
        for m_views in monthly_history:
            m_min, m_max, _ = estimate_revenue(m_views, niche, country)
            monthly_revenue_history.append({
                "views": m_views,
                "min": m_min,
                "max": m_max,
                "avg": round((m_min + m_max) / 2.0, 2)
            })

        # Build response
        response_data = {
            "is_demo": is_demo_mode(),
            "inferred_niche": inferred_niche,
            "profile": profile,
            "last_30_days": {
                "views": monthly_history[-1], # Sync views card to total overall monthly views
                "likes": analytics_data.get("likes", 0),
                "comments": analytics_data.get("comments", 0),
                "uploads": analytics_data.get("uploads", 0),
                "daily_views": analytics_data.get("daily_views", [0]*30)
            },
            "top_videos": analytics_data.get("top_videos", []),
            "revenue": {
                "last_month_min": last_month_min,
                "last_month_max": last_month_max,
                "next_month_min": projection.get("min", 0),
                "next_month_max": projection.get("max", 0),
                "next_month_trend_positive": projection.get("trend_positive", True),
                "monthly_history": monthly_revenue_history,
                "currency": currency
            },
            "growth": {
                "subscribers_delta": growth_data.get("subscribers_delta", 0.0),
                "views_delta_pct": growth_data.get("views_delta_pct", 0.0),
                "uploads_this_month": growth_data.get("uploads_this_month", 0),
                "uploads_delta_pct": growth_data.get("uploads_delta_pct", 0.0)
            }
        }

        return jsonify(response_data)

    except QuotaExceededError as e:
        return handle_quota_exceeded(e)
    except ValueError as ve:
        return handle_value_error(ve)
    except Exception as e:
        return jsonify({
            "error": "server_error",
            "message": f"An error occurred while fetching details: {str(e)}"
        }), 500

if __name__ == "__main__":
    # Start the Flask development server on port 5000
    app.run(debug=True, port=5000)
