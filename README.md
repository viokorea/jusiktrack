# 📈 Stock Portfolio Competition

A real-time stock portfolio performance tracker comparing DK and JS portfolios against major market indices.

## Version

**Current Version**: v1.0.0

## Features

- **Real-time Performance Tracking**: Track portfolio performance from different start dates
- **Material Design UI**: Modern, responsive interface with Korean stock market color scheme (Red=Rise, Blue=Fall)
- **Interactive Charts**: Plotly-powered charts with monthly annotations and current date marker
- **Mobile Optimized**: Responsive design that works on all devices

## Portfolios

### DK Portfolio (Start: Oct 7, 2025)
- QQQM: 45%
- SMH: 15%
- SPYM: 10%
- JEPQ: 10%
- IAU: 10%
- DBMF: 10%

### JS Portfolio (Start: Mar 1, 2025)
- SCHD: 33%
- SPYM: 67%

## Installation

1. Clone the repository:
```bash
git clone <your-repo-url>
cd jusikzothem
```

2. Create virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

Run the Streamlit app:
```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

## Deployment

See [DEPLOYMENT.md](DEPLOYMENT.md) for deployment options and instructions.

## Tech Stack

- **Frontend**: Streamlit
- **Data**: yfinance
- **Visualization**: Plotly
- **Data Processing**: Pandas

## Changelog

### v1.0.0 (2025-11-19)

**Initial Release**

#### Features
- ✅ Real-time portfolio tracking with different start dates
  - DK Portfolio: Oct 7, 2025
  - JS Portfolio: Mar 1, 2025
- ✅ Material Design UI with card-based layout
- ✅ Korean stock market color scheme (Red=Rise, Blue=Fall)
- ✅ Interactive Plotly charts with:
  - Monthly return annotations
  - Current date marker
  - Dashed/transparent index lines for better portfolio visibility
  - Responsive date labels
- ✅ Total Return Summary cards with hover effects
- ✅ Monthly change table
- ✅ Mobile-responsive design
- ✅ Comparison against major indices (KOSPI, NASDAQ, S&P 500)

#### Technical
- Streamlit-based web application
- yfinance for real-time market data
- Pandas for data processing
- Plotly for interactive visualizations
- Custom CSS for Material Design styling

## License

MIT
