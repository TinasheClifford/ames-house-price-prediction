# Capture your application screenshots

Run the application and open its browser tab. Use Windows + Shift + S to capture only the application content. Avoid personal folders, browser accounts and unrelated tabs. Save genuine captures in a new `screenshots/` folder at the repository root:

1. `app_inputs.png`: the property-entry form.
2. `app_prediction.png`: one completed estimate with its submitted details and historical scope visible.
3. `app_performance.png`: the performance tab with held-out metrics.

After adding these files, add the following to README.md:

```markdown
## Application preview

![Property entry form](screenshots/app_inputs.png)
![Historical prediction example](screenshots/app_prediction.png)
![Model performance](screenshots/app_performance.png)
```

The ZIP does not contain application screenshots. The diagnostic figures already in the README are genuine outputs from model evaluation. Keep screenshots readable and do not change the historical-price wording.
