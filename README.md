
# Stress-Testing & Noise-Injection Analytics Engine

## Overview

The Stress-Testing & Noise-Injection Analytics Engine is a Python-based
framework designed to evaluate the reliability of business analytics
under controlled data corruption.

The project uses a sales dataset to investigate how different types
and levels of data quality issues affect business KPIs, customer
segmentation, and statistical analysis.

## Objectives

- Simulate controlled data quality issues.
- Evaluate the impact of missing values.
- Measure the effect of numerical outliers.
- Study categorical label errors.
- Compare individual and combined corruption scenarios.
- Evaluate the stability of business analytics.

## Technologies

- Python
- Pandas
- NumPy
- SciPy
- Matplotlib
- Plotly
- Streamlit

## Experimental Design

Noise types:
1. Missing values
2. Numerical outliers
3. Categorical label errors
4. Combined noise

Noise levels:
- 5%
- 15%
- 30%

Each scenario is repeated using 10 random seeds.

This produces 120 experimental runs, in addition to the clean baseline.

## Evaluation Metrics

- Total revenue
- Total units sold
- Average order value
- Revenue per customer
- Top product category
- Customer segmentation stability
- ANOVA statistics
- Missing-value percentage

## Project Structure

- data/: Input and generated datasets
- src/: Noise injection and evaluation modules
- dashboard/: Streamlit dashboard
- results/: Experimental outputs and visualizations
- reports/: Research documentation

## How to Run

Install dependencies:

    python -m pip install -r requirements.txt

Generate corrupted datasets:

    python src/noise_injector.py

Run experiments:

    python src/experiment_runner.py

Generate plots:

    python src/plot_degradation.py

Launch dashboard:

    python -m streamlit run dashboard/app.py

## Research Focus

The project investigates how data quality degradation can influence
the accuracy, stability, and reliability of data-driven business
decisions.
