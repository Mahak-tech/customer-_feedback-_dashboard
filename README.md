# 📊 Customer Feedback Dashboard

A Streamlit dashboard that analyzes customer feedback sentiment using **TextBlob**
and visualizes results with interactive **Plotly** charts.

## Features
- Upload your own CSV or use built-in sample data
- Automatic sentiment analysis (Positive / Neutral / Negative) with polarity & subjectivity scores
- KPI metric cards
- Sentiment distribution pie chart
- Polarity score histogram
- Sentiment breakdown by product/category (auto-detected)
- Polarity vs Subjectivity scatter plot
- Sentiment trend over time (auto-detected date column)
- Filterable, sortable data table
- Download processed results as CSV

## Project Structure
```
customer_feedback_dashboard/
├── app.py                     # Main Streamlit application
├── requirements.txt           # Python dependencies
├── data/
│   └── sample_feedback.csv    # Sample dataset (20 rows)
└── README.md                  # This file
```

## Prerequisites
- Python 3.9 or higher installed
- VS Code with the Python extension installed

## Step-by-Step Setup (VS Code)

### 1. Unzip and open the project
Unzip the downloaded folder, then in VS Code:
`File > Open Folder...` → select `customer_feedback_dashboard`

### 2. Open a terminal in VS Code
`Terminal > New Terminal` (or `` Ctrl+` ``)

### 3. Create a virtual environment (recommended)
```bash
python -m venv venv
```

Activate it:
- **Windows:** `venv\Scripts\activate`
- **macOS/Linux:** `source venv/bin/activate`

### 4. Install dependencies
```bash
pip install -r requirements.txt
```

### 5. Download TextBlob's language corpora (one-time setup)
```bash
python -m textblob.download_corpora
```

### 6. Run the app
```bash
streamlit run app.py
```

### 7. View in browser
Streamlit will automatically open your default browser. If not, go to:
```
http://localhost:8501
```

## Using Your Own Data
1. In the sidebar, select **"Upload CSV"**
2. Upload any CSV file that has at least one text column (e.g., `feedback`, `review`, `comment`)
3. Select the correct text column from the dropdown
4. Optional: include a `product`/`category` column for grouped charts, and a `date` column for trend charts

## Troubleshooting
- **`ModuleNotFoundError`**: Ensure your virtual environment is activated and run `pip install -r requirements.txt` again
- **TextBlob corpora error**: Re-run `python -m textblob.download_corpora`
- **Port already in use**: Run `streamlit run app.py --server.port 8502` to use a different port
- **Blank charts**: Make sure your filtered sentiment selection (sidebar) isn't empty

## Stopping the App
Press `Ctrl+C` in the VS Code terminal.
