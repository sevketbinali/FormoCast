from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from db.models import Database
from core.analyzer import AccuracyAnalyzer
import uvicorn

app = FastAPI(title="FormoCast Executive Dashboard")
db = Database()
analyzer = AccuracyAnalyzer()

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.get("/", response_class=HTMLResponse)
async def dashboard():
    stats = analyzer.get_weekly_stats()
    
    # HTML template with premium "Dark Mode" aesthetic
    html_content = f"""
    <html>
        <head>
            <title>FormoCast | Executive Dashboard</title>
            <style>
                body {{
                    background-color: #1a1a1a;
                    color: #ffffff;
                    font-family: 'Inter', sans-serif;
                    margin: 0;
                    padding: 40px;
                }}
                .container {{
                    max-width: 1000px;
                    margin: auto;
                }}
                .header {{
                    text-align: center;
                    margin-bottom: 50px;
                }}
                h1 {{ color: #00d1b2; font-size: 3rem; }}
                .stats-grid {{
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                    gap: 20px;
                    margin-bottom: 40px;
                }}
                .card {{
                    background-color: #2d2d2d;
                    padding: 20px;
                    border-radius: 12px;
                    border: 1px solid #4a4a4a;
                    text-align: center;
                }}
                .card h3 {{ color: #b5b5b5; margin: 0; font-size: 0.9rem; }}
                .card p {{ font-size: 2rem; font-weight: bold; margin: 10px 0; }}
                .accuracy {{ color: #00d1b2; }}
                .footer {{ text-align: center; color: #4a4a4a; margin-top: 50px; font-size: 0.8rem; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>FormoCast</h1>
                    <p>Finansal Zeka ve Otonom Analiz Platformu</p>
                </div>
                
                <div class="stats-grid">
                    <div class="card">
                        <h3>Toplam Tespit</h3>
                        <p>{stats['total_detections']}</p>
                    </div>
                    <div class="card">
                        <h3>Doğruluk Oranı</h3>
                        <p class="accuracy">%{stats['accuracy_rate']:.1f}</p>
                    </div>
                    <div class="card">
                        <h3>Başarılı / Başarısız</h3>
                        <p>{stats['correct']} / {stats['incorrect']}</p>
                    </div>
                </div>

                <div class="card" style="text-align: left;">
                    <h3 style="margin-bottom: 15px;">En Sık Görülen Formasyonlar</h3>
                    <ul>
                        {''.join([f"<li>{p[0]}: {p[1]}</li>" for p in stats['top_patterns']])}
                    </ul>
                </div>

                <div class="footer">
                    &copy; 2026 FormoCast Intelligence. All rights reserved.
                </div>
            </div>
        </body>
    </html>
    """
    return HTMLResponse(content=html_content)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
