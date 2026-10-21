# FashionHub AI — Professional Streamlit Dashboard

A polished Streamlit prototype inspired by the FashionHub AI presentation.

## Features
- Executive overview with KPI cards and interactive Plotly charts
- Revenue trend, category mix, marketing channel comparison, discount/sales scatter
- Sales Forecast Lab with scenario comparison and CSV export
- Marketing Intelligence with campaign scenario, sensitivity chart, and channel scorecard
- Product Insights for category ranking, price distribution, and seasonal demand
- Data Explorer with data-quality profile, correlation heatmap, and CSV export
- Sidebar CSV upload and filters for category and date when matching columns exist

## Run locally
```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

## Deploy on Streamlit Community Cloud
1. Create a GitHub repository and upload `app.py`, `requirements.txt`, and `README.md`.
2. Open https://share.streamlit.io/ and sign in with GitHub.
3. Choose **Create app**, select the repository and branch, and set the main file path to `app.py`.
4. Click **Deploy**.

## Data and model note
Without a supplied real dataset or trained model, the app uses synthetic demonstration data and transparent heuristic scenario calculations. These are not validated production forecasts. For real business use, map your CSV columns to the expected names and train/evaluate models on historical data.
