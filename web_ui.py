#!/usr/bin/env python3
"""
Simple Web UI for the Binance Futures Trading Bot.
A lightweight Flask-based frontend for placing orders.
"""

from flask import Flask, render_template_string, request, jsonify
import os
from datetime import datetime
from dotenv import load_dotenv
from bot import BasicBot
from logger import setup_logger

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Initialize bot
bot = None
trade_log = []  # Store trade history

def get_bot():
    global bot
    if bot is None:
        api_key = os.getenv('BINANCE_API_KEY')
        api_secret = os.getenv('BINANCE_API_SECRET')
        print(f"[DEBUG] API Key present: {bool(api_key)}, Secret present: {bool(api_secret)}")
        if not api_key or not api_secret:
            print("[ERROR] Missing BINANCE_API_KEY or BINANCE_API_SECRET environment variables!")
            raise ValueError("Missing API credentials")
        bot = BasicBot(api_key, api_secret, testnet=True)
    return bot

def add_log(action, details, success=True):
    """Add entry to trade log"""
    trade_log.insert(0, {
        'time': datetime.now().strftime('%H:%M:%S'),
        'action': action,
        'details': details,
        'success': success
    })
    # Keep only last 20 entries
    if len(trade_log) > 20:
        trade_log.pop()

# HTML Template
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PrimeTrade - Trading Bot</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        body {
            font-family: 'Segoe UI', sans-serif;
            background: linear-gradient(135deg, #0d1421 0%, #1a2332 100%);
            min-height: 100vh;
            color: #e4e4e4;
            padding: 20px;
        }
        
        .container { max-width: 1400px; margin: 0 auto; }
        
        header {
            text-align: center;
            padding: 20px 0 30px;
        }
        
        h1 {
            font-size: 2rem;
            background: linear-gradient(90deg, #00d4ff, #00ff88);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 5px;
        }
        
        .subtitle { color: #666; font-size: 0.9rem; }
        
        .testnet-badge {
            display: inline-block;
            background: #e74c3c;
            color: white;
            padding: 4px 12px;
            border-radius: 15px;
            font-size: 0.75rem;
            margin-top: 8px;
        }
        
        .main-grid {
            display: grid;
            grid-template-columns: 1fr 400px;
            gap: 20px;
        }
        
        @media (max-width: 900px) {
            .main-grid { grid-template-columns: 1fr; }
        }
        
        .card {
            background: rgba(255, 255, 255, 0.03);
            border-radius: 12px;
            padding: 20px;
            border: 1px solid rgba(255, 255, 255, 0.08);
            overflow: hidden;
        }
        
        .card h2 {
            font-size: 1rem;
            color: #00d4ff;
            margin-bottom: 15px;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        
        /* Stats Row */
        .stats-row {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 15px;
            margin-bottom: 20px;
        }
        
        .stat-card {
            background: rgba(255, 255, 255, 0.03);
            border-radius: 10px;
            padding: 15px;
            text-align: center;
            border: 1px solid rgba(255, 255, 255, 0.08);
        }
        
        .stat-label { color: #666; font-size: 0.8rem; margin-bottom: 5px; }
        .stat-value { font-size: 1.3rem; font-weight: bold; color: #00ff88; }
        .stat-value.negative { color: #ff4757; }
        .stat-value.price { color: #00d4ff; }
        
        /* Trading Panel */
        .trading-panel { display: flex; flex-direction: column; gap: 20px; }
        
        .order-section {
            background: rgba(0, 212, 255, 0.05);
            border-radius: 10px;
            padding: 20px;
            border: 1px solid rgba(0, 212, 255, 0.2);
        }
        
        .order-section h3 {
            color: #00d4ff;
            font-size: 0.95rem;
            margin-bottom: 15px;
        }
        
        .form-row {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 10px;
            margin-bottom: 12px;
        }
        
        .form-group { 
            display: flex; 
            flex-direction: column; 
            gap: 5px;
            min-width: 0;
            overflow: hidden;
        }
        .form-group.full { grid-column: span 2; }
        
        label { font-size: 0.8rem; color: #888; }
        
        input, select {
            padding: 10px 12px;
            border-radius: 6px;
            border: 1px solid rgba(255, 255, 255, 0.15);
            background: rgba(0, 0, 0, 0.3);
            color: white;
            font-size: 0.95rem;
            width: 100%;
            box-sizing: border-box;
            min-width: 0;
        }
        
        input:focus, select:focus {
            outline: none;
            border-color: #00d4ff;
        }
        
        .btn-row {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 10px;
            margin-top: 15px;
        }
        
        .btn {
            padding: 12px;
            border: none;
            border-radius: 6px;
            font-size: 0.95rem;
            font-weight: bold;
            cursor: pointer;
            transition: all 0.2s;
        }
        
        .btn-buy {
            background: linear-gradient(135deg, #00b894, #00a085);
            color: white;
        }
        
        .btn-sell {
            background: linear-gradient(135deg, #e74c3c, #c0392b);
            color: white;
        }
        
        .btn:hover { transform: translateY(-1px); opacity: 0.9; }
        
        .btn:disabled {
            opacity: 0.5;
            cursor: not-allowed;
            transform: none;
        }
        
        /* How It Works */
        .how-it-works {
            background: rgba(0, 255, 136, 0.05);
            border: 1px solid rgba(0, 255, 136, 0.2);
            border-radius: 10px;
            padding: 15px;
            margin-bottom: 20px;
        }
        
        .how-it-works h3 {
            color: #00ff88;
            font-size: 0.9rem;
            margin-bottom: 10px;
        }
        
        .how-it-works ul {
            list-style: none;
            font-size: 0.85rem;
            color: #aaa;
        }
        
        .how-it-works li {
            padding: 4px 0;
            padding-left: 20px;
            position: relative;
        }
        
        .how-it-works li::before {
            content: "→";
            position: absolute;
            left: 0;
            color: #00ff88;
        }
        
        /* Activity Log */
        .activity-log {
            max-height: 300px;
            overflow-y: auto;
        }
        
        .log-entry {
            display: flex;
            gap: 10px;
            padding: 10px;
            border-bottom: 1px solid rgba(255, 255, 255, 0.05);
            font-size: 0.85rem;
        }
        
        .log-time { color: #666; min-width: 60px; }
        .log-action { color: #00d4ff; min-width: 80px; font-weight: 500; }
        .log-details { color: #aaa; flex: 1; }
        .log-entry.error .log-action { color: #ff4757; }
        .log-entry.success .log-action { color: #00ff88; }
        
        /* Positions Table */
        .positions-table {
            width: 100%;
            border-collapse: collapse;
            font-size: 0.9rem;
        }
        
        .positions-table th {
            text-align: left;
            padding: 10px;
            color: #666;
            font-weight: normal;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        }
        
        .positions-table td {
            padding: 12px 10px;
            border-bottom: 1px solid rgba(255, 255, 255, 0.05);
        }
        
        .positions-table td:last-child { text-align: right; }
        
        .long { color: #00ff88; }
        .short { color: #ff4757; }
        
        .close-btn {
            background: #e74c3c;
            color: white;
            border: none;
            padding: 5px 10px;
            border-radius: 4px;
            cursor: pointer;
            font-size: 0.8rem;
        }
        
        .close-btn:hover { background: #c0392b; }
        
        /* Result Message */
        .result-msg {
            margin-top: 15px;
            padding: 12px;
            border-radius: 6px;
            font-size: 0.9rem;
            display: none;
        }
        
        .result-msg.success {
            display: block;
            background: rgba(0, 255, 136, 0.1);
            border: 1px solid #00ff88;
            color: #00ff88;
        }
        
        .result-msg.error {
            display: block;
            background: rgba(255, 71, 87, 0.1);
            border: 1px solid #ff4757;
            color: #ff4757;
        }
        
        .no-positions {
            color: #666;
            text-align: center;
            padding: 30px;
        }
        
        .order-type-tabs {
            display: flex;
            gap: 5px;
            margin-bottom: 15px;
        }
        
        .tab-btn {
            flex: 1;
            padding: 8px;
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(255, 255, 255, 0.1);
            color: #888;
            border-radius: 5px;
            cursor: pointer;
            font-size: 0.85rem;
            transition: all 0.2s;
        }
        
        .tab-btn.active {
            background: rgba(0, 212, 255, 0.2);
            border-color: #00d4ff;
            color: #00d4ff;
        }
        
        .hidden { display: none !important; }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🤖 PrimeTrade Bot</h1>
            <p class="subtitle">Binance Futures Trading Bot Interface</p>
            <span class="testnet-badge">⚠️ TESTNET - Fake Money</span>
        </header>
        
        <!-- Stats Row -->
        <div class="stats-row">
            <div class="stat-card">
                <div class="stat-label">💰 Balance</div>
                <div class="stat-value" id="balance">$0.00</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">📊 Available</div>
                <div class="stat-value" id="available">$0.00</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">📈 Unrealized PnL</div>
                <div class="stat-value" id="pnl">$0.00</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">💹 BTC Price</div>
                <div class="stat-value price" id="btcPrice">$0.00</div>
            </div>
        </div>
        
        <div class="main-grid">
            <!-- Left Column -->
            <div>
                <!-- Open Positions -->
                <div class="card" style="margin-bottom: 20px;">
                    <h2>📊 Open Positions</h2>
                    <div id="positions">
                        <div class="no-positions">No open positions</div>
                    </div>
                </div>
                
                <!-- Activity Log -->
                <div class="card">
                    <h2>📋 Activity Log</h2>
                    <div class="activity-log" id="activityLog">
                        <div class="log-entry">
                            <span class="log-time">--:--</span>
                            <span class="log-action">INFO</span>
                            <span class="log-details">Bot ready. Place an order to start trading.</span>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Right Column - Trading Panel -->
            <div class="trading-panel">
                <!-- How It Works -->
                <div class="how-it-works">
                    <h3>📖 How It Works</h3>
                    <ul>
                        <li><strong>BUY/LONG</strong> = Bet price goes UP ↑</li>
                        <li><strong>SELL/SHORT</strong> = Bet price goes DOWN ↓</li>
                        <li><strong>Market</strong> = Execute immediately at current price</li>
                        <li><strong>Limit</strong> = Execute when price reaches your target</li>
                        <li><strong>Close Position</strong> = Exit and take profit/loss</li>
                    </ul>
                </div>
                
                <!-- Place Order -->
                <div class="order-section">
                    <h3>🚀 Place Order</h3>
                    
                    <div class="order-type-tabs">
                        <button class="tab-btn active" onclick="selectOrderType('market', this)">Market</button>
                        <button class="tab-btn" onclick="selectOrderType('limit', this)">Limit</button>
                        <button class="tab-btn" onclick="selectOrderType('stop', this)">Stop-Limit</button>
                        <button class="tab-btn" onclick="selectOrderType('oco', this)">OCO</button>
                    </div>
                    
                    <form id="orderForm" onsubmit="placeOrder(event)">
                        <input type="hidden" id="orderType" value="market">
                        
                        <div class="form-row">
                            <div class="form-group">
                                <label>Symbol</label>
                                <select id="symbol">
                                    <option value="BTCUSDT">BTCUSDT</option>
                                    <option value="ETHUSDT">ETHUSDT</option>
                                </select>
                            </div>
                            <div class="form-group">
                                <label>Quantity</label>
                                <input type="number" id="quantity" step="0.001" min="0.001" value="0.002" required>
                            </div>
                        </div>
                        
                        <div class="form-row hidden" id="priceRow">
                            <div class="form-group full">
                                <label>Limit Price ($)</label>
                                <input type="number" id="price" step="0.01" placeholder="Enter price">
                            </div>
                        </div>
                        
                        <div class="form-row hidden" id="stopPriceRow">
                            <div class="form-group full">
                                <label>Stop Trigger Price ($)</label>
                                <input type="number" id="stopPrice" step="0.01" placeholder="Trigger price">
                            </div>
                        </div>
                        
                        <div class="form-row hidden" id="ocoRow">
                            <div class="form-group">
                                <label>Take Profit Price ($)</label>
                                <input type="number" id="tpPrice" step="0.01" placeholder="TP price">
                            </div>
                            <div class="form-group">
                                <label>Stop Loss Price ($)</label>
                                <input type="number" id="slPrice" step="0.01" placeholder="SL trigger">
                            </div>
                        </div>
                        
                        <div id="ocoNote" class="hidden" style="font-size: 0.8rem; color: #888; margin-bottom: 10px;">
                            ℹ️ OCO places both Take-Profit and Stop-Loss orders. When one executes, close the other manually.
                        </div>
                        
                        <div class="btn-row">
                            <button type="button" class="btn btn-buy" onclick="submitOrder('BUY')">
                                📈 BUY / LONG
                            </button>
                            <button type="button" class="btn btn-sell" onclick="submitOrder('SELL')">
                                📉 SELL / SHORT
                            </button>
                        </div>
                    </form>
                    
                    <div class="result-msg" id="result"></div>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        // Load data on page load
        document.addEventListener('DOMContentLoaded', function() {
            loadAll();
            setInterval(loadAll, 3000);  // Auto-refresh every 3s
        });
        
        function loadAll() {
            loadAccount();
            loadPrice();
            loadPositions();
            loadActivityLog();
        }
        
        function selectOrderType(type, btn) {
            document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            document.getElementById('orderType').value = type;
            
            document.getElementById('priceRow').classList.toggle('hidden', type === 'market' || type === 'oco');
            document.getElementById('stopPriceRow').classList.toggle('hidden', type !== 'stop');
            document.getElementById('ocoRow').classList.toggle('hidden', type !== 'oco');
            document.getElementById('ocoNote').classList.toggle('hidden', type !== 'oco');
        }
        
        async function loadAccount() {
            try {
                const res = await fetch('/api/account');
                const data = await res.json();
                
                if (data.error) {
                    document.getElementById('balance').textContent = 'API Error';
                    document.getElementById('available').textContent = data.error.substring(0, 20);
                    console.error('Account API Error:', data.error);
                    return;
                }
                
                document.getElementById('balance').textContent = '$' + parseFloat(data.totalWalletBalance || 0).toFixed(2);
                document.getElementById('available').textContent = '$' + parseFloat(data.availableBalance || 0).toFixed(2);
                
                const pnl = parseFloat(data.totalUnrealizedProfit || 0);
                const pnlEl = document.getElementById('pnl');
                pnlEl.textContent = (pnl >= 0 ? '+$' : '-$') + Math.abs(pnl).toFixed(2);
                pnlEl.className = 'stat-value ' + (pnl >= 0 ? '' : 'negative');
            } catch (e) { console.error(e); }
        }
        
        async function loadPrice() {
            try {
                const res = await fetch('/api/price/BTCUSDT');
                const data = await res.json();
                document.getElementById('btcPrice').textContent = '$' + parseFloat(data.price).toLocaleString();
            } catch (e) { console.error(e); }
        }
        
        async function loadPositions() {
            try {
                const res = await fetch('/api/positions');
                const positions = await res.json();
                const container = document.getElementById('positions');
                
                if (!positions.length) {
                    container.innerHTML = '<div class="no-positions">No open positions - Place an order to start!</div>';
                    return;
                }
                
                let html = '<table class="positions-table"><tr><th>Symbol</th><th>Side</th><th>Size</th><th>Entry</th><th>PnL</th><th></th></tr>';
                
                positions.forEach(pos => {
                    const amt = parseFloat(pos.positionAmt) || 0;
                    const side = amt > 0 ? 'LONG' : 'SHORT';
                    const pnl = parseFloat(pos.unRealizedProfit) || parseFloat(pos.unrealizedProfit) || 0;
                    const entry = parseFloat(pos.entryPrice) || 0;
                    
                    html += `<tr>
                        <td>${pos.symbol}</td>
                        <td class="${amt > 0 ? 'long' : 'short'}">${side}</td>
                        <td>${Math.abs(amt).toFixed(4)}</td>
                        <td>$${entry.toLocaleString()}</td>
                        <td class="${pnl >= 0 ? 'long' : 'short'}">${pnl >= 0 ? '+' : ''}$${pnl.toFixed(2)}</td>
                        <td><button class="close-btn" onclick="closePosition('${pos.symbol}', ${Math.abs(amt)}, '${amt > 0 ? 'SELL' : 'BUY'}')">Close</button></td>
                    </tr>`;
                });
                
                container.innerHTML = html + '</table>';
            } catch (e) { console.error(e); }
        }
        
        async function loadActivityLog() {
            try {
                const res = await fetch('/api/logs');
                const logs = await res.json();
                const container = document.getElementById('activityLog');
                
                if (!logs.length) {
                    container.innerHTML = '<div class="log-entry"><span class="log-time">--:--</span><span class="log-action">INFO</span><span class="log-details">Bot ready.</span></div>';
                    return;
                }
                
                container.innerHTML = logs.map(log => `
                    <div class="log-entry ${log.success ? 'success' : 'error'}">
                        <span class="log-time">${log.time}</span>
                        <span class="log-action">${log.action}</span>
                        <span class="log-details">${log.details}</span>
                    </div>
                `).join('');
            } catch (e) { console.error(e); }
        }
        
        async function submitOrder(side) {
            const type = document.getElementById('orderType').value;
            const symbol = document.getElementById('symbol').value;
            const quantity = parseFloat(document.getElementById('quantity').value);
            const price = parseFloat(document.getElementById('price').value) || null;
            const stopPrice = parseFloat(document.getElementById('stopPrice').value) || null;
            const tpPrice = parseFloat(document.getElementById('tpPrice').value) || null;
            const slPrice = parseFloat(document.getElementById('slPrice').value) || null;
            
            const resultEl = document.getElementById('result');
            resultEl.className = 'result-msg';
            resultEl.textContent = '⏳ Placing order...';
            resultEl.style.display = 'block';
            
            try {
                const res = await fetch('/api/order', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ type, symbol, side, quantity, price, stopPrice, tpPrice, slPrice })
                });
                
                const data = await res.json();
                
                if (data.error) {
                    resultEl.className = 'result-msg error';
                    resultEl.textContent = '❌ ' + data.error;
                } else {
                    resultEl.className = 'result-msg success';
                    if (type === 'oco') {
                        resultEl.textContent = '✅ OCO orders placed! TP + SL active';
                    } else {
                        resultEl.textContent = '✅ ' + side + ' order placed! ID: ' + data.orderId;
                    }
                    loadAll();
                }
            } catch (e) {
                resultEl.className = 'result-msg error';
                resultEl.textContent = '❌ Error: ' + e.message;
            }
            
            setTimeout(() => { resultEl.style.display = 'none'; }, 5000);
        }
        
        async function closePosition(symbol, quantity, side) {
            if (!confirm('Close this position?')) return;
            
            try {
                const res = await fetch('/api/order', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ type: 'market', symbol, side, quantity })
                });
                
                const data = await res.json();
                if (data.error) alert('Error: ' + data.error);
                else {
                    alert('Position closed!');
                    loadAll();
                }
            } catch (e) { alert('Error: ' + e.message); }
        }
        
        function placeOrder(e) { e.preventDefault(); }
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/account')
def api_account():
    try:
        return jsonify(get_bot().get_account_info())
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/price/<symbol>')
def api_price(symbol):
    try:
        price = get_bot().get_symbol_price(symbol)
        return jsonify({'symbol': symbol, 'price': price})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/positions')
def api_positions():
    try:
        return jsonify(get_bot().get_positions())
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/logs')
def api_logs():
    return jsonify(trade_log)

@app.route('/api/order', methods=['POST'])
def api_order():
    try:
        data = request.json
        order_type = data.get('type', 'market')
        symbol = data.get('symbol')
        side = data.get('side')
        quantity = data.get('quantity')
        price = data.get('price')
        stop_price = data.get('stopPrice')
        tp_price = data.get('tpPrice')
        sl_price = data.get('slPrice')
        
        b = get_bot()
        
        if order_type == 'market':
            order = b.place_market_order(symbol, side, quantity)
            add_log(f'MARKET {side}', f'{quantity} {symbol} @ market price')
        elif order_type == 'limit':
            order = b.place_limit_order(symbol, side, quantity, price)
            add_log(f'LIMIT {side}', f'{quantity} {symbol} @ ${price}')
        elif order_type == 'stop':
            order = b.place_stop_limit_order(symbol, side, quantity, price, stop_price)
            add_log(f'STOP {side}', f'{quantity} {symbol} trigger ${stop_price}')
        elif order_type == 'oco':
            # OCO: place both take-profit and stop-loss
            orders = b.place_oco_order(symbol, side, quantity, tp_price, sl_price, sl_price * 0.995)
            add_log(f'OCO {side}', f'{quantity} {symbol} TP:${tp_price} SL:${sl_price}')
            return jsonify({'orderId': 'OCO', 'orders': len(orders)})
        else:
            return jsonify({'error': f'Unknown order type'}), 400
        
        return jsonify(order)
    except Exception as e:
        add_log('ERROR', str(e), success=False)
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    setup_logger()
    print("\n🤖 PrimeTrade Bot - Web UI")
    print("=" * 40)
    port = int(os.environ.get('PORT', 5000))
    print(f"Open: http://localhost:{port}")
    print("=" * 40)
    app.run(debug=False, host='0.0.0.0', port=port)
