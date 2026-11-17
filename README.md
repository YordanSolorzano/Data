# Customer churn risk dashboard

A dashboard that shows which customers of a fashion retail chain are likely to stop buying,
so the business can target them with retention campaigns.

All names are anonymized: stores appear as `TIENDA NORTE`, brands as `MARCA A`, and customer
IDs are masked.

## What it shows

| Item | Value |
| --- | --- |
| Transactions analyzed | 183,861 (Nov 2022 – Aug 2025) |
| Stores | 7 |
| Customers scored | 48,075 |
| Prediction target | No purchase in the next 180 days |
| Best model | Gradient Boosting, AUC 0.725 |
| Models compared | Logistic regression (0.715), Random Forest (0.721), Gradient Boosting (0.725) |
| Train / test customers | 29,508 / 9,837 |

The model uses recency, frequency, monetary value and behavior features. It was evaluated with
a time-based split per store, so no information from the future leaks into training.

The page also includes monthly sales per store, top brands and product lines, a customer
segmentation by risk and value, and an actionable list of high-value customers at risk.

## Repository layout

```
site/index.html         The published dashboard (HTML + Chart.js, data embedded as JSON)
src/churn_dashboard/    Python package that reads and validates the dashboard data
tests/                  Unit tests and checks on the published page
.github/workflows/      CI: tests on every push, and deployment to GitHub Pages
```

## Checks that run on every push

The dashboard is a static page, so a wrong or sensitive number could be published without
anyone noticing. The `churn_dashboard` package guards against that:

- **Consistency:** segments and the risk histogram add up to the total number of customers;
  store revenue and transactions add up to the headline KPIs; every store has one value per month.
- **Model sanity:** AUC values are in a valid range, the reported best model has the highest
  AUC, and the ROC curve never decreases.
- **Privacy:** customer IDs are masked, and store and brand names follow the anonymous pattern.
  A page with real names fails the build.

## Run it locally

```bash
pip install -e ".[dev]"
pytest                                      # run the tests
ruff check . && ruff format --check .       # lint and format
python -m churn_dashboard site/index.html   # validate the dashboard
```

## Known limitations

- The model training code is not in this repository yet; the page holds only its results.
- Some brands and product lines are not normalized in the source data (for example `ZAPATO`
  and `ZAPATOS` appear as separate lines), so their totals are split.
- Churn is very common in this dataset (about 92% of training customers), which limits how
  much the model can separate customers.
