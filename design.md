# FormoCast: Architectural Design Document

## 1. Design Philosophy
FormoCast is built on the principle of **"Intentional Minimalism"**. Every architectural choice is calculated to maximize reliability while minimizing the code surface area. We reject complex ML models where geometric logic provides clearer interpretability.

## 2. System Architecture (High-Level)

### 2.1 Decoupled Service Layers
To ensure scalability, the system is divided into four distinct layers:

1.  **Data Layer:** `services/data_fetcher.py` - Abstracts the complexities of the yfinance API. Implements caching and rate-limiting safeguards.
2.  **Intelligence Layer:** `core/detector.py` & `core/predictor.py` - Pure Python logic for pattern recognition. Zero external dependencies beyond `numpy` and `scipy`.
3.  **Visual & Communication Layer:** `services/visualizer.py` & `services/notifier.py` - Responsible for the "Premium" user experience. Handles chart rendering and SMTP dispatch.
4.  **Persistence Layer:** `db/models.py` - Managed SQLite instance tracking the lifecycle of a "Prediction".

## 3. Deep-Dive: Pattern Detection Algorithm
We avoid "black box" detection. Our algorithm follows a deterministic geometric approach:

### 3.1 Peak/Trough Synchronization
Using `argrelextrema`, we generate a sparse representation of the price series. 
- **Variable Windowing:** The `window` parameter is dynamically adjusted based on the asset's volatility to prevent noise-based detections.

### 3.2 Pattern Logic: The Double Top Case
```python
# Pseudo-logic
def detect_double_top():
    1. Identify last two peaks (P1, P2).
    2. Ensure abs(P1.price - P2.price) / P1.price < 0.02.
    3. Verify current_price is below the "Neckline" (Trough between P1, P2).
    4. Confirm prediction: "Down".
```

## 4. Visual Identity (Ultrathink Protocol)
- **Palette:** 
    - Background: `#1a1a1a` (Deep Space Gray)
    - Primary Action: `#00d1b2` (Electric Turquoise)
    - Alert/Danger: `#ff3860` (Vivid Crimson)
- **Typography:** Reports use sans-serif fonts (Inter/Roboto) for maximum legibility in email clients.

## 5. Security & Persistence Strategy
- **Docker Isolation:** The application runs in a rootless container.
- **Volume Strategy:** The SQLite database is mounted to a persistent host volume to prevent data loss during container rebuilds.
- **Environment Management:** Sensitive keys are handled via `python-dotenv`, never committed to Git.

## 6. Edge Case Analysis
| Edge Case | Prevention Strategy |
| :--- | :--- |
| **Market Gaps** | Use `yfinance` auto-adjustment for splits and dividends. |
| **Email Blockage** | Implement exponential backoff in SMTP delivery. |
| **No Patterns Found** | Logging system records "Quiet Scans" to verify the service is still alive. |
| **Duplicate Alerts** | DB check prevents sending alerts for the same pattern/ticker pair within 24h. |
