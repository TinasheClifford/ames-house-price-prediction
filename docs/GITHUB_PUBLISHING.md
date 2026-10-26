# Publish this project on GitHub

## Before uploading

Extract `ames_house_price_prediction_github_ready.zip`. Open the inner `ames-house-price-prediction` folder. Upload its contents so that `README.md` and `app.py` appear at the repository root. Do not upload the ZIP itself or drag the outer folder as an extra directory layer.

The clean package excludes Python environments, raw/processed transaction files, caches and credentials. Your previous working app can stay where it is; this is a separate publishing copy. Review README.md and run the app from this copy before publishing.

## Create the repository

Sign into https://github.com and create a repository called `ames-house-price-prediction` under your account. Suggested description:

> Historical Ames house-price estimation with Python, scikit-learn and Streamlit, including five explained notebooks and held-out evaluation.

Choose Public for a portfolio, or Private if you want to review it first. Do not generate a second README because this package provides one. Leave the licence unset until you decide what reuse rights to grant.

## Upload in the browser

Choose **Add file → Upload files** (or the upload link on an empty repository). Drag the extracted files and subfolders into the upload area, preserving their structure. Include the hidden `.gitignore` file; File Explorer may require “Hidden items” to be enabled. Browser uploads do not apply `.gitignore` filtering, so use this clean package rather than your working environment folder.

GitHub's browser limit is 25 MiB per file and 100 files per upload. The included model is below that per-file limit. If needed, upload notebooks, model and application in separate batches. Supply a descriptive commit message, review changes, and complete the displayed commit/proposal flow. If you propose a branch, merge its pull request to the default branch after review.

## Verify your portfolio page

- `README.md` displays on the main repository page.
- All five notebook links open, with saved tables and charts.
- `app.py`, `src/`, `models/` and `reports/` are present.
- The diagnostics image renders and model metrics match Notebook 5.
- No `.venv`, `house-env`, personal screenshots or unrelated files were added.
- Add repository topics: `python`, `machine-learning`, `regression`, `random-forest`, `streamlit`, `scikit-learn`, `data-science`.
- Pin the repository on your profile if desired.

This package has not yet been uploaded to your account. There is no live application URL to add yet.

## Add real app screenshots

Follow SCREENSHOTS.md. They are a useful final polish and can be added after your first upload. The README already includes an actual held-out diagnostic chart, not a simulated application screenshot.

## Public app deployment — next stage

Once the GitHub copy is verified, use Streamlit Community Cloud's “Create app” flow and select the repository, branch and `app.py`. Use the pinned requirements and a supported Python version matching the tested environment where available. Review build logs and verify a real prediction before adding the resulting URL to your repository's About website field and README.

No public deployment has been performed by preparing this package. The next guided step is creating your GitHub repository and checking the upload.

## Sources

- GitHub upload instructions and limits: https://docs.github.com/en/repositories/working-with-files/managing-files/adding-a-file-to-a-repository
- Streamlit deployment overview: https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app

A PowerPoint is optional after the repository and app are published. A useful six-slide structure is problem, data, preprocessing, model comparison, held-out results and demonstration. The README and notebooks are the primary project report.
