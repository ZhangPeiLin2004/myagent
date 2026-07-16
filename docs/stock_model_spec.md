


# A-share Next Day >1.5% Prediction Model Spec
## Data Range
2020-01-01 ~ 2026-07-03 A-share daily kline

## Input Window
t-2, t-1, t three consecutive daily k-lines, total 36 features.

## Label Definition
y=1: t+1 close gain > 1.5%
y=0: other cases

## Model
LightGBM binary classification
Threshold: 0.62

## Evaluation Metrics
Precision (core trading metric), Recall, Signal hit count, backtest return curve.

## Workflow
1. Query 3-day kline via DataQueryTool
2. Feature engineering
3. Standardization
4. Model predict probability
5. Compare threshold to output signal
