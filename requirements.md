# FormoCast: Professional Requirements Specification

## 1. Executive Summary
FormoCast is an advanced financial surveillance system designed to autonomously monitor market data, identify high-probability technical patterns, and deliver visual intelligence to the user. The system prioritizes aesthetic excellence, architectural simplicity, and data-driven accuracy analysis.

## 2. Functional Requirements (FR)

### 2.1 Surveillance & Data Acquisition
- **FR-1.1: Multi-Asset Monitoring:** System must support Tickers for Stocks, Crypto, and Forex via `yfinance`.
- **FR-1.2: Dynamic Timeframes:** Ability to analyze Daily, Weekly, and 4-hour intervals (configurable).
- **FR-1.3: Data Integrity:** Implement robust error handling for API rate limits and missing data points (NaN handling).

### 2.2 Pattern Intelligence
- **FR-2.1: Geometric Pattern Detection:** Implementation of high-fidelity detection algorithms for:
    - **Double Top/Bottom:** 2-peak/trough level parity within a 2% variance threshold.
    - **Head and Shoulders:** Recognition of shoulder-head-shoulder symmetry.
    - **Triangles/Wedges:** Identification of converging trendlines using linear regression on extrema.
- **FR-2.2: Signal Generation:** Each detected pattern must generate a "Confidence Score" and a "Predicted Direction" (Bullish/Bearish).

### 2.3 Visual Intelligence & Reporting
- **FR-3.1: Premium Charting:** Generation of Dark-Mode, publication-ready charts highlighting pattern extrema and target zones.
- **FR-3.2: Automated Notifier:** Real-time email delivery with embedded visuals and executive summaries.
- **FR-3.3: Weekly Performance Audit:** Automated generation of a "Success/Fail" report based on historical prediction outcomes.

## 3. Non-Functional Requirements (NFR)

### 3.1 Design Aesthetics (ULTRATHINK Mode)
- **NFR-3.1.1: Intentional Minimalism:** The UI/Reports must avoid "bootstrapped" generic looks. Custom hex-coded palettes (#00d1b2, #2d2d2d) must be used.
- **NFR-3.1.2: Visual Hierarchy:** Email reports must prioritize the most critical information (Ticker + Direction) through typography and whitespace.

### 3.2 Engineering Standards (Karpathy Guidelines)
- **NFR-3.2.1: Surgical Implementation:** No speculative abstractions. Every module must serve a direct functional requirement.
- **NFR-3.2.2: Environment Parity:** Full Dockerization to ensure "it works on my machine" consistency.
- **NFR-3.2.3: Database Performance:** SQLite with indexed lookups on `ticker` and `target_date`.

## 4. Constraint Analysis & Assumptions
- **API Limits:** We assume the user is using the free tier of `yfinance`. We implement jitter and delay to avoid IP blocks.
- **Prediction Horizon:** Predictions are currently fixed to a 7-day look-forward period.
- **Security:** SMTP credentials must never be hardcoded and should be injected via `.env`.

## 5. Success Criteria
- **Detection Reliability:** Zero false positives in "perfect" historical pattern samples.
- **Visual Impact:** Reports must meet "Senior Architect" visual standards (clean, informative, aesthetic).
- **Operational Autonomy:** The system must run for 7 days without manual restart or memory leakage.
