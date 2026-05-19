from flask import Flask, jsonify, request
import os
import sys
sys.path.insert(0, os.path.dirname(__file__))

app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False

try:
    from core import database as db
    db.init_db()
except Exception as e:
    print(f"Database error: {e}")
    db = None

try:
    from modules.calculadora.calc import calcular_verbas
except Exception as e:
    print(f"Calculator error: {e}")
    calcular_verbas = None

try:
    from modules.ia.gerador import GeradorPecas
    gerador = GeradorPecas()
except Exception as e:
    print(f"Generator error: {e}")
    gerador = None

def formatar_moeda(valor):
    try:
        return f"R$ {float(valor):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except:
        return "R$ 0,00"

@app.route('/')
def index():
    lawsuits = db.get_all_lawsuits()
    total = len(lawsuits)
    acordos = len([l for l in lawsuits if l['status'] == 'acordo'])
    andamento = len([l for l in lawsuits if l['status'] == 'em_andamento'])
    economia = sum(l.get('economia_processual', 0) or 0 for l in lawsuits)
    clientes = len(db.get_all_clientes())
    
    return jsonify({
        'status': 'ok',
        'data': {
            'total_processos': total,
            'acordos': acordos,
            'em_andamento': andamento,
            'economia': formatar_moeda(economia),
            'total_clientes': clientes,
            'ultimos_processos': [
                {
                    'numero': l['numero_processo'],
                    'vara': l['vara'],
                    'status': l['status'],
                    'valor': formatar_moeda(l.get('valor_pedido', 0) or 0)
                } for l in lawsuits[:5]
            ]
        }
    })

@app.route('/api/processos')
def api_processos():
    lawsuits = db.get_all_lawsuits()
    return jsonify([
        {
            'id': l.get('id'),
            'numero': l['numero_processo'],
            'vara': l['vara'],
            'status': l['status'],
            'valor': formatar_moeda(l.get('valor_pedido', 0) or 0),
            'cliente': l.get('cliente', 'N/A')
        } for l in lawsuits
    ])

@app.route('/api/clientes')
def api_clientes():
    clientes = db.get_all_clientes()
    return jsonify([
        {
            'id': c.get('id'),
            'nome': c['nome'],
            'cpf': c['cpf'],
            'telefone': c.get('telefone', '')
        } for c in clientes
    ])

@app.route('/api/calcular', methods=['POST'])
def api_calcular():
    data = request.json
    try:
        resultado = calcular_verbas(
            salario=data.get('salario', 0),
            meses=data.get('meses', 0),
            tipo=data.get('tipo', 'aviso_previo')
        )
        return jsonify({'status': 'ok', 'resultado': resultado})
    except Exception as e:
        return jsonify({'status': 'erro', 'mensagem': str(e)}), 400

@app.route('/api/gerar-peca', methods=['POST'])
def api_gerar_peca():
    data = request.json
    try:
        peca = gerador.gerar(
            tipo_peca=data.get('tipo', 'peca_inicial'),
            dados=data.get('dados', {})
        )
        return jsonify({'status': 'ok', 'peca': peca})
    except Exception as e:
        return jsonify({'status': 'erro', 'mensagem': str(e)}), 400

@app.route('/health')
def health():
    return jsonify({'status': 'healthy'}), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
