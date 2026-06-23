// CreatorPulse JavaScript Application Logic

// Global State
let currentChannelId = null;
let currentNiche = "tech";
let currentChannelData = null;
let currentCurrency = { symbol: "₹", code: "INR" };

// Chart Instances
let viewsLineChartInstance = null;
let engagementDoughnutChartInstance = null;
let revenueBarChartInstance = null;

/**
 * Reset dashboard back to hero search state
 */
function resetDashboard() {
    currentChannelId = null;
    currentChannelData = null;
    
    // UI elements toggle
    document.getElementById("dashboard-content").style.display = "none";
    document.getElementById("topbar-search-container").style.display = "none";
    
    document.getElementById("hero-search-section").style.display = "flex";
    document.getElementById("hero-search-input").value = "";
    document.getElementById("search-results-container").style.display = "none";
    document.getElementById("search-results-grid").innerHTML = "";
}

/**
 * Shows/Hides the Loading Spinner
 */
function toggleLoading(show) {
    const spinner = document.getElementById("loading-spinner");
    spinner.style.display = show ? "flex" : "none";
}

/**
 * Handles API and network errors by showing error modal
 */
function showError(title, message) {
    document.getElementById("error-title").textContent = title;
    document.getElementById("error-message").textContent = message;
    document.getElementById("error-overlay").style.display = "flex";
}

function closeErrorOverlay() {
    document.getElementById("error-overlay").style.display = "none";
}

/**
 * Helper to format numbers with Indian numbering style (en-IN)
 */
function formatNumber(num) {
    if (num === null || num === undefined || isNaN(num)) return "0";
    return Number(num).toLocaleString("en-IN");
}

/**
 * Helper to format currency
 */
function formatCurrency(amount) {
    if (amount === null || amount === undefined || isNaN(amount)) {
        return currentCurrency.symbol + "0.00";
    }
    const locale = currentCurrency.code === "INR" ? "en-IN" : "en-US";
    return currentCurrency.symbol + Number(amount).toLocaleString(locale, { minimumFractionDigits: 2, maximumFractionDigits: 2 });
}

/**
 * Submits search query to the API
 */
async function handleSearch(event, inputId) {
    event.preventDefault();
    const query = document.getElementById(inputId).value.trim();
    if (!query) return;

    toggleLoading(true);
    try {
        const response = await fetch(`/api/search?q=${encodeURIComponent(query)}`);
        
        if (!response.ok) {
            const errData = await response.json();
            if (response.status === 403) {
                showError("Quota Exceeded", errData.message || "YouTube API quota limit reached.");
            } else {
                showError("Search Failed", errData.message || "Failed to search channels.");
            }
            toggleLoading(false);
            return;
        }

        const data = await response.json();
        
        // Transition back to search view by hiding dashboard and showing hero section
        document.getElementById("dashboard-content").style.display = "none";
        document.getElementById("topbar-search-container").style.display = "none";
        document.getElementById("hero-search-section").style.display = "flex";
        
        // Sync search inputs
        if (inputId === "topbar-search-input") {
            document.getElementById("hero-search-input").value = query;
        } else {
            document.getElementById("topbar-search-input").value = query;
        }

        renderSearchResults(data);
    } catch (err) {
        showError("Connection Error", "Could not connect to the server. Please try again.");
    } finally {
        toggleLoading(false);
    }
}

/**
 * Renders the top 3 channel results in the UI
 */
function renderSearchResults(channels) {
    const container = document.getElementById("search-results-container");
    const grid = document.getElementById("search-results-grid");
    grid.innerHTML = "";

    if (!channels || channels.length === 0) {
        grid.innerHTML = `
            <div style="grid-column: 1 / -1; padding: 20px;" class="card">
                <p style="color: var(--text-muted);">No channels found matching that name. Try a different query.</p>
            </div>
        `;
        container.style.display = "block";
        return;
    }

    channels.forEach(ch => {
        const card = document.createElement("div");
        card.className = "channel-search-card";
        card.onclick = () => selectChannel(ch.channel_id);
        
        card.innerHTML = `
            <img class="avatar" src="${ch.thumbnail}" alt="${ch.title}">
            <h4 class="name">${ch.title}</h4>
            <p class="subs">${formatNumber(ch.subscriber_count)} subscribers</p>
        `;
        grid.appendChild(card);
    });

    container.style.display = "block";
    
    // Smooth scroll to results
    container.scrollIntoView({ behavior: "smooth" });
}

/**
 * Selects a channel and pulls details to render the dashboard
 */
async function selectChannel(channelId) {
    currentChannelId = channelId;
    currentNiche = document.getElementById("niche-select").value;

    toggleLoading(true);
    try {
        const response = await fetch(`/api/channel/${channelId}?niche=${currentNiche}`);
        
        if (!response.ok) {
            const errData = await response.json();
            if (response.status === 403) {
                showError("Quota Exceeded", errData.message || "YouTube API quota limit reached.");
            } else {
                showError("Error Fetching Channel", errData.message || "Could not retrieve channel details.");
            }
            toggleLoading(false);
            return;
        }

        const data = await response.json();
        currentChannelData = data;
        
        renderDashboard(data);
    } catch (err) {
        showError("Connection Error", "Could not load channel analytics. Check your connection.");
    } finally {
        toggleLoading(false);
    }
}

/**
 * Triggered when the user changes the niche dropdown selection
 */
async function onNicheChange() {
    if (!currentChannelId) return;
    
    currentNiche = document.getElementById("niche-select").value;
    toggleLoading(true);
    
    try {
        const response = await fetch(`/api/channel/${currentChannelId}?niche=${currentNiche}`);
        if (!response.ok) {
            const errData = await response.json();
            showError("Update Failed", errData.message || "Could not update niche estimates.");
            toggleLoading(false);
            return;
        }
        
        const data = await response.json();
        currentChannelData.revenue = data.revenue;
        
        // Update ONLY the revenue elements
        updateRevenueUI(data.revenue);
    } catch (err) {
        showError("Connection Error", "Could not fetch updated niche data.");
    } finally {
        toggleLoading(false);
    }
}

/**
 * Updates the revenue metric cards and history bar chart
 */
function updateRevenueUI(revenueData) {
    if (revenueData.currency) {
        currentCurrency = revenueData.currency;
    }
    // 30D Revenue card range display
    const rangeText = `${formatCurrency(revenueData.last_month_min)} - ${formatCurrency(revenueData.last_month_max)}`;
    document.getElementById("card-revenue-range").textContent = rangeText;
    document.getElementById("revenue-30d-display").textContent = rangeText;
    
    // Projection card
    document.getElementById("revenue-projection-display").textContent = 
        `${formatCurrency(revenueData.next_month_min)} - ${formatCurrency(revenueData.next_month_max)}`;
        
    // Trend indicator update
    const trendIndicator = document.getElementById("revenue-trend-indicator");
    if (revenueData.next_month_trend_positive) {
        trendIndicator.className = "badge-success";
        trendIndicator.innerHTML = `
            <svg class="trend-arrow" xmlns="http://www.w3.org/2000/svg" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" viewBox="0 0 24 24" width="14" height="14">
                <line x1="12" y1="19" x2="12" y2="5"></line>
                <polyline points="5 12 12 5 19 12"></polyline>
            </svg>
            <span>UPWARD</span>
        `;
    } else {
        trendIndicator.className = "badge-danger";
        trendIndicator.innerHTML = `
            <svg class="trend-arrow" xmlns="http://www.w3.org/2000/svg" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" viewBox="0 0 24 24" width="14" height="14">
                <line x1="12" y1="5" x2="12" y2="19"></line>
                <polyline points="19 12 12 19 5 12"></polyline>
            </svg>
            <span>DOWNWARD</span>
        `;
    }
    
    // Recreate the Revenue Bar Chart
    createRevenueBarChart(revenueData.monthly_history);
}

/**
 * Populates all dashboard elements with the retrieved channel details
 */
function renderDashboard(data) {
    // Hide Hero, Show dashboard and topbar search
    document.getElementById("hero-search-section").style.display = "none";
    document.getElementById("dashboard-content").style.display = "block";
    
    const topbarSearch = document.getElementById("topbar-search-container");
    topbarSearch.style.display = "block";
    document.getElementById("topbar-search-input").value = "";

    // Toggle demo warning banner
    const demoBanner = document.getElementById("demo-banner");
    if (data.is_demo) {
        demoBanner.style.display = "flex";
    } else {
        demoBanner.style.display = "none";
    }

    // Set dropdown value to the auto-inferred niche
    if (data.inferred_niche) {
        document.getElementById("niche-select").value = data.inferred_niche;
    }

    // 1. Channel Profile Card
    document.getElementById("channel-profile-img").src = data.profile.thumbnail;
    document.getElementById("channel-title").textContent = data.profile.title;
    document.getElementById("channel-country").textContent = data.profile.country;
    document.getElementById("channel-desc").textContent = data.profile.description || "No description provided.";
    
    document.getElementById("quick-stat-subscribers").textContent = formatNumber(data.profile.subscriber_count);
    document.getElementById("quick-stat-views").textContent = formatNumber(data.profile.total_views);
    document.getElementById("quick-stat-videos").textContent = formatNumber(data.profile.video_count);

    // 2. Stat Cards Grid
    document.getElementById("card-views-count").textContent = formatNumber(data.last_30_days.views);
    document.getElementById("card-likes-count").textContent = formatNumber(data.last_30_days.likes);
    document.getElementById("card-subs-count").textContent = `+${formatNumber(data.last_30_days.views * 0.005)} / mo`; // Estimated subs delta rate
    
    // Delta Badges in Stat Cards
    const viewsBadge = document.getElementById("card-views-badge");
    const likesBadge = document.getElementById("card-likes-badge");
    const subsBadge = document.getElementById("card-subs-badge");
    const revBadge = document.getElementById("card-revenue-badge");
    
    updateDeltaBadge(viewsBadge, data.growth.views_delta_pct);
    updateDeltaBadge(likesBadge, data.growth.views_delta_pct * 0.9); // Approximate likes delta with views
    updateDeltaBadge(subsBadge, data.growth.subscribers_delta);
    updateDeltaBadge(revBadge, data.growth.views_delta_pct); // Revenue matches views growth

    // 3. Growth Comparison row
    const subPctEl = document.getElementById("growth-subs-pct");
    const viewsPctEl = document.getElementById("growth-views-pct");
    
    subPctEl.textContent = formatPercentage(data.growth.subscribers_delta);
    subPctEl.className = data.growth.subscribers_delta >= 0 ? "growth-pct-number text-success" : "growth-pct-number text-danger";
    
    viewsPctEl.textContent = formatPercentage(data.growth.views_delta_pct);
    viewsPctEl.className = data.growth.views_delta_pct >= 0 ? "growth-pct-number text-success" : "growth-pct-number text-danger";
    
    document.getElementById("growth-uploads-count").textContent = data.growth.uploads_this_month;
    const uploadsBadge = document.getElementById("growth-uploads-pct");
    updateDeltaBadge(uploadsBadge, data.growth.uploads_delta_pct);

    // 4. Update Revenue Cards & History chart
    updateRevenueUI(data.revenue);

    // 5. Build and populate top videos table
    populateTopVideosTable(data.top_videos);

    // 6. Draw 30-day views line chart and engagement doughnut
    createViewsLineChart(data.last_30_days.daily_views);
    createEngagementDoughnutChart(data.last_30_days.likes, data.last_30_days.comments);
    
    // Scroll to the top of dashboard smoothly
    window.scrollTo({ top: 0, behavior: "smooth" });
}

/**
 * Formats delta percentages nicely
 */
function formatPercentage(val) {
    const sign = val >= 0 ? "+" : "";
    return `${sign}${val.toFixed(2)}%`;
}

/**
 * Updates small status badges (green for positive, red for negative)
 */
function updateDeltaBadge(badgeEl, value) {
    const sign = value >= 0 ? "+" : "";
    badgeEl.textContent = `${sign}${value.toFixed(1)}%`;
    if (value >= 0) {
        badgeEl.className = "badge-success";
    } else {
        badgeEl.className = "badge-danger";
    }
}

/**
 * Populates top uploads table
 */
function populateTopVideosTable(videos) {
    const tbody = document.getElementById("top-videos-tbody");
    tbody.innerHTML = "";

    if (!videos || videos.length === 0) {
        const template = document.getElementById("empty-state-template");
        const clone = template.content.cloneNode(true);
        const row = document.createElement("tr");
        const cell = document.createElement("td");
        cell.colSpan = 8;
        cell.appendChild(clone);
        row.appendChild(cell);
        tbody.appendChild(row);
        return;
    }

    videos.forEach((video, index) => {
        const tr = document.createElement("tr");
        
        // Style engagement rate badges
        let erClass = "er-low";
        if (video.engagement_rate > 3.0) {
            erClass = "er-high";
        } else if (video.engagement_rate >= 1.0) {
            erClass = "er-mid";
        }

        tr.innerHTML = `
            <td class="rank-column text-center">${index + 1}</td>
            <td><img class="video-thumbnail" src="${video.thumbnail}" alt="Video Thumbnail"></td>
            <td><div class="video-title-text" title="${video.title}">${video.title}</div></td>
            <td class="text-right">${formatNumber(video.views)}</td>
            <td class="text-right">${formatNumber(video.likes)}</td>
            <td class="text-right">${formatNumber(video.comments)}</td>
            <td class="text-center">
                <span class="badge-er ${erClass}">${video.engagement_rate.toFixed(2)}%</span>
            </td>
            <td>${video.published_at}</td>
        `;
        tbody.appendChild(tr);
    });
}

/**
 * Generates last 30 days labels relative to today
 */
function getLast30DaysLabels() {
    const labels = [];
    const today = new Date();
    for (let i = 29; i >= 0; i--) {
        const d = new Date(today.getFullYear(), today.getMonth(), today.getDate() - i);
        // Returns "Jun 22" style label
        labels.push(d.toLocaleDateString("en-US", { month: "short", day: "numeric" }));
    }
    return labels;
}

/**
 * Generates last 6 months labels relative to today
 */
function getLast6MonthsLabels() {
    const monthNames = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
    const labels = [];
    const today = new Date();
    for (let i = 5; i >= 0; i--) {
        const d = new Date(today.getFullYear(), today.getMonth() - i, 1);
        labels.push(monthNames[d.getMonth()]);
    }
    return labels;
}

/* ==========================================================================
   CHART.JS UTILITIES
   ========================================================================== */

/**
 * Draw Views - Last 30 days line chart
 */
function createViewsLineChart(dailyViews) {
    if (viewsLineChartInstance) {
        viewsLineChartInstance.destroy();
    }

    const ctx = document.getElementById("viewsLineChart").getContext("2d");
    
    // Create fill gradient (Red from top)
    const fillGradient = ctx.createLinearGradient(0, 0, 0, 300);
    fillGradient.addColorStop(0, "rgba(238, 28, 37, 0.35)");
    fillGradient.addColorStop(1, "rgba(238, 28, 37, 0.0)");

    viewsLineChartInstance = new Chart(ctx, {
        type: "line",
        data: {
            labels: getLast30DaysLabels(),
            datasets: [{
                label: "Views",
                data: dailyViews,
                borderColor: "#ee1c25", // Red stroke
                borderWidth: 2.5,
                backgroundColor: fillGradient, // Red gradient fill
                fill: true,
                tension: 0.35,
                pointBackgroundColor: "#ee1c25",
                pointBorderColor: "#ffffff",
                pointBorderWidth: 1.5,
                pointRadius: 3,
                pointHoverRadius: 5
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false }
            },
            scales: {
                y: {
                    grid: { color: "rgba(44, 49, 84, 0.05)" },
                    ticks: {
                        color: "#7f839b",
                        callback: function(value) {
                            return value >= 1000 ? (value / 1000) + "k" : value;
                        }
                    }
                },
                x: {
                    grid: { display: false },
                    ticks: { color: "#7f839b", maxRotation: 45 }
                }
            }
        }
    });
}

/**
 * Draw Engagement Breakdown doughnut chart
 */
function createEngagementDoughnutChart(likes, comments) {
    if (engagementDoughnutChartInstance) {
        engagementDoughnutChartInstance.destroy();
    }

    const ctx = document.getElementById("engagementDoughnutChart").getContext("2d");

    // Standard fallback if both are 0
    const dataValues = (likes === 0 && comments === 0) ? [1, 0] : [likes, comments];
    const labels = (likes === 0 && comments === 0) ? ["No Data Available", ""] : ["Likes", "Comments"];

    engagementDoughnutChartInstance = new Chart(ctx, {
        type: "doughnut",
        data: {
            labels: labels,
            datasets: [{
                data: dataValues,
                backgroundColor: ["#ee1c25", "#374151"], // Red and Slate Charcoal
                borderColor: "#ffffff",
                borderWidth: 2,
                hoverOffset: 6
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: "bottom",
                    labels: { color: "#7f839b", boxWidth: 12 }
                }
            },
            cutout: "68%"
        }
    });
}

/**
 * Draw 6-Month Historical Revenue Estimate Bar Chart
 */
function createRevenueBarChart(monthlyHistory) {
    if (revenueBarChartInstance) {
        revenueBarChartInstance.destroy();
    }

    const ctx = document.getElementById("revenueBarChart").getContext("2d");
    
    const minValues = monthlyHistory.map(item => item.min);
    const maxValues = monthlyHistory.map(item => item.max);

    revenueBarChartInstance = new Chart(ctx, {
        type: "bar",
        data: {
            labels: getLast6MonthsLabels(),
            datasets: [
                {
                    label: "Min Estimate (" + currentCurrency.symbol + ")",
                    data: minValues,
                    backgroundColor: "#ee1c25", // Red
                    borderRadius: 4
                },
                {
                    label: "Max Estimate (" + currentCurrency.symbol + ")",
                    data: maxValues,
                    backgroundColor: "#9ca3af", // Slate Silver
                    borderRadius: 4
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: "top",
                    labels: { color: "#7f839b", boxWidth: 12 }
                }
            },
            scales: {
                y: {
                    grid: { color: "rgba(44, 49, 84, 0.05)" },
                    ticks: {
                        color: "#7f839b",
                        callback: function(value) {
                            return "₹" + (value >= 1000 ? (value / 1000) + "k" : value);
                        }
                    }
                },
                x: {
                    grid: { display: false },
                    ticks: { color: "#7f839b" }
                }
            }
        }
    });
}
