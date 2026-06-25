<img width="1919" height="955" alt="image" src="https://github.com/user-attachments/assets/d6d3c808-aac8-4d9c-a458-3c572b654be8" /># YouTube Channel Analytics Dashboard

> **Live Demo → [creator-pulse1.onrender.com](https://creator-pulse1.onrender.com/)**

A Flask-powered analytics tool that pulls live data from the YouTube Data API v3 to give a full picture of any public channel — views, engagement, growth trends, niche detection, and revenue estimates. Includes a full **Demo Mode** that works without an API key.

---

## Screenshots

Channel Analytics
 *<img width="1919" height="946" alt="image" src="https://github.com/user-attachments/assets/7709108e-d311-4646-8bf2-eb78ac67bb5e" />

 Revenue Estimation
 *<img width="1919" height="955" alt="image" src="https://github.com/user-attachments/assets/c8df957c-78cc-43d1-8b53-30f66b7b3537" />


---

## Features

**Channel Search** — Search any public YouTube channel by name. Returns top 3 matching results with thumbnails and subscriber counts.

**30-Day Analytics** — Views, likes, comments, and upload count for the last 30 days. Daily views chart built from per-video publish dates.

**Growth Metrics** — Month-over-month delta for views, uploads, and a deterministic subscriber growth estimate (since YouTube's public API doesn't expose historical subscriber data).

**Auto Niche Detection** — Infers channel niche (Tech, Gaming, Finance, Lifestyle, Education, Entertainment) from YouTube category IDs and keyword scanning across video titles, channel title, and description.

**Revenue Estimation** — CPM-based revenue range for last month and a projected next-month forecast. Niche-specific CPM bands applied with country multipliers — Indian channels output in ₹ (INR), others in $ (USD).

**6-Month View History** — Deterministic synthetic history anchored to real recent views, seeded by channel ID for consistency across requests.

**Demo Mode** — No API key? The app runs on pre-loaded mock data for MKBHD, MrBeast, and T-Series automatically.

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        CLIENT (Browser)                         │
│              Single-page HTML + Vanilla JS + Charts             │
└───────────────────┬──────────────────┬──────────────────────────┘
                    │ GET /api/search   │ GET /api/channel/<id>
                    ▼                  ▼
┌─────────────────────────────────────────────────────────────────┐
│                      FLASK APPLICATION (app.py)                  │
│                                                                 │
│  Routes                                                         │
│  ├── GET /                    → index.html                      │
│  ├── GET /api/search?q=       → top 3 channel results           │
│  └── GET /api/channel/<id>    → full analytics payload          │
│       │                                                         │
│       ├── 1. get_channel_stats()   → profile + lifetime stats   │
│       ├── 2. get_recent_videos()   → last 60 days of videos     │
│       ├── 3. aggregate_last_30_days() → views/likes/comments    │
│       ├── 4. calculate_growth()    → MoM delta metrics          │
│       ├── 5. infer_niche()         → category + keyword scan    │
│       ├── 6. generate_monthly_history() → 6-month view history  │
│       └── 7. estimate_revenue() + project_next_month()          │
│                                                                 │
│  Demo Mode (no API key)                                         │
│  └── All API calls swapped to mock data (MKBHD, MrBeast, T-Series) │
└───────────────────┬─────────────────────────────────────────────┘
                    │  google-api-python-client
                    ▼
┌─────────────────────────────────────────────────────────────────┐
│               YouTube Data API v3 (Google)                      │
│  search.list → channels.list → search.list (videos)            │
│              → videos.list (statistics + snippet)               │
└─────────────────────────────────────────────────────────────────┘
```

---

## Revenue Model

| Niche | CPM Range (USD) |
|---|---|
| Finance | $10 – $20 |
| Tech | $6 – $10 |
| Education | $4 – $8 |
| Gaming | $3 – $6 |
| Entertainment | $2 – $4 |
| Lifestyle | $2 – $5 |
| India General | $0.8 – $2 |

Country multipliers applied on top (e.g. India = 20% of US CPM). Indian channels auto-convert to ₹ at ₹83/USD.

Next-month projection = 3-month rolling average × 1.10 if the trend is positive.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.12, Flask |
| YouTube Data | google-api-python-client |
| Config | python-dotenv |
| Frontend | Vanilla HTML/CSS/JS, Chart.js |

---

## Project Structure

```
youtube-analytics/
├── app.py                   # Flask routes + error handlers
├── requirements.txt
├── .env                     # YOUTUBE_API_KEY (gitignored)
├── utils/
│   ├── youtube_api.py       # API client, search, channel stats, video fetch, demo mock data
│   ├── analytics.py         # 30-day aggregation, growth calc, niche inference
│   └── revenue.py           # CPM bands, country multipliers, projections
├── templates/
│   └── index.html           # Single-page dashboard
└── static/
    ├── css/style.css
    └── js/main.js
```

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/search?q=<query>` | Returns top 3 matching channels |
| `GET` | `/api/channel/<channel_id>` | Returns full analytics payload for a channel |
| `GET` | `/api/channel/<id>?niche=finance` | Override auto-detected niche for revenue calc |

---

## Run Locally

```bash
git clone https://github.com/YOUR_USERNAME/youtube-analytics.git
cd youtube-analytics
pip install -r requirements.txt
```

Add your API key to `.env`:
```
YOUTUBE_API_KEY=your_key_here
```

> No key? Skip this step — the app runs in Demo Mode automatically.

```bash
python app.py
# → http://localhost:5000
```

Get a free API key at [console.cloud.google.com](https://console.cloud.google.com) → Enable **YouTube Data API v3** → Create credentials.

> **Quota note:** The YouTube Data API has a daily quota of 10,000 units. A full channel analysis uses ~103 units (search + channels + videos list calls).

---

## Author

**Saksham Jangir**  
B.Tech CSE (Data Analytics) — JECRC University, Jaipur  
[LinkedIn](https://linkedin.com/in/YOUR_PROFILE) · [GitHub](https://github.com/YOUR_USERNAME)
