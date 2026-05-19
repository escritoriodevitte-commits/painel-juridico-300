"""
Core Database - Painel Estratégico Jurídico v2
SQLite local com tabelas: clientes, processos, magistrados, acordos, referências, peças, parâmetros
"""
import sqlite3
import os
from datetime import datetime
from typing import Optional, List, Dict, Any

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "juridico.db")


def get_connection():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.executescript("""
    CREATE TABLE IF NOT EXISTS clientes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        cpf TEXT,
        telefone TEXT,
        email TEXT,
        endereco TEXT,
        observacoes TEXT,
        created_at TEXT DEFAULT (datetime('now')),
        updated_at TEXT DEFAULT (datetime('now'))
    );

    CREATE TABLE IF NOT EXISTS judges (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        vara TEXT NOT NULL,
        comarca TEXT,
        tendencia_conciliatoria TEXT CHECK(tendencia_conciliatoria IN ('alta','media','baixa')),
        faixa_acordo_min REAL,
        faixa_acordo_max REAL,
        postura_justa_causa TEXT,
        postura_acidente TEXT,
        postura_danos_morais TEXT,
        postura_horas_extras TEXT,
        postura_rescisao_indireta TEXT,
        observacoes TEXT,
        created_at TEXT DEFAULT (datetime('now')),
        updated_at TEXT DEFAULT (datetime('now'))
    );

    CREATE TABLE IF NOT EXISTS lawsuits (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        numero_processo TEXT NOT NULL,
        vara TEXT NOT NULL,
        judge_id INTEGER,
        cliente_id INTEGER,
        reclamante TEXT NOT NULL,
        reclamada TEXT NOT NULL,
        tese_inicial TEXT,
        tese_defesa TEXT,
        status TEXT NOT NULL DEFAULT 'em_andamento'
            CHECK(status IN ('em_andamento','acordo','sentenca_procedente','sentenca_improcedente','sentenca_parcial','arquivado')),
        resultado TEXT,
        valor_pedido REAL,
        valor_obtido REAL,
        economia_processual REAL,
        data_distribuicao TEXT,
        data_encerramento TEXT,
        created_at TEXT DEFAULT (datetime('now')),
        updated_at TEXT DEFAULT (datetime('now')),
        FOREIGN KEY (judge_id) REFERENCES judges(id),
        FOREIGN KEY (cliente_id) REFERENCES clientes(id)
    );

    CREATE TABLE IF NOT EXISTS settlements (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        lawsuit_id INTEGER NOT NULL,
        tipo TEXT NOT NULL CHECK(tipo IN ('acordo','sentenca')),
        valor_pedido REAL,
        valor_obtido REAL,
        parcelas INTEGER,
        condicao_parcelamento TEXT,
        clausulas_especiais TEXT,
        data_homologacao TEXT,
        dados_bancarios TEXT,
        observacoes TEXT,
        created_at TEXT DEFAULT (datetime('now')),
        updated_at TEXT DEFAULT (datetime('now')),
        FOREIGN KEY (lawsuit_id) REFERENCES lawsuits(id)
    );

    CREATE TABLE IF NOT EXISTS legal_references (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tipo TEXT NOT NULL CHECK(tipo IN ('doutrina','jurisprudencia','sumula','oj')),
        tema TEXT NOT NULL CHECK(tema IN ('justa_causa','acidente_trabalho','danos_morais','horas_extras',
            'rescisao_indireta','verbas_rescisorias','terceirizacao','equiparacao_salarial','prescricao',
            'honorarios','outros','aviso_previo','correcao_monetaria','estabilidade','insalubridade',
            'reforma_trabalhista','rito_sumarissimo','salario','vinculo')),
        titulo TEXT NOT NULL,
        autor TEXT,
        fonte TEXT,
        trecho TEXT NOT NULL,
        ano INTEGER,
        created_at TEXT DEFAULT (datetime('now')),
        updated_at TEXT DEFAULT (datetime('now'))
    );

    CREATE TABLE IF NOT EXISTS negotiation_params (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        judge_id INTEGER,
        tema_processual TEXT NOT NULL CHECK(tema_processual IN ('justa_causa','acidente_trabalho','danos_morais','horas_extras','rescisao_indireta','outros')),
        valor_inicial_sugerido REAL,
        faixa_fechamento_min REAL,
        faixa_fechamento_max REAL,
        estrategia_recomendada TEXT,
        observacoes TEXT,
        created_at TEXT DEFAULT (datetime('now')),
        updated_at TEXT DEFAULT (datetime('now')),
        FOREIGN KEY (judge_id) REFERENCES judges(id)
    );

    CREATE TABLE IF NOT EXISTS generated_pieces (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        lawsuit_id INTEGER,
        tipo_peca TEXT NOT NULL,
        conteudo TEXT NOT NULL,
        gerado_por TEXT DEFAULT 'template',
        created_at TEXT DEFAULT (datetime('now')),
        FOREIGN KEY (lawsuit_id) REFERENCES lawsuits(id)
    );
    """)
    conn.commit()
    conn.close()


# ==================== CLIENTES ====================
def get_all_clientes() -> List[Dict]:
    conn = get_connection()
    rows = conn.execute("SELECT * FROM clientes ORDER BY nome").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_cliente_by_id(cliente_id: int) -> Optional[Dict]:
    conn = get_connection()
    row = conn.execute("SELECT * FROM clientes WHERE id=?", (cliente_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def create_cliente(data: Dict) -> int:
    conn = get_connection()
    c = conn.execute("""INSERT INTO clientes (nome, cpf, telefone, email, endereco, observacoes)
        VALUES (?,?,?,?,?,?)""",
        (data.get('nome'), data.get('cpf'), data.get('telefone'),
         data.get('email'), data.get('endereco'), data.get('observacoes')))
    conn.commit()
    lid = c.lastrowid
    conn.close()
    return lid


def update_cliente(cliente_id: int, data: Dict):
    conn = get_connection()
    fields = []
    values = []
    for k, v in data.items():
        if k not in ('id', 'created_at'):
            fields.append(f"{k}=?")
            values.append(v)
    fields.append("updated_at=datetime('now')")
    values.append(cliente_id)
    conn.execute(f"UPDATE clientes SET {', '.join(fields)} WHERE id=?", values)
    conn.commit()
    conn.close()


def delete_cliente(cliente_id: int):
    conn = get_connection()
    conn.execute("DELETE FROM clientes WHERE id=?", (cliente_id,))
    conn.commit()
    conn.close()


def search_clientes(query: str) -> List[Dict]:
    conn = get_connection()
    rows = conn.execute("SELECT * FROM clientes WHERE nome LIKE ? OR cpf LIKE ? OR email LIKE ? ORDER BY nome",
                        (f"%{query}%", f"%{query}%", f"%{query}%")).fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ==================== JUDGES ====================
def get_all_judges() -> List[Dict]:
    conn = get_connection()
    rows = conn.execute("SELECT * FROM judges ORDER BY name").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_judge_by_id(judge_id: int) -> Optional[Dict]:
    conn = get_connection()
    row = conn.execute("SELECT * FROM judges WHERE id=?", (judge_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def create_judge(data: Dict) -> int:
    conn = get_connection()
    c = conn.execute("""INSERT INTO judges (name, vara, comarca, tendencia_conciliatoria,
        faixa_acordo_min, faixa_acordo_max, postura_justa_causa, postura_acidente,
        postura_danos_morais, postura_horas_extras, postura_rescisao_indireta, observacoes)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?)""",
        (data.get('name'), data.get('vara'), data.get('comarca'), data.get('tendencia_conciliatoria'),
         data.get('faixa_acordo_min'), data.get('faixa_acordo_max'), data.get('postura_justa_causa'),
         data.get('postura_acidente'), data.get('postura_danos_morais'), data.get('postura_horas_extras'),
         data.get('postura_rescisao_indireta'), data.get('observacoes')))
    conn.commit()
    lid = c.lastrowid
    conn.close()
    return lid


def update_judge(judge_id: int, data: Dict):
    conn = get_connection()
    fields = []
    values = []
    for k, v in data.items():
        if k not in ('id', 'created_at'):
            fields.append(f"{k}=?")
            values.append(v)
    fields.append("updated_at=datetime('now')")
    values.append(judge_id)
    conn.execute(f"UPDATE judges SET {', '.join(fields)} WHERE id=?", values)
    conn.commit()
    conn.close()


def delete_judge(judge_id: int):
    conn = get_connection()
    conn.execute("DELETE FROM judges WHERE id=?", (judge_id,))
    conn.commit()
    conn.close()


# ==================== LAWSUITS ====================
def get_all_lawsuits() -> List[Dict]:
    conn = get_connection()
    rows = conn.execute("""SELECT l.*, j.name as judge_name, c.nome as cliente_nome
        FROM lawsuits l
        LEFT JOIN judges j ON l.judge_id = j.id
        LEFT JOIN clientes c ON l.cliente_id = c.id
        ORDER BY l.created_at DESC""").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_lawsuit_by_id(lawsuit_id: int) -> Optional[Dict]:
    conn = get_connection()
    row = conn.execute("""SELECT l.*, j.name as judge_name, c.nome as cliente_nome
        FROM lawsuits l
        LEFT JOIN judges j ON l.judge_id = j.id
        LEFT JOIN clientes c ON l.cliente_id = c.id
        WHERE l.id=?""", (lawsuit_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def create_lawsuit(data: Dict) -> int:
    conn = get_connection()
    eco = (data.get('valor_pedido', 0) or 0) - (data.get('valor_obtido', 0) or 0)
    c = conn.execute("""INSERT INTO lawsuits (numero_processo, vara, judge_id, cliente_id, reclamante, reclamada,
        tese_inicial, tese_defesa, status, resultado, valor_pedido, valor_obtido, economia_processual,
        data_distribuicao, data_encerramento)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
        (data.get('numero_processo'), data.get('vara'), data.get('judge_id'), data.get('cliente_id'),
         data.get('reclamante'), data.get('reclamada'), data.get('tese_inicial'), data.get('tese_defesa'),
         data.get('status', 'em_andamento'), data.get('resultado'), data.get('valor_pedido'),
         data.get('valor_obtido'), eco, data.get('data_distribuicao'), data.get('data_encerramento')))
    conn.commit()
    lid = c.lastrowid
    conn.close()
    return lid


def update_lawsuit(lawsuit_id: int, data: Dict):
    conn = get_connection()
    if 'valor_pedido' in data or 'valor_obtido' in data:
        existing = get_lawsuit_by_id(lawsuit_id)
        vp = data.get('valor_pedido', existing.get('valor_pedido', 0)) or 0
        vo = data.get('valor_obtido', existing.get('valor_obtido', 0)) or 0
        data['economia_processual'] = vp - vo
    fields = []
    values = []
    for k, v in data.items():
        if k not in ('id', 'created_at', 'judge_name', 'cliente_nome'):
            fields.append(f"{k}=?")
            values.append(v)
    fields.append("updated_at=datetime('now')")
    values.append(lawsuit_id)
    conn.execute(f"UPDATE lawsuits SET {', '.join(fields)} WHERE id=?", values)
    conn.commit()
    conn.close()


def delete_lawsuit(lawsuit_id: int):
    conn = get_connection()
    conn.execute("DELETE FROM settlements WHERE lawsuit_id=?", (lawsuit_id,))
    conn.execute("DELETE FROM generated_pieces WHERE lawsuit_id=?", (lawsuit_id,))
    conn.execute("DELETE FROM lawsuits WHERE id=?", (lawsuit_id,))
    conn.commit()
    conn.close()


def get_lawsuits_by_judge(judge_id: int) -> List[Dict]:
    conn = get_connection()
    rows = conn.execute("SELECT * FROM lawsuits WHERE judge_id=?", (judge_id,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_lawsuits_by_cliente(cliente_id: int) -> List[Dict]:
    conn = get_connection()
    rows = conn.execute("""SELECT l.*, j.name as judge_name FROM lawsuits l
        LEFT JOIN judges j ON l.judge_id = j.id
        WHERE l.cliente_id=? ORDER BY l.created_at DESC""", (cliente_id,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ==================== SETTLEMENTS ====================
def get_all_settlements() -> List[Dict]:
    conn = get_connection()
    rows = conn.execute("""SELECT s.*, l.numero_processo FROM settlements s
        LEFT JOIN lawsuits l ON s.lawsuit_id = l.id ORDER BY s.created_at DESC""").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def create_settlement(data: Dict) -> int:
    conn = get_connection()
    c = conn.execute("""INSERT INTO settlements (lawsuit_id, tipo, valor_pedido, valor_obtido,
        parcelas, condicao_parcelamento, clausulas_especiais, data_homologacao, dados_bancarios, observacoes)
        VALUES (?,?,?,?,?,?,?,?,?,?)""",
        (data.get('lawsuit_id'), data.get('tipo'), data.get('valor_pedido'), data.get('valor_obtido'),
         data.get('parcelas'), data.get('condicao_parcelamento'), data.get('clausulas_especiais'),
         data.get('data_homologacao'), data.get('dados_bancarios'), data.get('observacoes')))
    conn.commit()
    lid = c.lastrowid
    conn.close()
    return lid


def get_settlement_by_id(settlement_id: int) -> Optional[Dict]:
    conn = get_connection()
    row = conn.execute("SELECT * FROM settlements WHERE id=?", (settlement_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def update_settlement(settlement_id: int, data: Dict):
    conn = get_connection()
    fields = []
    values = []
    for k, v in data.items():
        if k not in ('id', 'created_at', 'numero_processo'):
            fields.append(f"{k}=?")
            values.append(v)
    fields.append("updated_at=datetime('now')")
    values.append(settlement_id)
    conn.execute(f"UPDATE settlements SET {', '.join(fields)} WHERE id=?", values)
    conn.commit()
    conn.close()


def delete_settlement(settlement_id: int):
    conn = get_connection()
    conn.execute("DELETE FROM settlements WHERE id=?", (settlement_id,))
    conn.commit()
    conn.close()


# ==================== LEGAL REFERENCES ====================
def get_all_legal_references(tipo: str = None, tema: str = None) -> List[Dict]:
    conn = get_connection()
    query = "SELECT * FROM legal_references WHERE 1=1"
    params = []
    if tipo:
        query += " AND tipo=?"
        params.append(tipo)
    if tema:
        query += " AND tema=?"
        params.append(tema)
    query += " ORDER BY tema, titulo"
    rows = conn.execute(query, params).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def create_legal_reference(data: Dict) -> int:
    conn = get_connection()
    c = conn.execute("""INSERT INTO legal_references (tipo, tema, titulo, autor, fonte, trecho, ano)
        VALUES (?,?,?,?,?,?,?)""",
        (data.get('tipo'), data.get('tema'), data.get('titulo'), data.get('autor'),
         data.get('fonte'), data.get('trecho'), data.get('ano')))
    conn.commit()
    lid = c.lastrowid
    conn.close()
    return lid


def update_legal_reference(ref_id: int, data: Dict):
    conn = get_connection()
    fields = []
    values = []
    for k, v in data.items():
        if k not in ('id', 'created_at'):
            fields.append(f"{k}=?")
            values.append(v)
    fields.append("updated_at=datetime('now')")
    values.append(ref_id)
    conn.execute(f"UPDATE legal_references SET {', '.join(fields)} WHERE id=?", values)
    conn.commit()
    conn.close()


def get_legal_reference_by_id(ref_id: int) -> Optional[Dict]:
    conn = get_connection()
    row = conn.execute("SELECT * FROM legal_references WHERE id=?", (ref_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def delete_legal_reference(ref_id: int):
    conn = get_connection()
    conn.execute("DELETE FROM legal_references WHERE id=?", (ref_id,))
    conn.commit()
    conn.close()


# ==================== NEGOTIATION PARAMS ====================
def get_all_negotiation_params() -> List[Dict]:
    conn = get_connection()
    rows = conn.execute("""SELECT n.*, j.name as judge_name FROM negotiation_params n
        LEFT JOIN judges j ON n.judge_id = j.id ORDER BY n.tema_processual""").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def create_negotiation_param(data: Dict) -> int:
    conn = get_connection()
    c = conn.execute("""INSERT INTO negotiation_params (judge_id, tema_processual, valor_inicial_sugerido,
        faixa_fechamento_min, faixa_fechamento_max, estrategia_recomendada, observacoes)
        VALUES (?,?,?,?,?,?,?)""",
        (data.get('judge_id'), data.get('tema_processual'), data.get('valor_inicial_sugerido'),
         data.get('faixa_fechamento_min'), data.get('faixa_fechamento_max'),
         data.get('estrategia_recomendada'), data.get('observacoes')))
    conn.commit()
    lid = c.lastrowid
    conn.close()
    return lid


def delete_negotiation_param(param_id: int):
    conn = get_connection()
    conn.execute("DELETE FROM negotiation_params WHERE id=?", (param_id,))
    conn.commit()
    conn.close()


# ==================== GENERATED PIECES ====================
def save_generated_piece(lawsuit_id: int, tipo: str, conteudo: str, gerado_por: str = "template") -> int:
    conn = get_connection()
    c = conn.execute("INSERT INTO generated_pieces (lawsuit_id, tipo_peca, conteudo, gerado_por) VALUES (?,?,?,?)",
                     (lawsuit_id, tipo, conteudo, gerado_por))
    conn.commit()
    lid = c.lastrowid
    conn.close()
    return lid

def get_generated_pieces(lawsuit_id: int = None) -> List[Dict]:
    conn = get_connection()
    if lawsuit_id:
        rows = conn.execute("SELECT * FROM generated_pieces WHERE lawsuit_id=? ORDER BY created_at DESC",
                            (lawsuit_id,)).fetchall()
    else:
        rows = conn.execute("SELECT * FROM generated_pieces ORDER BY created_at DESC").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def delete_generated_piece(piece_id: int):
    conn = get_connection()
    conn.execute("DELETE FROM generated_pieces WHERE id=?", (piece_id,))
    conn.commit()
    conn.close()
