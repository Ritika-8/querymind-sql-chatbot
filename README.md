# QueryMind — LLM-Powered SQL Analytics Chatbot

Ask business questions in plain English. Get SQL, results, and insights instantly.

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.32-red)
![Gemini](https://img.shields.io/badge/Gemini-1.5_Flash-orange)
![SQLite](https://img.shields.io/badge/SQLite-3-green)

---

## Overview

Most business teams cannot write SQL. This application bridges that gap. You type a plain English question and the app:

1. Converts it to SQL using Google Gemini 1.5 Flash
2. Executes the query on a real e-commerce database
3. Visualizes the results automatically (bar, line, or pie charts)
4. Returns a concise business insight in plain English

---

## Dataset

Realistic Indian e-commerce database containing:
- 500 customers across 10 cities (Mumbai, Delhi, Bengaluru, Hyderabad, Chennai and more)
- 20 products across 6 categories (Electronics, Clothing, Kitchen, Footwear, Audio, Wearables)
- Approximately 2000 orders over the last 365 days
- Payment methods: UPI, Credit Card, Debit Card, Net Banking, Cash on Delivery

---

## Example Questions

| Question | What it does |
|----------|-------------|
| Which city has the highest revenue? | Aggregates total amount by city |
| Top 5 best-selling products this month | Joins orders, order items, and products |
| What percentage of orders were cancelled? | Calculates cancellation rate |
| Average order value by loyalty tier | Groups customers by tier |
| Revenue trend over the last 6 months | Time-series aggregation by month |

---

## Architecture

```
User Question (Natural Language)
        |
        v
Google Gemini 1.5 Flash
(Natural Language to SQL)
        |
        v
SQLite Database
(Query Execution)
        |
        v
Auto Visualization
(Plotly Charts)
        |
        v
Google Gemini 1.5 Flash
(Business Insight Generation)
        |
        v
Streamlit UI
```

---

## Getting Started

Prerequisites:
- Python 3.10 or higher
- A free Google Gemini API key from https://aistudio.google.com/app/apikey

Installation:

```bash
# Clone the repository
git clone https://github.com/Ritika-8/querymind-sql-chatbot
cd querymind-sql-chatbot

# Install dependencies
pip install -r requirements.txt

# Run the application
streamlit run app.py
```

The app will open automatically at http://localhost:8501.
Enter your Gemini API key in the sidebar to begin.

---

## Deployment on Streamlit Cloud

1. Fork this repository to your GitHub account
2. Go to https://share.streamlit.io
3. Connect your GitHub account and select this repository
4. Set the main file path as app.py
5. Click Deploy and enter your API key in the sidebar once live

---

## Tech Stack

| Component            | Technology              |
|----------------------|-------------------------|
| Large Language Model | Google Gemini 1.5 Flash |
| Database             | SQLite                  |
| Frontend             | Streamlit               |
| Visualization        | Plotly                  |
| Data Processing      | Pandas, NumPy           |

---

## Project Structure

```
querymind-sql-chatbot/
|
|-- app.py              # Main Streamlit application
|-- database.py         # Database creation, schema, and query execution
|-- requirements.txt    # Python dependencies
|-- README.md           # Project documentation
```

---

## Planned Improvements

- Support for uploading custom CSV or Excel files
- Multi-turn conversation memory
- Export query results to Excel
- Support for PostgreSQL and MySQL connections
- Query history and saved queries panel

---

## Author

Ritika Bajaj — MSc Data Science, King's College London

LinkedIn: https://www.linkedin.com/in/ritika-bajaj-b0929821b/
GitHub: https://github.com/Ritika-8
