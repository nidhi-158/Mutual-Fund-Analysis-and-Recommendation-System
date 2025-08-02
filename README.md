# 📈 Mutual Fund Recommendation System (Historical + Live NAV)
---

## 🏦 Problem Statement
Develop a mutual fund recommendation system that:

- **Existing Investors:**
  - Analyze their portfolio and suggest:
    - **Hold** if their current fund is performing well.
    - **Switch** to a better-performing fund if one exists.
  - If no better fund exists, hold the current fund.

- **New Investors:**
  - Suggest mutual funds based on risk profile, budget, and investment type (Asset Class & Market Cap preference).
  - Provide NAV values and rankings.

---

## 📌 Dataset
- **Source:** [AMFI India](https://www.amfiindia.com/)
- **Duration:** Jan 2023 – Dec 2024 (historical) + real-time NAV fetching.
- **Rows:** 3,770,134  

| Column       | Type     | Description              |
|--------------|----------|--------------------------|
| Date         | Date     | NAV date                |
| Fund House   | Object   | Mutual fund house name  |
| Fund HouseID | Int      | Fund house ID          |
| Scheme       | Object   | Scheme name            |
| SchemeID     | Int      | Unique scheme identifier|
| NAV          | Float    | Net Asset Value        |

---

## 🏗 Workflow
1. **Data Scraping**
   - Scrape 2 years of historical NAV data.
   - Fetch live NAV data from AMFI.
2. **Data Preprocessing)**
   - Handle null values.
   - Convert Date & NAV types.
   - Remove duplicates.
3. **Feature Engineering**
   - Calculate returns and risk metrics (Std Dev, Sharpe, Sortino).
   - Asset class & market cap classification.
   - Balanced distribution.
4. **Scaling & Encoding**
   - Label Encoding for categorical features.
   - StandardScaler for numerical features.
5. **Outlier Detection**
   - Z-score-based outlier flagging.
6. **Model Development**
   - Clustering and recommendation logic.
7. **Deployment**
   - Phase 1: Streamlit app (Int project).
   - Phase 2: FastAPI backend + React frontend (mf_website).

---

## 🛠 Tech Stack
- **Language:** Python 3.10+
- **Backend:** FastAPI
- **Frontend:** React.js
- **Deployment:** Streamlit (Phase 1), FastAPI + React (Phase 2)
- **Database:** SQLite
- **Libraries:** Pandas, NumPy, Scikit-learn, SQLAlchemy, Passlib, Requests, BeautifulSoup
- **Data Source:** AMFI India

---

## 🖥 Installation
### Phase 1: Historical System (Streamlit)
---
### Phase 2: Live NAV System (FastAPI + React)
---
