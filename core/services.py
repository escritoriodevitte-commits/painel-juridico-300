"""
Core Services - Serviços de negócio do Painel Estratégico Jurídico
"""
from core.database import get_connection, get_all_lawsuits, get_lawsuit_by_id, get_all_clientes


class ClienteService:
    @staticmethod
    def criar_cliente(nome, cpf, telefone, email, endereco="", observacoes=""):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO clientes (nome, cpf, telefone, email, endereco, observacoes) VALUES (?, ?, ?, ?, ?, ?)",
                       (nome, cpf, telefone, email, endereco, observacoes))
        conn.commit()
        lid = cursor.lastrowid
        conn.close()
        return lid

    @staticmethod
    def buscar_por_cpf(cpf):
        conn = get_connection()
        row = conn.execute("SELECT * FROM clientes WHERE cpf=?", (cpf,)).fetchone()
        conn.close()
        return dict(row) if row else None

    @staticmethod
    def listar_processos_cliente(cliente_id):
        conn = get_connection()
        rows = conn.execute("""SELECT l.*, j.name as judge_name FROM lawsuits l
            LEFT JOIN judges j ON l.judge_id = j.id
            WHERE l.cliente_id=? ORDER BY l.created_at DESC""", (cliente_id,)).fetchall()
        conn.close()
        return [dict(r) for r in rows]

    @staticmethod
    def resumo_cliente(cliente_id):
        processos = ClienteService.listar_processos_cliente(cliente_id)
        total = len(processos)
        em_andamento = len([p for p in processos if p['status'] == 'em_andamento'])
        encerrados = total - em_andamento
        valor_total_pedido = sum(p.get('valor_pedido', 0) or 0 for p in processos)
        valor_total_obtido = sum(p.get('valor_obtido', 0) or 0 for p in processos)
        economia = sum(p.get('economia_processual', 0) or 0 for p in processos)
        return {
            'total_processos': total,
            'em_andamento': em_andamento,
            'encerrados': encerrados,
            'valor_total_pedido': round(valor_total_pedido, 2),
            'valor_total_obtido': round(valor_total_obtido, 2),
            'economia_total': round(economia, 2),
        }


class ProcessoService:
    @staticmethod
    def vincular_cliente(lawsuit_id, cliente_id):
        conn = get_connection()
        conn.execute("UPDATE lawsuits SET cliente_id=?, updated_at=datetime('now') WHERE id=?",
                     (cliente_id, lawsuit_id))
        conn.commit()
        conn.close()

    @staticmethod
    def estatisticas_gerais():
        lawsuits = get_all_lawsuits()
        total = len(lawsuits)
        em_andamento = len([l for l in lawsuits if l['status'] == 'em_andamento'])
        encerrados = total - em_andamento
        total_pedido = sum(l.get('valor_pedido', 0) or 0 for l in lawsuits)
        total_obtido = sum(l.get('valor_obtido', 0) or 0 for l in lawsuits)
        economia = sum(l.get('economia_processual', 0) or 0 for l in lawsuits)
        return {
            'total': total, 'em_andamento': em_andamento, 'encerrados': encerrados,
            'total_pedido': round(total_pedido, 2), 'total_obtido': round(total_obtido, 2),
            'economia': round(economia, 2),
        }

    @staticmethod
    def buscar_por_numero(numero):
        conn = get_connection()
        row = conn.execute("""SELECT l.*, j.name as judge_name FROM lawsuits l
            LEFT JOIN judges j ON l.judge_id = j.id
            WHERE l.numero_processo LIKE ?""", (f"%{numero}%",)).fetchone()
        conn.close()
        return dict(row) if row else None
