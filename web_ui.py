#!/usr/bin/env python3
"""
Simple Web UI for the Binance Futures Trading Bot.
A lightweight Flask-based frontend for placing orders.
"""

from flask import Flask, render_template_string, request, jsonify
import os
from dotenv import load_dotenv
from bot import BasicBot
from logger import setup_logger

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Initialize bot
bot = None

def get_bot():
    global bot
    if bot is None:
        api_key = os.getenv('BINANCE_API_KEY')
        api_secret = os.getenv('BINANCE_API_SECRET')
        bot = BasicBot(api_key, api_secret, testnet=True)
    return bot

# HTML Template
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PrimeTrade - Trading Bot</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
            min-height: 100vh;
            color: #e4e4e4;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
        
        header {
            text-align: center;
            padding: 30px 0;
            border-bottom: 1px solid #333;
            margin-bottom: 30px;
        }
        
        h1 {
            font-size: 2.5rem;
            background: linear-gradient(90deg, #00d4ff, #7b2cbf);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 10px;
        }
        
        .subtitle {
            color: #888;
            font-size: 0.9rem;
        }
        
        .testnet-badge {
            display: inline-block;
            background: #ff6b35;
            color: white;
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 0.8rem;
            margin-top: 10px;
        }
        
        .dashboard {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .card {
            background: rgba(255, 255, 255, 0.05);
            border-radius: 15px;
            padding: 25px;
            border: 1px solid rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
        }
        
        .card h2 {
            font-size: 1.2rem;
            margin-bottom: 20px;
            color: #00d4ff;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .stat {
            display: flex;
            justify-content: space-between;
            padding: 10px 0;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        }
        
        .stat:last-child {
            border-bottom: none;
        }
        
        .stat-label {
            color: #888;
        }
        
        .stat-value {
            font-weight: bold;
            color: #00ff88;
        }
        
        .stat-value.negative {
            color: #ff4757;
        }
        
        .order-form {
            display: grid;
            gap: 15px;
        }
        
        .form-group {
            display: flex;
            flex-direction: column;
            gap: 5px;
        }
        
        label {
            font-size: 0.85rem;
            color: #888;
        }
        
        input, select {
            padding: 12px;
            border-radius: 8px;
            border: 1px solid rgba(255, 255, 255, 0.2);
            background: rgba(255, 255, 255, 0.05);
            color: white;
            font-size: 1rem;
        }
        
        input:focus, select:focus {
            outline: none;
            border-color: #00d4ff;
        }
        
        .btn-group {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 10px;
            margin-top: 10px;
        }
        
        button {
            padding: 15px;
            border: none;
            border-radius: 8px;
            font-size: 1rem;
            font-weight: bold;
            cursor: pointer;
            transition: all 0.3s;
        }
        
        .btn-buy {
            background: linear-gradient(135deg, #00b894, #00cec9);
            color: white;
        }
        
        .btn-sell {
            background: linear-gradient(135deg, #e17055, #d63031);
            color: white;
        }
        
        button:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 20px rgba(0, 0, 0, 0.3);
        }
        
        .btn-secondary {
            background: rgba(255, 255, 255, 0.1);
            color: white;
            grid-column: span 2;
        }
        
        #result {
            margin-top: 20px;
            padding: 15px;
            border-radius: 8px;
            display: none;
        }
        
        #result.success {
            display: block;
            background: rgba(0, 255, 136, 0.1);
            border: 1px solid #00ff88;
        }
        
        #result.error {
            display: block;
            background: rgba(255, 71, 87, 0.1);
            border: 1px solid #ff4757;
        }
        
        .positions-table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 15px;
        }
        
        .positions-table th, .positions-table td {
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        }
        
        .positions-table th {
            color: #888;
            font-weight: normal;
        }
        
        .long { color: #00ff88; }
        .short { color: #ff4757; }
        
        .refresh-btn {
            background: rgba(0, 212, 255, 0.2);
            border: 1px solid #00d4ff;
            color: #00d4ff;
            padding: 8px 15px;
            border-radius: 5px;
            cursor: pointer;
            font-size: 0.85rem;
        }
        
        .price-display {
            font-size: 2rem;
            font-weight: bold;
            color: #00ff88;
            text-align: center;
            padding: 20px 0;
        }
        
        .order-types {
            display: flex;
            gap: 10px;
            margin-bottom: 15px;
        }
        
        .order-type-btn {
            flex: 1;
            padding: 10px;
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(255, 255, 255, 0.2);
            border-radius: 8px;
            color: #888;
            cursor: pointer;
            transition: all 0.3s;
        }
        
        .order-type-btn.active {
            background: rgba(0, 212, 255, 0.2);
            border-color: #00d4ff;
            color: #00d4ff;
        }
        
        .hidden {
            display: none !important;
        }
        
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }
        
        .loading {
            animation: pulse 1s infinite;
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🚀 PrimeTrade</h1>
            <p class="subtitle">Binance Futures Trading Bot</p>
            <span class="testnet-badge">⚠️ TESTNET MODE</span>
        </header>
        
        <div class="dashboard">
            <!-- Account Info -->
            <div class="card">
                <h2>💰 Account</h2>
                <div class="stat">
                    <span class="stat-label">Balance</span>
                    <span class="stat-value" id="balance">Loading...</span>
                </div>
                <div class="stat">
                    <span class="stat-label">Available</span>
                    <span class="stat-value" id="available">Loading...</span>
                </div>
                <div class="stat">
                    <span class="stat-label">Unrealized PnL</span>
                    <span class="stat-value" id="pnl">Loading...</span>
                </div>
                <button class="refresh-btn" onclick="loadAccount()" style="margin-top: 15px;">🔄 Refresh</button>
            </div>
            
            <!-- Price Display -->
            <div class="card">
                <h2>📊 Market Price</h2>
                <div class="form-group">
                    <select id="priceSymbol" onchange="loadPrice()">
                        <option value="BTCUSDT">BTCUSDT</option>
                        <option value="ETHUSDT">ETHUSDT</option>
                        <option value="BNBUSDT">BNBUSDT</option>
                        <option value="SOLUSDT">SOLUSDT</option>
                    </select>
                </div>
                <div class="price-display" id="currentPrice">$0.00</div>
                <button class="refresh-btn" onclick="loadPrice()">🔄 Refresh Price</button>
            </div>
            
            <!-- Place Order -->
            <div class="card">
                <h2>📝 Place Order</h2>
                
                <div class="order-types">
                    <button class="order-type-btn active" onclick="selectOrderType('market')">Market</button>
                    <button class="order-type-btn" onclick="selectOrderType('limit')">Limit</button>
                    <button class="order-type-btn" onclick="selectOrderType('stop')">Stop-Limit</button>
                </div>
                
                <form class="order-form" onsubmit="placeOrder(event)">
                    <input type="hidden" id="orderType" value="market">
                    
                    <div class="form-group">
                        <label>Symbol</label>
                        <select id="symbol">
                            <option value="BTCUSDT">BTCUSDT</option>
                            <option value="ETHUSDT">ETHUSDT</option>
                            <option value="BNBUSDT">BNBUSDT</option>
                            <option value="SOLUSDT">SOLUSDT</option>
                        </select>
                    </div>
                    
                    <div class="form-group">
                        <label>Quantity</label>
                        <input type="number" id="quantity" step="0.001" min="0.001" value="0.002" required>
                    </div>
                    
                    <div class="form-group hidden" id="priceGroup">
                        <label>Price</label>
                        <input type="number" id="price" step="0.01" min="0">
                    </div>
                    
                    <div class="form-group hidden" id="stopPriceGroup">
                        <label>Stop Price (Trigger)</label>
                        <input type="number" id="stopPrice" step="0.01" min="0">
                    </div>
                    
                    <div class="btn-group">
                        <button type="submit" class="btn-buy" onclick="document.getElementById('side').value='BUY'">
                            📈 BUY / LONG
                        </button>
                        <button type="submit" class="btn-sell" onclick="document.getElementById('side').value='SELL'">
                            📉 SELL / SHORT
                        </button>
                    </div>
                    <input type="hidden" id="side" value="BUY">
                </form>
                
                <div id="result"></div>
            </div>
            
            <!-- Positions -->
            <div class="card">
                <h2>📈 Open Positions</h2>
                <button class="refresh-btn" onclick="loadPositions()" style="margin-bottom: 15px;">🔄 Refresh</button>
                <div id="positions">
                    <p style="color: #888;">No positions</p>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        // Load data on page load
        document.addEventListener('DOMContentLoaded', function() {
            loadAccount();
            loadPrice();
            loadPositions();
        });
        
        function selectOrderType(type) {
            document.querySelectorAll('.order-type-btn').forEach(btn => btn.classList.remove('active'));
            event.target.classList.add('active');
            document.getElementById('orderType').value = type;
            
            const priceGroup = document.getElementById('priceGroup');
            const stopPriceGroup = document.getElementById('stopPriceGroup');
            
            if (type === 'market') {
                priceGroup.classList.add('hidden');
                stopPriceGroup.classList.add('hidden');
            } else if (type === 'limit') {
                priceGroup.classList.remove('hidden');
                stopPriceGroup.classList.add('hidden');
            } else if (type === 'stop') {
                priceGroup.classList.remove('hidden');
                stopPriceGroup.classList.remove('hidden');
            }
        }
        
        async function loadAccount() {
            try {
                const response = await fetch('/api/account');
                const data = await response.json();
                
                document.getElementById('balance').textContent = '$' + parseFloat(data.totalWalletBalance).toFixed(2);
                document.getElementById('available').textContent = '$' + parseFloat(data.availableBalance).toFixed(2);
                
                const pnl = parseFloat(data.totalUnrealizedProfit);
                const pnlEl = document.getElementById('pnl');
                pnlEl.textContent = (pnl >= 0 ? '+' : '') + '$' + pnl.toFixed(4);
                pnlEl.className = 'stat-value ' + (pnl >= 0 ? '' : 'negative');
            } catch (e) {
                console.error('Error loading account:', e);
            }
        }
        
        async function loadPrice() {
            const symbol = document.getElementById('priceSymbol').value;
            try {
                const response = await fetch('/api/price/' + symbol);
                const data = await response.json();
                document.getElementById('currentPrice').textContent = '$' + parseFloat(data.price).toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2});
            } catch (e) {
                console.error('Error loading price:', e);
            }
        }
        
        async function loadPositions() {
            try {
                const response = await fetch('/api/positions');
                const positions = await response.json();
                
                const container = document.getElementById('positions');
                
                if (positions.length === 0) {
                    container.innerHTML = '<p style="color: #888;">No open positions</p>';
                    return;
                }
                
                let html = '<table class="positions-table"><tr><th>Symbol</th><th>Side</th><th>Size</th><th>Entry</th><th>PnL</th></tr>';
                
                positions.forEach(pos => {
                    const amt = parseFloat(pos.positionAmt);
                    const side = amt > 0 ? 'LONG' : 'SHORT';
                    const sideClass = amt > 0 ? 'long' : 'short';
                    const pnl = parseFloat(pos.unrealizedProfit);
                    const pnlClass = pnl >= 0 ? 'long' : 'short';
                    
                    html += `<tr>
                        <td>${pos.symbol}</td>
                        <td class="${sideClass}">${side}</td>
                        <td>${Math.abs(amt)}</td>
                        <td>$${parseFloat(pos.entryPrice).toFixed(2)}</td>
                        <td class="${pnlClass}">${pnl >= 0 ? '+' : ''}${pnl.toFixed(4)}</td>
                    </tr>`;
                });
                
                html += '</table>';
                container.innerHTML = html;
            } catch (e) {
                console.error('Error loading positions:', e);
            }
        }
        
        async function placeOrder(event) {
            event.preventDefault();
            
            const orderType = document.getElementById('orderType').value;
            const symbol = document.getElementById('symbol').value;
            const side = document.getElementById('side').value;
            const quantity = document.getElementById('quantity').value;
            const price = document.getElementById('price').value;
            const stopPrice = document.getElementById('stopPrice').value;
            
            const resultEl = document.getElementById('result');
            resultEl.className = '';
            resultEl.style.display = 'none';
            
            try {
                const response = await fetch('/api/order', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        type: orderType,
                        symbol: symbol,
                        side: side,
                        quantity: parseFloat(quantity),
                        price: price ? parseFloat(price) : null,
                        stopPrice: stopPrice ? parseFloat(stopPrice) : null
                    })
                });
                
                const data = await response.json();
                
                if (data.error) {
                    resultEl.className = 'error';
                    resultEl.textContent = '❌ ' + data.error;
                } else {
                    resultEl.className = 'success';
                    resultEl.textContent = '✅ Order placed! ID: ' + data.orderId;
                    loadAccount();
                    loadPositions();
                }
            } catch (e) {
                resultEl.className = 'error';
                resultEl.textContent = '❌ Error: ' + e.message;
            }
        }
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
        account = get_bot().get_account_info()
        return jsonify(account)
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
        positions = get_bot().get_positions()
        return jsonify(positions)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

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
        
        bot = get_bot()
        
        if order_type == 'market':
            order = bot.place_market_order(symbol, side, quantity)
        elif order_type == 'limit':
            order = bot.place_limit_order(symbol, side, quantity, price)
        elif order_type == 'stop':
            order = bot.place_stop_limit_order(symbol, side, quantity, price, stop_price)
        else:
            return jsonify({'error': f'Unknown order type: {order_type}'}), 400
        
        return jsonify(order)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/orders')
def api_orders():
    try:
        orders = get_bot().get_open_orders()
        return jsonify(orders)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    setup_logger()
    print("\n🚀 PrimeTrade Web UI")
    print("=" * 40)
    print("Open in browser: http://localhost:5000")
    print("=" * 40)
    print("\nPress Ctrl+C to stop\n")
    app.run(debug=True, port=5000)

