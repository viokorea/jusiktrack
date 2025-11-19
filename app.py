import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta

# Set page config
st.set_page_config(page_title="Stock Portfolio Competition", layout="wide")

# Constants
START_DATE_DK = "2025-10-07"
START_DATE_JS = "2025-03-01"
EARLIEST_DATE = "2025-03-01" # For fetching data
TODAY = datetime.now().strftime("%Y-%m-%d")

# Portfolios
PORTFOLIO_DK = {
    "QQQM": 0.45,
    "SMH": 0.15,
    "SPYM": 0.10,
    "JEPQ": 0.10,
    "IAU": 0.10,
    "DBMF": 0.10
}

PORTFOLIO_JS = {
    "SCHD": 0.33,
    "SPYM": 0.67
}

INDICES = {
    "KOSPI": "^KS11",
    "NASDAQ": "^IXIC",
    "S&P 500": "^GSPC"
}

@st.cache_data
def fetch_data(tickers, start_date):
    data = yf.download(tickers, start=start_date, progress=False)['Close']
    return data

def calculate_portfolio_performance(data, portfolio, start_date):
    # Filter data for the portfolio tickers
    portfolio_data = data[list(portfolio.keys())].copy()
    
    # Filter by start date
    portfolio_data = portfolio_data[portfolio_data.index >= start_date]
    
    # Normalize to start date = 1.0 (or 100%)
    # We need to handle missing data (e.g. holidays) by forward filling
    portfolio_data = portfolio_data.ffill().bfill()
    
    if portfolio_data.empty:
        return pd.Series()

    normalized_data = portfolio_data / portfolio_data.iloc[0]
    
    # Calculate weighted sum
    portfolio_value = pd.Series(0, index=normalized_data.index)
    for ticker, weight in portfolio.items():
        portfolio_value += normalized_data[ticker] * weight
        
    return portfolio_value

def main():
    st.title("📈 Stock Portfolio Competition: DK vs JS")
    st.write(f"Tracking performance from **{START_DATE_JS}** (JS) and **{START_DATE_DK}** (DK) to **{TODAY}**")

    # Collect all tickers
    all_tickers = list(PORTFOLIO_DK.keys()) + list(PORTFOLIO_JS.keys()) + list(INDICES.values())
    # Remove duplicates
    all_tickers = list(set(all_tickers))

    with st.spinner('Fetching data...'):
        try:
            data = fetch_data(all_tickers, EARLIEST_DATE)
        except Exception as e:
            st.error(f"Error fetching data: {e}")
            return

    if data.empty:
        st.error("No data fetched. Please check the tickers or date range.")
        return

    # Calculate Portfolios
    dk_performance = calculate_portfolio_performance(data, PORTFOLIO_DK, START_DATE_DK)
    js_performance = calculate_portfolio_performance(data, PORTFOLIO_JS, START_DATE_JS)

    # Calculate Indices (Start from Earliest Date for comparison context, or align with JS?)
    # User asked to compare. Let's compute from Earliest Date (JS start)
    indices_performance = {}
    for name, ticker in INDICES.items():
        if ticker in data.columns:
            series = data[ticker].ffill().bfill()
            # Filter from Earliest Date
            series = series[series.index >= pd.Timestamp(EARLIEST_DATE)]
            if not series.empty:
                indices_performance[name] = series / series.iloc[0]

    # Combine all into one DataFrame for plotting (outer join to keep all dates)
    plot_data = pd.DataFrame({
        "DK Portfolio": dk_performance,
        "JS Portfolio": js_performance,
        **indices_performance
    })
    
    # Calculate percentage change (Growth - 1) * 100
    pct_change_data = (plot_data - 1) * 100

    # --- Custom CSS for Material Design ---
    st.markdown("""
        <style>
        .metric-card {
            background-color: #262730;
            border-radius: 12px;
            padding: 16px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
            text-align: center;
            margin-bottom: 16px;
            transition: transform 0.2s;
        }
        .metric-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 8px rgba(0, 0, 0, 0.4);
        }
        .metric-name {
            font-size: 1rem;
            color: #E0E0E0;
            margin-bottom: 8px;
            font-weight: 500;
        }
        .metric-value {
            font-size: 2rem;
            font-weight: 700;
            margin-bottom: 4px;
        }
        .metric-delta {
            font-size: 1rem;
            font-weight: 500;
        }
        </style>
    """, unsafe_allow_html=True)

    # --- Total Return Summary (Moved to Top) ---
    st.subheader("Total Return Summary")
    
    # Get latest available date
    latest_date = pct_change_data.index[-1]
    
    summary_data = []
    for name in pct_change_data.columns:
        # Handle NaN at the end (if different timezones/update times)
        # Get last valid index for this column
        valid_series = pct_change_data[name].dropna()
        if valid_series.empty:
            continue
            
        current_return = valid_series.iloc[-1]
        
        # For daily change, we need the last two valid points
        if len(valid_series) > 1:
            prev_return = valid_series.iloc[-2]
            
            # Reconstruct value series (base 100)
            current_val = 100 * (1 + current_return/100)
            prev_val = 100 * (1 + prev_return/100)
            daily_change_pct = ((current_val - prev_val) / prev_val) * 100
        else:
            daily_change_pct = 0.0

        # Fix 0% issue: if daily change is exactly 0, maybe look back one more day?
        if abs(daily_change_pct) < 0.0001 and len(valid_series) > 2:
             prev_return = valid_series.iloc[-2]
             prev_prev_return = valid_series.iloc[-3]
             
             val_prev = 100 * (1 + prev_return/100)
             val_prev_prev = 100 * (1 + prev_prev_return/100)
             daily_change_pct = ((val_prev - val_prev_prev) / val_prev_prev) * 100

        summary_data.append({
            "Name": name,
            "Daily Change (%)": daily_change_pct,
            "Total Return (%)": current_return
        })
    
    # Responsive Grid Layout
    # Streamlit columns don't wrap automatically on mobile, but we can use a container width trick or just rely on Streamlit's responsive behavior.
    # However, for "mobile optimization", stacking is better. Streamlit stacks columns on mobile by default.
    cols = st.columns(len(summary_data))
    for i, row in enumerate(summary_data):
        with cols[i]:
            total_return = row['Total Return (%)']
            daily_change = row['Daily Change (%)']
            
            # Korean Stock Colors: Red = Rise, Blue = Fall
            color = "#FF3B30" if total_return >= 0 else "#007AFF" 
            delta_color = "#FF3B30" if daily_change >= 0 else "#007AFF"
            delta_arrow = "▲" if daily_change >= 0 else "▼"
            
            st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-name">{row['Name']}</div>
                    <div class="metric-value" style="color: {color};">
                        {total_return:+.2f}%
                    </div>
                    <div class="metric-delta" style="color: {delta_color};">
                        {delta_arrow} {abs(daily_change):.2f}%
                    </div>
                </div>
            """, unsafe_allow_html=True)

    # --- Graph ---
    st.subheader("Performance Comparison (Cumulative Return %)")
    
    fig = go.Figure()
    for column in pct_change_data.columns:
        # Drop NaNs for plotting so lines don't drop to zero or break weirdly
        series = pct_change_data[column].dropna()
        
        # Line styling
        is_portfolio = "Portfolio" in column
        line_width = 4 if is_portfolio else 2
        line_dash = "solid" if is_portfolio else "dash"
        opacity = 1.0 if is_portfolio else 0.5
        
        # Specific colors for Portfolios (Distinct from Status Colors)
        # DK: Orange-Red, JS: Cyan-Blue to align roughly but distinguish from status
        line_color = None
        if column == "DK Portfolio":
            line_color = "#FF9500" # Orange
        elif column == "JS Portfolio":
            line_color = "#5856D6" # Purple/Indigo
            
        fig.add_trace(go.Scatter(
            x=series.index, 
            y=series, 
            mode='lines', 
            name=column,
            line=dict(width=line_width, color=line_color, dash=line_dash),
            opacity=opacity
        ))

        # Add annotations at intervals (e.g., Month End)
        # Resample to find points to annotate
        if not series.empty:
            # Get last day of each month in the series
            # We use 'ME' for month end. 
            # We only want to annotate if it's within the visible range (DK Start Date)
            # But we can just add them all, Plotly handles clipping usually, or we filter.
            
            # Filter series to start from DK Start Date for annotations to avoid clutter
            annot_series = series[series.index >= pd.Timestamp(START_DATE_DK)]
            
            # Resample to get monthly points. 
            # We want the value at the actual data point closest to month end.
            # Let's just pick every ~30 days or so to be simple and robust against missing dates
            # Or use the resampled index to find nearest date in actual index.
            
            # Simple approach: Iterate and pick first of month? Or last?
            # Let's use Month Ends.
            month_ends = annot_series.resample('ME').last()
            
            for date, value in month_ends.items():
                # Check if date is in original series (it might be shifted by resample)
                # resample('ME') gives the last calendar day, which might not be a trading day.
                # So we should find the nearest valid index.
                
                # Efficient way: asof
                try:
                    idx = annot_series.index.get_indexer([date], method='nearest')[0]
                    real_date = annot_series.index[idx]
                    real_value = annot_series.iloc[idx]
                    
                    # Only annotate if the date is reasonably close (e.g. within 5 days)
                    # Fix: Use timedelta for date arithmetic
                    date_diff = abs((real_date - date).total_seconds() / 86400)  # Convert to days
                    if date_diff < 5:
                         fig.add_annotation(
                            x=real_date,
                            y=real_value,
                            text=f"{real_value:+.1f}%",
                            showarrow=True,
                            arrowhead=0,
                            ax=0,
                            ay=-20 if real_value >= 0 else 20,
                            font=dict(size=10, color="white"),
                            bgcolor=line_color if line_color else "#555",
                            opacity=0.8
                        )
                except:
                    pass
    
    # Set X-axis range to start from DK Start Date
    fig.update_layout(
        xaxis=dict(
            title="Date",
            range=[START_DATE_DK, TODAY],
            # Responsive date formatting based on range
            tickformat="%Y-%m-%d",
            dtick="M1",  # Monthly ticks
            tickangle=-45
        ),
        yaxis_title="Return (%)",
        hovermode="x unified",
        template="plotly_dark",
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01
        ),
        margin=dict(l=0, r=0, t=30, b=0) # Optimize margins for mobile
    )
    
    # Add vertical line and annotation for current date
    # Get the latest date with data for each portfolio
    latest_dk = pct_change_data["DK Portfolio"].dropna().index[-1] if "DK Portfolio" in pct_change_data.columns else None
    latest_js = pct_change_data["JS Portfolio"].dropna().index[-1] if "JS Portfolio" in pct_change_data.columns else None
    
    # Use the most recent date
    current_date = max([d for d in [latest_dk, latest_js] if d is not None])
    
    # Add vertical line at current date
    fig.add_vline(
        x=current_date,
        line_dash="dot",
        line_color="gray",
        opacity=0.5,
        annotation_text=f"Today: {current_date.strftime('%Y-%m-%d')}",
        annotation_position="top",
        annotation_font_size=11,
        annotation_font_color="white"
    )
    
    st.plotly_chart(fig, use_container_width=True)

    # --- Monthly Change Table ---
    st.subheader("Monthly Change (%)")
    
    # Resample to month end and calculate percentage change
    # We need the raw values (normalized) to calculate % change correctly
    # plot_data contains values relative to 1.0 at start
    
    monthly_data = plot_data.resample('ME').last() # 'ME' is Month End in newer pandas, 'M' deprecated
    
    # Calculate month-over-month percentage change
    monthly_changes = monthly_data.pct_change() * 100
    
    # Format the index to be more readable (YYYY-MM)
    monthly_changes.index = monthly_changes.index.strftime('%Y-%m')
    
    # Sort index descending (newest first)
    monthly_changes = monthly_changes.sort_index(ascending=False)
    
    # Format numbers
    st.dataframe(monthly_changes.style.format("{:+.2f}%"))

if __name__ == "__main__":
    main()
