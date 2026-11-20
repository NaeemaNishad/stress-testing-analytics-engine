# Integrated ApexPlanet Portfolio + Research Extension

## Files
- `index.html`: original ApexPlanet internship portfolio, preserved and extended with a Research Extension section.
- `dashboard.html`: original ApexPlanet sales dashboard, preserved with cross-navigation to the portfolio.
- `research.html`: research overview and methodology page.
- `dashboard/app.py`: interactive Streamlit dashboard for the stress-testing experiments.

## Important
Keep your existing `src/`, `data/`, `results/`, and `reports/` folders. Copy these files into the root of that existing project; merge the `dashboard/app.py` file into your existing `dashboard/` folder. Do not delete your original data or experiment scripts.

The links to `http://localhost:8501` are for local development only. After deploying Streamlit, replace those links with the public Streamlit URL. Update the GitHub repository URL in the portfolio section if your repository name differs.

## Run locally
From the project root, install dependencies from your `requirements.txt`, run the experiment scripts to generate `results/stress_test_results.csv` and `results/stress_test_summary.csv`, then:

```powershell
python -m streamlit run dashboard/app.py
```

Open `index.html` with VS Code Live Server. From the portfolio, open the original ApexPlanet dashboard or the research overview. The research overview links to the Streamlit app.

## Note
The original ApexPlanet dashboard contains its own embedded sales data and remains a standalone HTML dashboard. It is intentionally preserved rather than replaced by the new Streamlit research dashboard.
