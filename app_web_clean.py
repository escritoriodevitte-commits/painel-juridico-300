from flask import Flask, jsonify
import os
import json
from datetime import datetime

app = Flask(__name__)

# Database simples em JSON
DB_FILE = "data.json"

def get_db():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {
        'processos': [],
        'clientes': [],
        'analises': []
    }

def save_db(data):
    with open(DB_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def formatar_moeda(valor):
    try:
        return f"R$ {float(valor):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except:
        return "R$ 0,00"

# ROTAS
@app.route('/')
def home():
    db = get_db()
    total = len(db['processos'])
    acordos = len([p for p in db['processos'] if p.get('status') == 'acordo'])
    andamento = len([p for p in db['processos'] if p.get('status') == 'em_andamento'])
    economia = sum(float(p.get('economia', 0) or 0) for p in db['processos'])
    
    return jsonify({
        'app': 'Painel Jurídico v2',
        'status': 'online',
        'dados': {
            'total_processos': total,
            'acordos': acordos,
            'em_andamento': andamento,
            'economia_processual': formatar_moeda(economia),
            'total_clientes': len(db['clientes'])
        }
    })

@app.route('/api/processos')
def processos():
    db = get_db()
    return jsonify(db['processos'])

@app.route('/api/clientes')
def clientes():
    db = get_db()
    return jsonify(db['clientes'])

@app.route('/api/analises')
def analises():
    db = get_db()
    return jsonify(db['analises'])

@app.route('/health')
def health():
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()}), 200

@app.errorhandler(404)
def not_found(e):
    return jsonify({'erro': 'Rota não encontrada'}), 404

@app.errorhandler(500)
def server_error(e):
    return jsonify({'erro': 'Erro interno do servidor'}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
