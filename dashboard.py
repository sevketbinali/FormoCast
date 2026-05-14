from fastapi import FastAPI, BackgroundTasks
from fastapi.responses import HTMLResponse, JSONResponse
from db.models import Database
from core.analyzer import AccuracyAnalyzer
from services.bist_scanner import BistScanner
import plotly.graph_objects as go
import plotly.io as pio
import uvicorn
import pandas as pd
from datetime import datetime

app = FastAPI(title="FormoCast Executive Dashboard")
db = Database()
analyzer = AccuracyAnalyzer()

# Shared scanner instance for manual triggers
manual_scanner = BistScanner()

# Plotly default template
pio.templates.default = "plotly_dark"

def create_pnl_chart(pnl_history):
    if not pnl_history:
        return "<div style='text-align:center; padding:50px; color:#666;'>Kümülatif PnL verisi henüz oluşmadı.</div>"
    
    df = pd.DataFrame(pnl_history)
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df['prediction_date'], 
        y=df['cumulative_pnl'],
        mode='lines+markers',
        name='Kümülatif Getiri (%)',
        line=dict(color='#00d1b2', width=3),
        fill='tozeroy',
        fillcolor='rgba(0, 209, 178, 0.1)'
    ))
    fig.update_layout(
        title=dict(text="Kümülatif Getiri Performansı (%)", font=dict(size=16)),
        xaxis_title="Tarih",
        yaxis_title="Getiri (%)",
        margin=dict(l=20, r=20, t=50, b=20),
        height=350,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    return pio.to_html(fig, full_html=False, include_plotlyjs=False)

def create_pattern_chart(pattern_perf):
    if not pattern_perf:
        return "<div style='text-align:center; padding:50px; color:#666;'>Formasyon bazlı veri henüz oluşmadı.</div>"
    
    patterns = list(pattern_perf.keys())
    rates = [v['success_rate'] for v in pattern_perf.values()]
    
    fig = go.Figure(go.Bar(
        x=patterns,
        y=rates,
        marker=dict(color='#48c774', line=dict(color='#333', width=1)),
        opacity=0.8
    ))
    fig.update_layout(
        title=dict(text="Formasyon Bazlı Başarı Oranı (%)", font=dict(size=16)),
        yaxis=dict(range=[0, 100]),
        margin=dict(l=20, r=20, t=50, b=20),
        height=350,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    return pio.to_html(fig, full_html=False, include_plotlyjs=False)

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.post("/api/scan")
async def trigger_manual_scan(background_tasks: BackgroundTasks):
    """
    Triggers a manual BIST scan in the background.
    """
    try:
        # Clear cache for manual testing to ensure emails are sent
        manual_scanner.processed_signals.clear()
        background_tasks.add_task(manual_scanner.scan)
        return {"status": "success", "message": "BIST 100 taraması arka planda başlatıldı."}
    except Exception as e:
        return JSONResponse(status_code=500, content={"status": "error", "message": str(e)})

@app.get("/", response_class=HTMLResponse)
async def dashboard():
    stats = analyzer.get_weekly_stats()
    latest_preds = db.get_latest_predictions(10)
    
    pnl_chart_html = create_pnl_chart(stats['pnl_history'])
    pattern_chart_html = create_pattern_chart(stats['pattern_performance'])
    
    rows_html = ""
    for p in latest_preds:
        ticker, pattern, direction, price, date, outcome = p
        outcome_color = "#48c774" if outcome == "Correct" else "#ff3860" if outcome == "Incorrect" else "#b5b5b5"
        direction_color = "#48c774" if direction == "Up" else "#ff3860"
        
        rows_html += f"""
        <tr>
            <td>{date}</td>
            <td><strong>{ticker}</strong></td>
            <td>{pattern}</td>
            <td style="color: {direction_color}; font-weight: bold;">{direction}</td>
            <td>{price:.2f}</td>
            <td style="color: {outcome_color}; font-weight: bold;">{outcome or 'Analiz Bekliyor'}</td>
        </tr>
        """

    html_content = f"""
    <html>
        <head>
            <title>FormoCast | Executive Dashboard</title>
            <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
            <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap" rel="stylesheet">
            <style>
                :root {{ --primary: #00d1b2; --bg: #0f0f0f; --card: #1e1e1e; --border: #333; }}
                body {{
                    background-color: var(--bg);
                    color: #ffffff;
                    font-family: 'Inter', sans-serif;
                    margin: 0;
                    padding: 30px;
                }}
                .container {{ max-width: 1300px; margin: auto; }}
                .header-flex {{ 
                    display: flex; 
                    justify-content: space-between; 
                    align-items: center;
                    margin-bottom: 40px;
                    padding-bottom: 20px;
                    border-bottom: 1px solid var(--border);
                }}
                h1 {{ color: var(--primary); font-size: 2.2rem; margin: 0; font-weight: 800; }}
                
                .btn-scan {{
                    background-color: var(--primary);
                    color: #000;
                    border: none;
                    padding: 12px 24px;
                    border-radius: 8px;
                    font-weight: 600;
                    cursor: pointer;
                    display: flex;
                    align-items: center;
                    gap: 10px;
                    transition: all 0.3s ease;
                }}
                .btn-scan:hover {{ transform: scale(1.05); filter: brightness(1.1); }}
                .btn-scan:disabled {{ background-color: #444; color: #888; cursor: not_allowed; }}

                .stats-grid {{
                    display: grid;
                    grid-template-columns: repeat(4, 1fr);
                    gap: 20px;
                    margin-bottom: 30px;
                }}
                .card {{
                    background-color: var(--card);
                    padding: 25px;
                    border-radius: 16px;
                    border: 1px solid var(--border);
                }}
                .card h3 {{ color: #888; font-size: 0.75rem; margin: 0; text-transform: uppercase; letter-spacing: 1px; }}
                .card p {{ font-size: 2.2rem; font-weight: 800; margin: 10px 0 0 0; }}
                
                .charts-grid {{
                    display: grid;
                    grid-template-columns: 1.5fr 1fr;
                    gap: 20px;
                    margin-bottom: 30px;
                }}
                .chart-card {{
                    background-color: var(--card);
                    border-radius: 16px;
                    padding: 20px;
                    border: 1px solid var(--border);
                }}
                .table-card {{
                    background-color: var(--card);
                    border-radius: 16px;
                    padding: 30px;
                    border: 1px solid var(--border);
                }}
                table {{ width: 100%; border-collapse: collapse; margin-top: 25px; }}
                th {{ text-align: left; color: #888; font-size: 0.75rem; text-transform: uppercase; padding-bottom: 15px; border-bottom: 1px solid var(--border); }}
                td {{ padding: 15px 0; border-bottom: 1px solid #2d2d2d; font-size: 0.95rem; }}
                
                .live-status {{ color: var(--primary); font-weight: 600; font-size: 0.85rem; display: flex; align-items: center; gap: 8px; }}
                .dot {{ height: 8px; width: 8px; background-color: var(--primary); border-radius: 50%; box-shadow: 0 0 8px var(--primary); animation: pulse 2s infinite; }}
                @keyframes pulse {{ 0% {{ opacity: 1; }} 50% {{ opacity: 0.4; }} 100% {{ opacity: 1; }} }}

                #toast {{
                    visibility: hidden;
                    min-width: 250px;
                    background-color: var(--primary);
                    color: #000;
                    text-align: center;
                    border-radius: 8px;
                    padding: 16px;
                    position: fixed;
                    z-index: 1;
                    right: 30px;
                    bottom: 30px;
                    font-weight: 600;
                }}
                #toast.show {{ visibility: visible; animation: fadein 0.5s, fadeout 0.5s 2.5s; }}
                @keyframes fadein {{ from {{ bottom: 0; opacity: 0; }} to {{ bottom: 30px; opacity: 1; }} }}
                @keyframes fadeout {{ from {{ bottom: 30px; opacity: 1; }} to {{ bottom: 0; opacity: 0; }} }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header-flex">
                    <div>
                        <h1>FormoCast Executive</h1>
                        <div class="live-status"><span class="dot"></span> BIST 100 CANLI TAKİP SİSTEMİ AKTİF</div>
                    </div>
                    <button class="btn-scan" id="scanBtn" onclick="triggerScan()">
                        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line></svg>
                        MANUEL TARAMAYI BAŞLAT
                    </button>
                </div>

                <div class="stats-grid">
                    <div class="card">
                        <h3>Toplam Sinyal</h3>
                        <p>{stats['total_detections']}</p>
                    </div>
                    <div class="card">
                        <h3>Başarı Oranı</h3>
                        <p style="color: var(--primary);">%{stats['accuracy_rate']:.1f}</p>
                    </div>
                    <div class="card">
                        <h3>Ortalama PnL</h3>
                        <p style="color: {'#48c774' if stats['avg_pnl'] >= 0 else '#ff3860'};">{stats['avg_pnl']:.2f}%</p>
                    </div>
                    <div class="card">
                        <h3>Net Performans</h3>
                        <p>{stats['correct']}G / {stats['incorrect']}M</p>
                    </div>
                </div>

                <div class="charts-grid">
                    <div class="chart-card">{pnl_chart_html}</div>
                    <div class="chart-card">{pattern_chart_html}</div>
                </div>

                <div class="table-card">
                    <h3 style="margin: 0; font-size: 1.1rem;">Son Formasyon Sinyalleri</h3>
                    <table>
                        <thead>
                            <tr>
                                <th>Tespit Tarihi</th>
                                <th>Sembol</th>
                                <th>Formasyon</th>
                                <th>Yön</th>
                                <th>Giriş Fiyatı</th>
                                <th>Durum</th>
                            </tr>
                        </thead>
                        <tbody>
                            {rows_html or '<tr><td colspan="6" style="text-align:center; padding:50px; color:#666;">Veritabanında henüz sinyal bulunamadı.</td></tr>'}
                        </tbody>
                    </table>
                </div>
            </div>

            <div id="toast">Taram Başlatıldı...</div>

            <script>
                async function triggerScan() {{
                    const btn = document.getElementById('scanBtn');
                    const toast = document.getElementById('toast');
                    
                    btn.disabled = true;
                    btn.innerHTML = 'TARANIYOR...';
                    
                    try {{
                        const response = await fetch('/api/scan', {{ method: 'POST' }});
                        const data = await response.json();
                        
                        toast.innerHTML = data.message;
                        toast.className = "show";
                        setTimeout(() => {{ toast.className = toast.className.replace("show", ""); }}, 3000);
                        
                    }} catch (error) {{
                        console.error('Scan error:', error);
                    }} finally {{
                        setTimeout(() => {{
                            btn.disabled = false;
                            btn.innerHTML = '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line></svg> MANUEL TARAMAYI BAŞLAT';
                        }}, 5000);
                    }}
                }}
            </script>
        </body>
    </html>
    """
    return HTMLResponse(content=html_content)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
