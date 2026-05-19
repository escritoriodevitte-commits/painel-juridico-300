"""
Painel Estratégico Jurídico v2 - Software Desktop
Interface gráfica completa com CustomTkinter
Todas as telas possuem abas de edição manual
"""
import customtkinter as ctk
from tkinter import messagebox, filedialog, ttk
import os
import sys

# Adicionar diretório raiz ao path
sys.path.insert(0, os.path.dirname(__file__))

from core import database as db
from modules.calculadora.calc import calcular_verbas as _calcular_verbas
from modules.analytics.engine import AnalyticsEngine
from modules.ia.gerador import GeradorPecas, TIPOS_PECA
from modules.exports.pdf import PDFExporter
from modules.exports.csv_export import CSVExporter
from modules.api_bridge import LegalAIClient
from seed import run_seed

# ==================== CORES ====================
COLORS = {
    'bg_dark': '#0f172a', 'bg_card': '#1e293b', 'bg_input': '#334155',
    'accent': '#3b82f6', 'accent_hover': '#2563eb', 'success': '#22c55e',
    'warning': '#f59e0b', 'danger': '#ef4444', 'text': '#f8fafc',
    'text_secondary': '#94a3b8', 'gold': '#fbbf24', 'cliente': '#8b5cf6',
    'border': '#475569',
}

def formatar_moeda(valor):
    try:
        return f"R$ {float(valor):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except:
        return "R$ 0,00"


class PainelJuridico(ctk.CTk):
    def __init__(self):
        super().__init__()
        ctk.set_appearance_mode("dark")
        self.title("Painel Estratégico Jurídico v2")
        self.geometry("1400x850")
        self.minsize(1200, 700)

        db.init_db()
        run_seed()

        self.gerador = GeradorPecas()
        self.analytics = AnalyticsEngine()
        # calculadora usa função direta, não classe

        self.current_page = "dashboard"
        self._build_layout()
        self.show_page("dashboard")

    def _build_layout(self):
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self._build_sidebar()
        self.content_frame = ctk.CTkScrollableFrame(self, fg_color=COLORS['bg_dark'])
        self.content_frame.grid(row=0, column=1, sticky="nsew")

    def _build_sidebar(self):
        sidebar = ctk.CTkFrame(self, width=220, fg_color="#0c1222", corner_radius=0)
        sidebar.grid(row=0, column=0, sticky="nsew")
        sidebar.grid_propagate(False)

        ctk.CTkLabel(sidebar, text="PAINEL JURÍDICO", font=("Arial", 16, "bold"),
                     text_color=COLORS['gold']).pack(pady=(20, 5))
        ctk.CTkLabel(sidebar, text="Estratégia Trabalhista", font=("Arial", 10),
                     text_color=COLORS['text_secondary']).pack(pady=(0, 20))

        sections = [
            ("GESTÃO", [
                ("dashboard", "Dashboard"),
                ("processos", "Processos"),
                ("clientes", "Clientes"),
                ("magistrados", "Magistrados"),
                ("acordos", "Acordos"),
                ("biblioteca", "Biblioteca"),
                ("calculadora", "Calculadora"),
            ]),
            ("INTELIGÊNCIA", [
                ("previsao", "Previsão"),
                ("motor_teses", "Motor Teses"),
                ("radar_risco", "Radar Risco"),
                ("competitiva", "Competitiva"),
                ("gerar_pecas", "Gerar Peças"),
            ]),
            ("CONFIGURAÇÕES", [
                ("api_config", "API OpenAI"),
                ("integracao_legal_ai", "Integração Legal AI"),
            ]),
        ]

        for section_name, items in sections:
            ctk.CTkLabel(sidebar, text=section_name, font=("Arial", 9, "bold"),
                         text_color=COLORS['text_secondary']).pack(anchor="w", padx=15, pady=(15, 5))
            for page_id, label in items:
                btn = ctk.CTkButton(sidebar, text=f"  {label}", font=("Arial", 12),
                                    fg_color="transparent", hover_color=COLORS['bg_input'],
                                    anchor="w", height=32,
                                    command=lambda p=page_id: self.show_page(p))
                btn.pack(fill="x", padx=10, pady=1)

    def show_page(self, page):
        self.current_page = page
        for w in self.content_frame.winfo_children():
            w.destroy()
        builder = getattr(self, f"build_{page}", None)
        if builder:
            builder(self.content_frame)

    def create_section_title(self, parent, title, subtitle=""):
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill="x", padx=20, pady=(15, 5))
        ctk.CTkLabel(frame, text=title, font=("Arial", 22, "bold"), text_color=COLORS['text']).pack(anchor="w")
        if subtitle:
            ctk.CTkLabel(frame, text=subtitle, font=("Arial", 12), text_color=COLORS['text_secondary']).pack(anchor="w")

    def create_stat_card(self, parent, label, value, color=None):
        card = ctk.CTkFrame(parent, fg_color=COLORS['bg_card'], corner_radius=12, height=90)
        card.pack_propagate(False)
        ctk.CTkLabel(card, text=label, font=("Arial", 10), text_color=COLORS['text_secondary']).pack(anchor="w", padx=15, pady=(12, 2))
        ctk.CTkLabel(card, text=str(value), font=("Arial", 20, "bold"),
                     text_color=color or COLORS['accent']).pack(anchor="w", padx=15)
        return card

    def create_table(self, parent, columns, data):
        frame = ctk.CTkFrame(parent, fg_color=COLORS['bg_card'], corner_radius=10)
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Dark.Treeview", background="#1e293b", foreground="#f8fafc",
                        fieldbackground="#1e293b", borderwidth=0, font=("Arial", 10))
        style.configure("Dark.Treeview.Heading", background="#334155", foreground="#f8fafc",
                        font=("Arial", 10, "bold"))
        style.map("Dark.Treeview", background=[("selected", "#3b82f6")])

        cols = [c[0] for c in columns]
        tree = ttk.Treeview(frame, columns=cols, show="headings", style="Dark.Treeview", height=min(len(data), 12))
        for col_id, col_label, col_width in columns:
            tree.heading(col_id, text=col_label)
            tree.column(col_id, width=col_width, minwidth=50)
        for row in data:
            tree.insert("", "end", values=row)

        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        tree.pack(side="left", fill="both", expand=True, padx=(10, 0), pady=10)
        scrollbar.pack(side="right", fill="y", pady=10, padx=(0, 10))
        return frame, tree

    # ==================== DASHBOARD ====================
    def build_dashboard(self, parent):
        self.create_section_title(parent, "Dashboard", "Visão geral estratégica")
        lawsuits = db.get_all_lawsuits()
        total = len(lawsuits)
        acordos = len([l for l in lawsuits if l['status'] == 'acordo'])
        improcedentes = len([l for l in lawsuits if l['status'] == 'sentenca_improcedente'])
        andamento = len([l for l in lawsuits if l['status'] == 'em_andamento'])
        economia = sum(l.get('economia_processual', 0) or 0 for l in lawsuits)
        clientes = len(db.get_all_clientes())
        refs = len(db.get_all_legal_references())

        cards_frame = ctk.CTkFrame(parent, fg_color="transparent")
        cards_frame.pack(fill="x", padx=20, pady=10)
        for i, (lbl, val, clr) in enumerate([
            ("Processos", total, COLORS['accent']),
            ("Acordos", f"{acordos} ({(acordos/total*100):.0f}%)" if total else "0", COLORS['success']),
            ("Improcedentes", f"{improcedentes} ({(improcedentes/total*100):.0f}%)" if total else "0", COLORS['warning']),
            ("Em Andamento", andamento, COLORS['danger']),
            ("Economia", formatar_moeda(economia), COLORS['gold']),
            ("Clientes", clientes, COLORS['cliente']),
            ("Referências", refs, COLORS['text']),
        ]):
            card = self.create_stat_card(cards_frame, lbl, val, clr)
            card.grid(row=i // 4, column=i % 4, padx=5, pady=5, sticky="ew")
        for c in range(4):
            cards_frame.grid_columnconfigure(c, weight=1)

        # Últimos processos
        self.create_section_title(parent, "Últimos Processos")
        cols = [("num", "Número", 170), ("vara", "Vara", 150), ("status", "Status", 120),
                ("valor", "Valor Pedido", 120), ("eco", "Economia", 120)]
        data = [(l['numero_processo'], l['vara'], l['status'],
                 formatar_moeda(l.get('valor_pedido', 0) or 0),
                 formatar_moeda(l.get('economia_processual', 0) or 0)) for l in lawsuits[:10]]
        tf, _ = self.create_table(parent, cols, data)
        tf.pack(fill="x", padx=20, pady=10)

    # ==================== PROCESSOS ====================
    def build_processos(self, parent):
        self.create_section_title(parent, "Processos", "Gestão de processos trabalhistas")

        # Tabview com abas
        tabview = ctk.CTkTabview(parent, fg_color=COLORS['bg_dark'])
        tabview.pack(fill="both", expand=True, padx=20, pady=10)
        tab_lista = tabview.add("Lista de Processos")
        tab_novo = tabview.add("Novo Processo")
        tab_editar = tabview.add("Editar Processo")

        # === ABA LISTA ===
        lawsuits = db.get_all_lawsuits()
        cols = [("id", "ID", 40), ("num", "Número", 170), ("vara", "Vara", 150),
                ("reclamante", "Reclamante", 150), ("reclamada", "Reclamada", 150),
                ("status", "Status", 100), ("valor", "Valor Pedido", 100)]
        data = [(l['id'], l['numero_processo'], l['vara'], l['reclamante'],
                 l['reclamada'], l['status'], formatar_moeda(l.get('valor_pedido', 0) or 0)) for l in lawsuits]
        tf, tree_proc = self.create_table(tab_lista, cols, data)
        tf.pack(fill="both", expand=True, padx=5, pady=5)

        btn_frame = ctk.CTkFrame(tab_lista, fg_color="transparent")
        btn_frame.pack(fill="x", padx=5, pady=5)
        ctk.CTkButton(btn_frame, text="Excluir Selecionado", fg_color=COLORS['danger'],
                      command=lambda: self._delete_selected(tree_proc, "processo")).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="Exportar CSV", fg_color=COLORS['accent'],
                      command=lambda: self._export_csv("processos")).pack(side="left", padx=5)

        # === ABA NOVO ===
        self._build_processo_form(tab_novo, mode="create")

        # === ABA EDITAR ===
        ctk.CTkLabel(tab_editar, text="Selecione um processo na aba 'Lista' e clique aqui para editar",
                     font=("Arial", 12), text_color=COLORS['text_secondary']).pack(pady=10)
        edit_id_var = ctk.StringVar()
        id_frame = ctk.CTkFrame(tab_editar, fg_color="transparent")
        id_frame.pack(fill="x", padx=10, pady=5)
        ctk.CTkLabel(id_frame, text="ID do Processo:").pack(side="left", padx=5)
        ctk.CTkEntry(id_frame, textvariable=edit_id_var, width=80, fg_color=COLORS['bg_input']).pack(side="left", padx=5)
        edit_container = ctk.CTkFrame(tab_editar, fg_color="transparent")
        edit_container.pack(fill="both", expand=True)

        def load_for_edit():
            pid = edit_id_var.get().strip()
            if not pid or not pid.isdigit():
                messagebox.showwarning("Aviso", "Informe um ID válido")
                return
            proc = db.get_lawsuit_by_id(int(pid))
            if not proc:
                messagebox.showwarning("Aviso", "Processo não encontrado")
                return
            for w in edit_container.winfo_children():
                w.destroy()
            self._build_processo_form(edit_container, mode="edit", data=proc)

        ctk.CTkButton(id_frame, text="Carregar", fg_color=COLORS['accent'], command=load_for_edit).pack(side="left", padx=5)

        def on_select(event):
            sel = tree_proc.selection()
            if sel:
                edit_id_var.set(str(tree_proc.item(sel[0])['values'][0]))

        tree_proc.bind("<<TreeviewSelect>>", on_select)

    def _build_processo_form(self, parent, mode="create", data=None):
        scroll = ctk.CTkScrollableFrame(parent, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=5, pady=5)

        fields = {}
        judges = db.get_all_judges()
        clientes = db.get_all_clientes()

        row_frame = ctk.CTkFrame(scroll, fg_color="transparent")
        row_frame.pack(fill="x", pady=5)
        left = ctk.CTkFrame(row_frame, fg_color="transparent")
        left.pack(side="left", fill="both", expand=True, padx=5)
        right = ctk.CTkFrame(row_frame, fg_color="transparent")
        right.pack(side="left", fill="both", expand=True, padx=5)

        for key, label, col in [
            ("numero_processo", "Número do Processo *", left),
            ("vara", "Vara *", left),
            ("reclamante", "Reclamante *", left),
            ("reclamada", "Reclamada *", left),
            ("data_distribuicao", "Data Distribuição", left),
            ("data_encerramento", "Data Encerramento", right),
            ("valor_pedido", "Valor Pedido (R$)", right),
            ("valor_obtido", "Valor Obtido (R$)", right),
        ]:
            ctk.CTkLabel(col, text=label, font=("Arial", 11)).pack(anchor="w", padx=5, pady=(5, 1))
            entry = ctk.CTkEntry(col, fg_color=COLORS['bg_input'], height=32)
            entry.pack(fill="x", padx=5)
            if data and data.get(key):
                entry.insert(0, str(data[key]))
            fields[key] = entry

        # Status
        ctk.CTkLabel(right, text="Status", font=("Arial", 11)).pack(anchor="w", padx=5, pady=(5, 1))
        status_var = ctk.StringVar(value=data.get('status', 'em_andamento') if data else 'em_andamento')
        ctk.CTkOptionMenu(right, variable=status_var, fg_color=COLORS['bg_input'],
                          values=['em_andamento', 'acordo', 'sentenca_procedente', 'sentenca_improcedente',
                                  'sentenca_parcial', 'arquivado']).pack(fill="x", padx=5)

        # Juiz
        ctk.CTkLabel(right, text="Magistrado", font=("Arial", 11)).pack(anchor="w", padx=5, pady=(5, 1))
        judge_names = ["(Nenhum)"] + [f"{j['id']} - {j['name']}" for j in judges]
        judge_var = ctk.StringVar(value="(Nenhum)")
        if data and data.get('judge_id'):
            for j in judges:
                if j['id'] == data['judge_id']:
                    judge_var.set(f"{j['id']} - {j['name']}")
        ctk.CTkOptionMenu(right, variable=judge_var, fg_color=COLORS['bg_input'], values=judge_names).pack(fill="x", padx=5)

        # Cliente
        ctk.CTkLabel(right, text="Cliente", font=("Arial", 11)).pack(anchor="w", padx=5, pady=(5, 1))
        cliente_names = ["(Nenhum)"] + [f"{c['id']} - {c['nome']}" for c in clientes]
        cliente_var = ctk.StringVar(value="(Nenhum)")
        if data and data.get('cliente_id'):
            for c in clientes:
                if c['id'] == data['cliente_id']:
                    cliente_var.set(f"{c['id']} - {c['nome']}")
        ctk.CTkOptionMenu(right, variable=cliente_var, fg_color=COLORS['bg_input'], values=cliente_names).pack(fill="x", padx=5)

        # Teses
        for key, label in [("tese_inicial", "Tese do Reclamante"), ("tese_defesa", "Tese da Defesa"), ("resultado", "Resultado")]:
            ctk.CTkLabel(scroll, text=label, font=("Arial", 11)).pack(anchor="w", padx=10, pady=(5, 1))
            tb = ctk.CTkTextbox(scroll, fg_color=COLORS['bg_input'], height=60)
            tb.pack(fill="x", padx=10)
            if data and data.get(key):
                tb.insert("1.0", str(data[key]))
            fields[key] = tb

        def save():
            d = {}
            for k, widget in fields.items():
                if isinstance(widget, ctk.CTkTextbox):
                    d[k] = widget.get("1.0", "end").strip()
                else:
                    d[k] = widget.get().strip()
            if not d.get('numero_processo') or not d.get('vara') or not d.get('reclamante') or not d.get('reclamada'):
                messagebox.showwarning("Aviso", "Campos obrigatórios: Número, Vara, Reclamante, Reclamada")
                return
            d['status'] = status_var.get()
            jv = judge_var.get()
            d['judge_id'] = int(jv.split(" - ")[0]) if jv != "(Nenhum)" else None
            cv = cliente_var.get()
            d['cliente_id'] = int(cv.split(" - ")[0]) if cv != "(Nenhum)" else None
            for f in ['valor_pedido', 'valor_obtido']:
                try:
                    d[f] = float(d[f].replace(",", ".")) if d.get(f) else None
                except:
                    d[f] = None

            if mode == "create":
                db.create_lawsuit(d)
                messagebox.showinfo("Sucesso", "Processo cadastrado!")
            else:
                db.update_lawsuit(data['id'], d)
                messagebox.showinfo("Sucesso", "Processo atualizado!")
            self.show_page("processos")

        ctk.CTkButton(scroll, text="Salvar" if mode == "create" else "Atualizar",
                      fg_color=COLORS['accent'], height=40, command=save).pack(fill="x", padx=10, pady=15)

    # ==================== CLIENTES ====================
    def build_clientes(self, parent):
        self.create_section_title(parent, "Clientes", "Gestão de clientes do escritório")

        tabview = ctk.CTkTabview(parent, fg_color=COLORS['bg_dark'])
        tabview.pack(fill="both", expand=True, padx=20, pady=10)
        tab_lista = tabview.add("Lista de Clientes")
        tab_novo = tabview.add("Novo Cliente")
        tab_editar = tabview.add("Editar Cliente")

        # === ABA LISTA ===
        clientes = db.get_all_clientes()
        cols = [("id", "ID", 40), ("nome", "Nome", 200), ("cpf", "CPF", 120),
                ("telefone", "Telefone", 120), ("email", "Email", 200)]
        data_list = [(c['id'], c['nome'], c.get('cpf', '-'), c.get('telefone', '-'),
                      c.get('email', '-')) for c in clientes]
        tf, tree_cli = self.create_table(tab_lista, cols, data_list)
        tf.pack(fill="both", expand=True, padx=5, pady=5)

        btn_frame = ctk.CTkFrame(tab_lista, fg_color="transparent")
        btn_frame.pack(fill="x", padx=5, pady=5)
        ctk.CTkButton(btn_frame, text="Excluir Selecionado", fg_color=COLORS['danger'],
                      command=lambda: self._delete_selected(tree_cli, "cliente")).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="Exportar CSV", fg_color=COLORS['accent'],
                      command=lambda: self._export_csv("clientes")).pack(side="left", padx=5)

        # === ABA NOVO ===
        self._build_cliente_form(tab_novo, mode="create")

        # === ABA EDITAR ===
        edit_id_var = ctk.StringVar()
        id_frame = ctk.CTkFrame(tab_editar, fg_color="transparent")
        id_frame.pack(fill="x", padx=10, pady=5)
        ctk.CTkLabel(id_frame, text="ID do Cliente:").pack(side="left", padx=5)
        ctk.CTkEntry(id_frame, textvariable=edit_id_var, width=80, fg_color=COLORS['bg_input']).pack(side="left", padx=5)
        edit_container = ctk.CTkFrame(tab_editar, fg_color="transparent")
        edit_container.pack(fill="both", expand=True)

        def load_for_edit():
            cid = edit_id_var.get().strip()
            if not cid or not cid.isdigit():
                messagebox.showwarning("Aviso", "Informe um ID válido")
                return
            cli = db.get_cliente_by_id(int(cid))
            if not cli:
                messagebox.showwarning("Aviso", "Cliente não encontrado")
                return
            for w in edit_container.winfo_children():
                w.destroy()
            self._build_cliente_form(edit_container, mode="edit", data=cli)

        ctk.CTkButton(id_frame, text="Carregar", fg_color=COLORS['accent'], command=load_for_edit).pack(side="left", padx=5)

        def on_select(event):
            sel = tree_cli.selection()
            if sel:
                edit_id_var.set(str(tree_cli.item(sel[0])['values'][0]))

        tree_cli.bind("<<TreeviewSelect>>", on_select)

    def _build_cliente_form(self, parent, mode="create", data=None):
        fields = {}
        for key, label in [("nome", "Nome *"), ("cpf", "CPF"), ("telefone", "Telefone"),
                           ("email", "Email"), ("endereco", "Endereço"), ("observacoes", "Observações")]:
            ctk.CTkLabel(parent, text=label, font=("Arial", 11)).pack(anchor="w", padx=10, pady=(5, 1))
            entry = ctk.CTkEntry(parent, fg_color=COLORS['bg_input'], height=32)
            entry.pack(fill="x", padx=10)
            if data and data.get(key):
                entry.insert(0, str(data[key]))
            fields[key] = entry

        def save():
            d = {k: e.get().strip() for k, e in fields.items()}
            if not d.get('nome'):
                messagebox.showwarning("Aviso", "Nome é obrigatório")
                return
            if mode == "create":
                db.create_cliente(d)
                messagebox.showinfo("Sucesso", "Cliente cadastrado!")
            else:
                db.update_cliente(data['id'], d)
                messagebox.showinfo("Sucesso", "Cliente atualizado!")
            self.show_page("clientes")

        ctk.CTkButton(parent, text="Salvar" if mode == "create" else "Atualizar",
                      fg_color=COLORS['accent'], height=40, command=save).pack(fill="x", padx=10, pady=15)

    # ==================== MAGISTRADOS ====================
    def build_magistrados(self, parent):
        self.create_section_title(parent, "Magistrados", "Perfil e tendências dos juízes")

        tabview = ctk.CTkTabview(parent, fg_color=COLORS['bg_dark'])
        tabview.pack(fill="both", expand=True, padx=20, pady=10)
        tab_lista = tabview.add("Lista")
        tab_novo = tabview.add("Novo Magistrado")
        tab_editar = tabview.add("Editar Magistrado")

        judges = db.get_all_judges()
        cols = [("id", "ID", 40), ("nome", "Nome", 200), ("vara", "Vara", 200),
                ("tendencia", "Tendência", 120)]
        data_list = [(j['id'], j['name'], j['vara'], j.get('tendencia_conciliatoria', '-')) for j in judges]
        tf, tree_j = self.create_table(tab_lista, cols, data_list)
        tf.pack(fill="both", expand=True, padx=5, pady=5)

        # Detalhes do magistrado
        detail_frame = ctk.CTkFrame(tab_lista, fg_color=COLORS['bg_card'], corner_radius=12)
        detail_frame.pack(fill="x", padx=5, pady=5)
        ctk.CTkLabel(detail_frame, text="Selecione um magistrado para ver o perfil",
                     font=("Arial", 12), text_color=COLORS['text_secondary']).pack(padx=20, pady=15)

        def on_select_judge(event):
            sel = tree_j.selection()
            if not sel:
                return
            jid = tree_j.item(sel[0])['values'][0]
            judge = db.get_judge_by_id(jid)
            if not judge:
                return
            for w in detail_frame.winfo_children():
                w.destroy()
            ctk.CTkLabel(detail_frame, text=f"Juiz(a): {judge['name']}",
                         font=("Arial", 16, "bold")).pack(anchor="w", padx=20, pady=(10, 3))
            ctk.CTkLabel(detail_frame, text=f"Vara: {judge['vara']}",
                         font=("Arial", 12), text_color=COLORS['text_secondary']).pack(anchor="w", padx=20)
            for label, campo in [("Tendência Conciliatória", "tendencia_conciliatoria"),
                                 ("Justa Causa", "postura_justa_causa"), ("Acidente", "postura_acidente"),
                                 ("Danos Morais", "postura_danos_morais"), ("Horas Extras", "postura_horas_extras"),
                                 ("Rescisão Indireta", "postura_rescisao_indireta")]:
                val = judge.get(campo)
                if val:
                    ctk.CTkLabel(detail_frame, text=f"  {label}: {val}", font=("Arial", 11),
                                 text_color=COLORS['text_secondary']).pack(anchor="w", padx=20, pady=1)
            if judge.get('observacoes'):
                ctk.CTkLabel(detail_frame, text=f"  Obs: {judge['observacoes']}", font=("Arial", 10),
                             text_color=COLORS['text_secondary']).pack(anchor="w", padx=20, pady=(3, 10))

        tree_j.bind("<<TreeviewSelect>>", on_select_judge)

        btn_frame = ctk.CTkFrame(tab_lista, fg_color="transparent")
        btn_frame.pack(fill="x", padx=5, pady=5)
        ctk.CTkButton(btn_frame, text="Excluir Selecionado", fg_color=COLORS['danger'],
                      command=lambda: self._delete_selected(tree_j, "magistrado")).pack(side="left", padx=5)

        # === ABA NOVO ===
        self._build_magistrado_form(tab_novo, mode="create")

        # === ABA EDITAR ===
        edit_id_var = ctk.StringVar()
        id_frame = ctk.CTkFrame(tab_editar, fg_color="transparent")
        id_frame.pack(fill="x", padx=10, pady=5)
        ctk.CTkLabel(id_frame, text="ID:").pack(side="left", padx=5)
        ctk.CTkEntry(id_frame, textvariable=edit_id_var, width=80, fg_color=COLORS['bg_input']).pack(side="left", padx=5)
        edit_container = ctk.CTkFrame(tab_editar, fg_color="transparent")
        edit_container.pack(fill="both", expand=True)

        def load_for_edit():
            jid = edit_id_var.get().strip()
            if not jid or not jid.isdigit():
                return
            judge = db.get_judge_by_id(int(jid))
            if not judge:
                messagebox.showwarning("Aviso", "Magistrado não encontrado")
                return
            for w in edit_container.winfo_children():
                w.destroy()
            self._build_magistrado_form(edit_container, mode="edit", data=judge)

        ctk.CTkButton(id_frame, text="Carregar", fg_color=COLORS['accent'], command=load_for_edit).pack(side="left", padx=5)

        def on_sel_edit(event):
            sel = tree_j.selection()
            if sel:
                edit_id_var.set(str(tree_j.item(sel[0])['values'][0]))

        tree_j.bind("<<TreeviewSelect>>", on_sel_edit)

    def _build_magistrado_form(self, parent, mode="create", data=None):
        scroll = ctk.CTkScrollableFrame(parent, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=5, pady=5)
        fields = {}
        for key, label in [("name", "Nome *"), ("vara", "Vara *"), ("comarca", "Comarca"),
                           ("postura_justa_causa", "Postura Justa Causa"),
                           ("postura_acidente", "Postura Acidente de Trabalho"),
                           ("postura_danos_morais", "Postura Danos Morais"),
                           ("postura_horas_extras", "Postura Horas Extras"),
                           ("postura_rescisao_indireta", "Postura Rescisão Indireta"),
                           ("observacoes", "Observações")]:
            ctk.CTkLabel(scroll, text=label, font=("Arial", 11)).pack(anchor="w", padx=10, pady=(5, 1))
            entry = ctk.CTkEntry(scroll, fg_color=COLORS['bg_input'], height=32)
            entry.pack(fill="x", padx=10)
            if data and data.get(key):
                entry.insert(0, str(data[key]))
            fields[key] = entry

        ctk.CTkLabel(scroll, text="Tendência Conciliatória", font=("Arial", 11)).pack(anchor="w", padx=10, pady=(5, 1))
        tend_var = ctk.StringVar(value=data.get('tendencia_conciliatoria', 'media') if data else 'media')
        ctk.CTkOptionMenu(scroll, variable=tend_var, fg_color=COLORS['bg_input'],
                          values=['alta', 'media', 'baixa']).pack(fill="x", padx=10)

        def save():
            d = {k: e.get().strip() for k, e in fields.items()}
            d['tendencia_conciliatoria'] = tend_var.get()
            if not d.get('name') or not d.get('vara'):
                messagebox.showwarning("Aviso", "Nome e Vara são obrigatórios")
                return
            if mode == "create":
                db.create_judge(d)
                messagebox.showinfo("Sucesso", "Magistrado cadastrado!")
            else:
                db.update_judge(data['id'], d)
                messagebox.showinfo("Sucesso", "Magistrado atualizado!")
            self.show_page("magistrados")

        ctk.CTkButton(scroll, text="Salvar" if mode == "create" else "Atualizar",
                      fg_color=COLORS['accent'], height=40, command=save).pack(fill="x", padx=10, pady=15)

    # ==================== ACORDOS ====================
    def build_acordos(self, parent):
        self.create_section_title(parent, "Acordos e Sentenças", "Registro de resultados processuais")

        tabview = ctk.CTkTabview(parent, fg_color=COLORS['bg_dark'])
        tabview.pack(fill="both", expand=True, padx=20, pady=10)
        tab_lista = tabview.add("Lista")
        tab_novo = tabview.add("Novo Acordo/Sentença")
        tab_editar = tabview.add("Editar")

        settlements = db.get_all_settlements()
        cols = [("id", "ID", 40), ("processo", "Processo", 170), ("tipo", "Tipo", 100),
                ("valor_p", "Valor Pedido", 110), ("valor_o", "Valor Obtido", 110),
                ("data", "Data", 100), ("obs", "Observações", 200)]
        data_list = [(s['id'], s.get('numero_processo', '-'), s.get('tipo', '-'),
                      formatar_moeda(s.get('valor_pedido', 0) or 0),
                      formatar_moeda(s.get('valor_obtido', 0) or 0),
                      s.get('data_homologacao', '-'), (s.get('observacoes', '') or '')[:50]) for s in settlements]
        tf, tree_s = self.create_table(tab_lista, cols, data_list)
        tf.pack(fill="both", expand=True, padx=5, pady=5)

        btn_frame = ctk.CTkFrame(tab_lista, fg_color="transparent")
        btn_frame.pack(fill="x", padx=5, pady=5)
        ctk.CTkButton(btn_frame, text="Excluir Selecionado", fg_color=COLORS['danger'],
                      command=lambda: self._delete_selected(tree_s, "acordo")).pack(side="left", padx=5)

        # === ABA NOVO ===
        self._build_acordo_form(tab_novo, mode="create")

        # === ABA EDITAR ===
        edit_id_var = ctk.StringVar()
        id_frame = ctk.CTkFrame(tab_editar, fg_color="transparent")
        id_frame.pack(fill="x", padx=10, pady=5)
        ctk.CTkLabel(id_frame, text="ID:").pack(side="left", padx=5)
        ctk.CTkEntry(id_frame, textvariable=edit_id_var, width=80, fg_color=COLORS['bg_input']).pack(side="left", padx=5)
        edit_container = ctk.CTkFrame(tab_editar, fg_color="transparent")
        edit_container.pack(fill="both", expand=True)

        def load_for_edit():
            sid = edit_id_var.get().strip()
            if not sid or not sid.isdigit():
                return
            sett = db.get_settlement_by_id(int(sid))
            if not sett:
                messagebox.showwarning("Aviso", "Acordo não encontrado")
                return
            for w in edit_container.winfo_children():
                w.destroy()
            self._build_acordo_form(edit_container, mode="edit", data=sett)

        ctk.CTkButton(id_frame, text="Carregar", fg_color=COLORS['accent'], command=load_for_edit).pack(side="left", padx=5)

        def on_sel(event):
            sel = tree_s.selection()
            if sel:
                edit_id_var.set(str(tree_s.item(sel[0])['values'][0]))

        tree_s.bind("<<TreeviewSelect>>", on_sel)

    def _build_acordo_form(self, parent, mode="create", data=None):
        lawsuits = db.get_all_lawsuits()
        fields = {}

        ctk.CTkLabel(parent, text="Processo *", font=("Arial", 11)).pack(anchor="w", padx=10, pady=(5, 1))
        proc_names = [f"{l['id']} - {l['numero_processo']}" for l in lawsuits]
        proc_var = ctk.StringVar(value=proc_names[0] if proc_names else "")
        if data and data.get('lawsuit_id'):
            for l in lawsuits:
                if l['id'] == data['lawsuit_id']:
                    proc_var.set(f"{l['id']} - {l['numero_processo']}")
        ctk.CTkOptionMenu(parent, variable=proc_var, fg_color=COLORS['bg_input'],
                          values=proc_names if proc_names else ["Nenhum processo"]).pack(fill="x", padx=10)

        ctk.CTkLabel(parent, text="Tipo *", font=("Arial", 11)).pack(anchor="w", padx=10, pady=(5, 1))
        tipo_var = ctk.StringVar(value=data.get('tipo', 'acordo') if data else 'acordo')
        ctk.CTkOptionMenu(parent, variable=tipo_var, fg_color=COLORS['bg_input'],
                          values=['acordo', 'sentenca']).pack(fill="x", padx=10)

        for key, label in [("valor_pedido", "Valor Pedido (R$)"), ("valor_obtido", "Valor Obtido (R$)"),
                           ("parcelas", "Parcelas"), ("data_homologacao", "Data Homologação"),
                           ("condicao_parcelamento", "Condição Parcelamento"),
                           ("clausulas_especiais", "Cláusulas Especiais"),
                           ("dados_bancarios", "Dados Bancários"), ("observacoes", "Observações")]:
            ctk.CTkLabel(parent, text=label, font=("Arial", 11)).pack(anchor="w", padx=10, pady=(5, 1))
            entry = ctk.CTkEntry(parent, fg_color=COLORS['bg_input'], height=32)
            entry.pack(fill="x", padx=10)
            if data and data.get(key):
                entry.insert(0, str(data[key]))
            fields[key] = entry

        def save():
            d = {k: e.get().strip() for k, e in fields.items()}
            pv = proc_var.get()
            d['lawsuit_id'] = int(pv.split(" - ")[0]) if pv and pv != "Nenhum processo" else None
            d['tipo'] = tipo_var.get()
            for f in ['valor_pedido', 'valor_obtido', 'parcelas']:
                try:
                    d[f] = float(d[f].replace(",", ".")) if d.get(f) else None
                except:
                    d[f] = None
            if mode == "create":
                db.create_settlement(d)
                messagebox.showinfo("Sucesso", "Acordo/Sentença cadastrado!")
            else:
                db.update_settlement(data['id'], d)
                messagebox.showinfo("Sucesso", "Acordo/Sentença atualizado!")
            self.show_page("acordos")

        ctk.CTkButton(parent, text="Salvar" if mode == "create" else "Atualizar",
                      fg_color=COLORS['accent'], height=40, command=save).pack(fill="x", padx=10, pady=15)

    # ==================== BIBLIOTECA ====================
    def build_biblioteca(self, parent):
        self.create_section_title(parent, "Biblioteca Jurídica", "Súmulas, jurisprudência, doutrina e OJs")

        tabview = ctk.CTkTabview(parent, fg_color=COLORS['bg_dark'])
        tabview.pack(fill="both", expand=True, padx=20, pady=10)
        tab_consulta = tabview.add("Consulta")
        tab_nova = tabview.add("Nova Referência")
        tab_editar = tabview.add("Editar Referência")

        # === ABA CONSULTA ===
        filter_frame = ctk.CTkFrame(tab_consulta, fg_color="transparent")
        filter_frame.pack(fill="x", padx=5, pady=5)
        ctk.CTkLabel(filter_frame, text="Tipo:").pack(side="left", padx=5)
        tipo_var = ctk.StringVar(value="todos")
        ctk.CTkOptionMenu(filter_frame, variable=tipo_var,
                          values=["todos", "sumula", "oj", "jurisprudencia", "doutrina"],
                          fg_color=COLORS['bg_input'], width=150).pack(side="left", padx=5)
        ctk.CTkLabel(filter_frame, text="Tema:").pack(side="left", padx=10)
        tema_var = ctk.StringVar(value="todos")
        ctk.CTkOptionMenu(filter_frame, variable=tema_var,
                          values=["todos", "justa_causa", "acidente_trabalho", "danos_morais", "horas_extras",
                                  "verbas_rescisorias", "rescisao_indireta", "prescricao", "honorarios",
                                  "terceirizacao", "equiparacao_salarial", "outros"],
                          fg_color=COLORS['bg_input'], width=180).pack(side="left", padx=5)
        search_entry = ctk.CTkEntry(filter_frame, fg_color=COLORS['bg_input'], width=200, placeholder_text="Buscar...")
        search_entry.pack(side="left", padx=10)

        result_frame = ctk.CTkScrollableFrame(tab_consulta, fg_color="transparent")
        result_frame.pack(fill="both", expand=True, padx=5, pady=5)

        def load_refs():
            for w in result_frame.winfo_children():
                w.destroy()
            refs = db.get_all_legal_references()
            tipo = tipo_var.get()
            tema = tema_var.get()
            query = search_entry.get().lower()
            if tipo != "todos":
                refs = [r for r in refs if r['tipo'] == tipo]
            if tema != "todos":
                refs = [r for r in refs if r['tema'] == tema]
            if query:
                refs = [r for r in refs if query in (r.get('titulo', '') + r.get('trecho', '')).lower()]

            ctk.CTkLabel(result_frame, text=f"{len(refs)} referências encontradas",
                         font=("Arial", 12), text_color=COLORS['text_secondary']).pack(anchor="w", pady=5)

            for ref in refs:
                card = ctk.CTkFrame(result_frame, fg_color=COLORS['bg_card'], corner_radius=10)
                card.pack(fill="x", pady=4)
                tipo_color = {'sumula': COLORS['accent'], 'jurisprudencia': COLORS['success'],
                              'oj': COLORS['warning'], 'doutrina': COLORS['cliente']}.get(ref['tipo'], COLORS['text'])
                header = ctk.CTkFrame(card, fg_color="transparent")
                header.pack(fill="x", padx=15, pady=(10, 2))
                ctk.CTkLabel(header, text=f"[{ref['tipo'].upper()}] ID:{ref['id']}", font=("Arial", 9, "bold"),
                             text_color=tipo_color).pack(side="left")
                ctk.CTkLabel(header, text=f" {ref['titulo']}", font=("Arial", 11, "bold"),
                             text_color=COLORS['text']).pack(side="left", padx=5)
                ctk.CTkLabel(header, text=f"Tema: {ref['tema']}", font=("Arial", 9),
                             text_color=COLORS['text_secondary']).pack(side="right")

                # Botão excluir
                ref_id = ref['id']
                ctk.CTkButton(header, text="X", width=25, height=25, fg_color=COLORS['danger'],
                              command=lambda rid=ref_id: self._delete_ref(rid)).pack(side="right", padx=5)

                if ref.get('trecho'):
                    ctk.CTkLabel(card, text=ref['trecho'][:300] + ("..." if len(ref.get('trecho', '')) > 300 else ""),
                                 font=("Arial", 10), text_color=COLORS['text_secondary'],
                                 wraplength=800, justify="left").pack(anchor="w", padx=15, pady=(2, 5))
                if ref.get('fonte'):
                    ctk.CTkLabel(card, text=f"Fonte: {ref['fonte']}", font=("Arial", 9),
                                 text_color=COLORS['gold']).pack(anchor="w", padx=15, pady=(0, 10))

        ctk.CTkButton(filter_frame, text="Filtrar", fg_color=COLORS['accent'], width=80,
                      command=load_refs).pack(side="left", padx=5)
        load_refs()

        # === ABA NOVA REFERÊNCIA ===
        self._build_referencia_form(tab_nova, mode="create")

        # === ABA EDITAR ===
        edit_id_var = ctk.StringVar()
        id_frame = ctk.CTkFrame(tab_editar, fg_color="transparent")
        id_frame.pack(fill="x", padx=10, pady=5)
        ctk.CTkLabel(id_frame, text="ID da Referência:").pack(side="left", padx=5)
        ctk.CTkEntry(id_frame, textvariable=edit_id_var, width=80, fg_color=COLORS['bg_input']).pack(side="left", padx=5)
        edit_container = ctk.CTkFrame(tab_editar, fg_color="transparent")
        edit_container.pack(fill="both", expand=True)

        def load_for_edit():
            rid = edit_id_var.get().strip()
            if not rid or not rid.isdigit():
                return
            ref = db.get_legal_reference_by_id(int(rid))
            if not ref:
                messagebox.showwarning("Aviso", "Referência não encontrada")
                return
            for w in edit_container.winfo_children():
                w.destroy()
            self._build_referencia_form(edit_container, mode="edit", data=ref)

        ctk.CTkButton(id_frame, text="Carregar", fg_color=COLORS['accent'], command=load_for_edit).pack(side="left", padx=5)

    def _build_referencia_form(self, parent, mode="create", data=None):
        scroll = ctk.CTkScrollableFrame(parent, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=5, pady=5)

        ctk.CTkLabel(scroll, text="Tipo *", font=("Arial", 11)).pack(anchor="w", padx=10, pady=(5, 1))
        tipo_var = ctk.StringVar(value=data.get('tipo', 'sumula') if data else 'sumula')
        ctk.CTkOptionMenu(scroll, variable=tipo_var, fg_color=COLORS['bg_input'],
                          values=['sumula', 'oj', 'jurisprudencia', 'doutrina']).pack(fill="x", padx=10)

        ctk.CTkLabel(scroll, text="Tema *", font=("Arial", 11)).pack(anchor="w", padx=10, pady=(5, 1))
        tema_var = ctk.StringVar(value=data.get('tema', 'outros') if data else 'outros')
        ctk.CTkOptionMenu(scroll, variable=tema_var, fg_color=COLORS['bg_input'],
                          values=['justa_causa', 'acidente_trabalho', 'danos_morais', 'horas_extras',
                                  'verbas_rescisorias', 'rescisao_indireta', 'prescricao', 'honorarios',
                                  'terceirizacao', 'equiparacao_salarial', 'outros']).pack(fill="x", padx=10)

        fields = {}
        for key, label in [("titulo", "Título *"), ("autor", "Autor"), ("fonte", "Fonte"), ("ano", "Ano")]:
            ctk.CTkLabel(scroll, text=label, font=("Arial", 11)).pack(anchor="w", padx=10, pady=(5, 1))
            entry = ctk.CTkEntry(scroll, fg_color=COLORS['bg_input'], height=32)
            entry.pack(fill="x", padx=10)
            if data and data.get(key):
                entry.insert(0, str(data[key]))
            fields[key] = entry

        ctk.CTkLabel(scroll, text="Trecho / Ementa *", font=("Arial", 11)).pack(anchor="w", padx=10, pady=(5, 1))
        trecho_tb = ctk.CTkTextbox(scroll, fg_color=COLORS['bg_input'], height=150)
        trecho_tb.pack(fill="x", padx=10)
        if data and data.get('trecho'):
            trecho_tb.insert("1.0", data['trecho'])

        def save():
            d = {k: e.get().strip() for k, e in fields.items()}
            d['tipo'] = tipo_var.get()
            d['tema'] = tema_var.get()
            d['trecho'] = trecho_tb.get("1.0", "end").strip()
            if not d.get('titulo') or not d.get('trecho'):
                messagebox.showwarning("Aviso", "Título e Trecho são obrigatórios")
                return
            try:
                d['ano'] = int(d['ano']) if d.get('ano') else None
            except:
                d['ano'] = None
            if mode == "create":
                db.create_legal_reference(d)
                messagebox.showinfo("Sucesso", "Referência cadastrada!")
            else:
                db.update_legal_reference(data['id'], d)
                messagebox.showinfo("Sucesso", "Referência atualizada!")
            self.show_page("biblioteca")

        ctk.CTkButton(scroll, text="Salvar" if mode == "create" else "Atualizar",
                      fg_color=COLORS['accent'], height=40, command=save).pack(fill="x", padx=10, pady=15)

    def _delete_ref(self, ref_id):
        if messagebox.askyesno("Confirmar", f"Excluir referência ID {ref_id}?"):
            db.delete_legal_reference(ref_id)
            self.show_page("biblioteca")

    # ==================== CALCULADORA ====================
    def build_calculadora(self, parent):
        self.create_section_title(parent, "Calculadora Trabalhista", "Cálculo completo de verbas rescisórias (CLT)")

        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="both", expand=True, padx=20, pady=10)
        left = ctk.CTkScrollableFrame(row, fg_color=COLORS['bg_card'], corner_radius=12, width=500)
        left.pack(side="left", fill="both", expand=True, padx=(0, 5))
        right = ctk.CTkScrollableFrame(row, fg_color=COLORS['bg_card'], corner_radius=12, width=500)
        right.pack(side="left", fill="both", expand=True, padx=(5, 0))

        ctk.CTkLabel(left, text="DADOS DO CONTRATO", font=("Arial", 14, "bold"), text_color=COLORS['gold']).pack(anchor="w", padx=15, pady=(10, 5))

        fields = {}
        for key, label, default in [
            ("salario", "Salário Base (R$)", "3000"),
            ("data_admissao", "Data Admissão (DD/MM/AAAA)", "01/01/2020"),
            ("data_demissao", "Data Demissão (DD/MM/AAAA)", "20/04/2026"),
            ("saldo_fgts", "Saldo FGTS (R$)", "0"),
            ("ferias_vencidas", "Férias Vencidas (períodos)", "0"),
            ("aviso_previo_dias", "Aviso Prévio (dias, 0=calcular)", "0"),
            ("dependentes", "Dependentes IRRF", "0"),
            ("filhos_menores", "Filhos Menores (sal.família)", "0"),
        ]:
            ctk.CTkLabel(left, text=label, font=("Arial", 10)).pack(anchor="w", padx=15, pady=(5, 1))
            entry = ctk.CTkEntry(left, fg_color=COLORS['bg_input'], height=30)
            entry.pack(fill="x", padx=15)
            entry.insert(0, default)
            fields[key] = entry

        ctk.CTkLabel(left, text="Tipo de Rescisão", font=("Arial", 10)).pack(anchor="w", padx=15, pady=(5, 1))
        tipo_var = ctk.StringVar(value="sem_justa_causa")
        ctk.CTkOptionMenu(left, variable=tipo_var, fg_color=COLORS['bg_input'],
                          values=["sem_justa_causa", "pedido_demissao", "justa_causa", "rescisao_indireta",
                                  "culpa_reciproca", "acordo_mutuo", "termino_contrato", "falecimento"]).pack(fill="x", padx=15)

        ctk.CTkLabel(right, text="ADICIONAIS", font=("Arial", 14, "bold"), text_color=COLORS['gold']).pack(anchor="w", padx=15, pady=(10, 5))

        for key, label, default in [
            ("horas_extras_50_mes", "Horas Extras 50%/mês", "0"),
            ("horas_extras_100_mes", "Horas Extras 100%/mês", "0"),
            ("horas_noturnas_mes", "Horas Noturnas/mês", "0"),
            ("grau_insalubridade", "Insalubridade (0/10/20/40)", "0"),
        ]:
            ctk.CTkLabel(right, text=label, font=("Arial", 10)).pack(anchor="w", padx=15, pady=(5, 1))
            entry = ctk.CTkEntry(right, fg_color=COLORS['bg_input'], height=30)
            entry.pack(fill="x", padx=15)
            entry.insert(0, default)
            fields[key] = entry

        pericul_var = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(right, text="Periculosidade (30%)", variable=pericul_var,
                        fg_color=COLORS['accent']).pack(anchor="w", padx=15, pady=5)
        vt_var = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(right, text="Desconto Vale-Transporte (6%)", variable=vt_var,
                        fg_color=COLORS['accent']).pack(anchor="w", padx=15, pady=5)
        multa477_var = ctk.BooleanVar(value=True)
        ctk.CTkCheckBox(right, text="Multa Art. 477 §8º CLT", variable=multa477_var,
                        fg_color=COLORS['accent']).pack(anchor="w", padx=15, pady=5)
        multa467_var = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(right, text="Multa Art. 467 CLT", variable=multa467_var,
                        fg_color=COLORS['accent']).pack(anchor="w", padx=15, pady=5)

        result_frame = ctk.CTkScrollableFrame(parent, fg_color=COLORS['bg_card'], corner_radius=12, height=400)
        result_frame.pack(fill="x", padx=20, pady=10)
        ctk.CTkLabel(result_frame, text="Clique em 'Calcular' para ver o resultado",
                     font=("Arial", 12), text_color=COLORS['text_secondary']).pack(pady=20)

        def calcular():
            for w in result_frame.winfo_children():
                w.destroy()
            try:
                d = {k: e.get().strip() for k, e in fields.items()}
                params = {
                    'salario_base': float(d['salario'].replace(',', '.') or '0'),
                    'data_admissao': d['data_admissao'],
                    'data_demissao': d['data_demissao'],
                    'tipo_rescisao': tipo_var.get(),
                    'saldo_fgts': float(d.get('saldo_fgts', '0').replace(',', '.') or '0'),
                    'periodos_ferias_vencidas': int(d.get('ferias_vencidas', '0') or '0'),
                    'aviso_previo': 'indenizado' if int(d.get('aviso_previo_dias', '0') or '0') > 0 else 'nenhum',
                    'num_dependentes': int(d.get('dependentes', '0') or '0'),
                    'num_filhos_menores': int(d.get('filhos_menores', '0') or '0'),
                    'horas_extras_50': float(d.get('horas_extras_50_mes', '0').replace(',', '.') or '0'),
                    'horas_extras_100': float(d.get('horas_extras_100_mes', '0').replace(',', '.') or '0'),
                    'adicional_noturno_horas': float(d.get('horas_noturnas_mes', '0').replace(',', '.') or '0'),
                    'insalubridade_grau': {0: None, 10: 'minimo', 20: 'medio', 40: 'maximo'}.get(
                        int(float(d.get('grau_insalubridade', '0') or '0')), None),
                    'periculosidade': pericul_var.get(),
                    'vale_transporte': vt_var.get(),
                    'multa_477': multa477_var.get(),
                    'multa_467': multa467_var.get(),
                }
                resultado = _calcular_verbas(params)
                # Exibir resultado
                ctk.CTkLabel(result_frame, text="RESULTADO DO CÁLCULO", font=("Arial", 16, "bold"),
                             text_color=COLORS['gold']).pack(anchor="w", padx=15, pady=(10, 5))

                cards = ctk.CTkFrame(result_frame, fg_color="transparent")
                cards.pack(fill="x", padx=15, pady=5)
                fgts_total = sum(v['valor'] for v in resultado.get('verbas', []) if 'FGTS' in v.get('descricao', ''))
                for i, (lbl, val, clr) in enumerate([
                    ("Total Bruto", formatar_moeda(resultado.get('total_bruto', 0)), COLORS['accent']),
                    ("Descontos", formatar_moeda(resultado.get('total_descontos', 0)), COLORS['danger']),
                    ("Total Líquido", formatar_moeda(resultado.get('total_liquido', 0)), COLORS['success']),
                    ("FGTS + Multa", formatar_moeda(fgts_total), COLORS['warning']),
                ]):
                    c = self.create_stat_card(cards, lbl, val, clr)
                    c.grid(row=0, column=i, padx=5, sticky="ew")
                for c in range(4):
                    cards.grid_columnconfigure(c, weight=1)

                # Verbas detalhadas
                ctk.CTkLabel(result_frame, text="VERBAS RESCISÓRIAS", font=("Arial", 13, "bold"),
                             text_color=COLORS['accent']).pack(anchor="w", padx=15, pady=(15, 5))
                for verba in resultado.get('verbas', []):
                    vf = ctk.CTkFrame(result_frame, fg_color=COLORS['bg_input'], corner_radius=6)
                    vf.pack(fill="x", padx=15, pady=2)
                    ctk.CTkLabel(vf, text=verba['descricao'], font=("Arial", 11)).pack(side="left", padx=10, pady=5)
                    ctk.CTkLabel(vf, text=formatar_moeda(verba['valor']), font=("Arial", 11, "bold"),
                                 text_color=COLORS['success']).pack(side="right", padx=10, pady=5)
                    if verba.get('fundamento'):
                        ctk.CTkLabel(vf, text=verba['fundamento'], font=("Arial", 8),
                                     text_color=COLORS['text_secondary']).pack(side="right", padx=10)

                # Descontos
                if resultado.get('descontos'):
                    ctk.CTkLabel(result_frame, text="DESCONTOS", font=("Arial", 13, "bold"),
                                 text_color=COLORS['danger']).pack(anchor="w", padx=15, pady=(15, 5))
                    for desc in resultado['descontos']:
                        df = ctk.CTkFrame(result_frame, fg_color=COLORS['bg_input'], corner_radius=6)
                        df.pack(fill="x", padx=15, pady=2)
                        ctk.CTkLabel(df, text=desc['descricao'], font=("Arial", 11)).pack(side="left", padx=10, pady=5)
                        ctk.CTkLabel(df, text=f"- {formatar_moeda(desc['valor'])}", font=("Arial", 11, "bold"),
                                     text_color=COLORS['danger']).pack(side="right", padx=10, pady=5)

                # Seguro-desemprego
                seguro = resultado.get('seguro_desemprego', {})
                if seguro.get('parcelas', 0) > 0:
                    ctk.CTkLabel(result_frame, text="SEGURO-DESEMPREGO", font=("Arial", 13, "bold"),
                                 text_color=COLORS['warning']).pack(anchor="w", padx=15, pady=(15, 5))
                    ctk.CTkLabel(result_frame, text=f"  {seguro['parcelas']} parcelas de {formatar_moeda(seguro.get('valor_parcela', 0))} = {formatar_moeda(seguro.get('total', 0))}",
                                 font=("Arial", 11)).pack(anchor="w", padx=15, pady=3)

                # Exportar
                def exportar_pdf():
                    path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF", "*.pdf")])
                    if path:
                        exp = PDFExporter()
                        exp.exportar_calculo(resultado, path)
                        messagebox.showinfo("Sucesso", f"PDF salvo em: {path}")

                ctk.CTkButton(result_frame, text="Exportar PDF", fg_color=COLORS['accent'],
                              command=exportar_pdf).pack(fill="x", padx=15, pady=15)

            except Exception as e:
                ctk.CTkLabel(result_frame, text=f"Erro: {str(e)}", font=("Arial", 12),
                             text_color=COLORS['danger']).pack(pady=20)

        ctk.CTkButton(parent, text="CALCULAR VERBAS RESCISÓRIAS", fg_color=COLORS['success'],
                      height=45, font=("Arial", 14, "bold"), command=calcular).pack(fill="x", padx=20, pady=(0, 5))

    # ==================== PREVISÃO ====================
    def build_previsao(self, parent):
        self.create_section_title(parent, "Previsão de Decisões", "Score preditivo baseado em dados históricos")
        lawsuits = db.get_all_lawsuits()
        judges = db.get_all_judges()
        analytics = self.analytics.gerar_previsao(lawsuits, judges)

        cards = ctk.CTkFrame(parent, fg_color="transparent")
        cards.pack(fill="x", padx=20, pady=10)
        for i, (lbl, val, clr) in enumerate([
            ("Score Geral", f"{analytics.get('score_geral', 0):.1f}/10", COLORS['accent']),
            ("Classificação", analytics.get('classificacao', '-'), COLORS['success']),
            ("Taxa Acordo", f"{analytics.get('taxa_acordo', 0):.1f}%", COLORS['warning']),
            ("Taxa Improcedência", f"{analytics.get('taxa_improcedencia', 0):.1f}%", COLORS['gold']),
        ]):
            c = self.create_stat_card(cards, lbl, val, clr)
            c.grid(row=0, column=i, padx=5, sticky="ew")
        for c in range(4):
            cards.grid_columnconfigure(c, weight=1)

        # Valor estratégico de acordo
        val_acordo = analytics.get('valor_estrategico_acordo', {})
        if val_acordo:
            ctk.CTkLabel(parent, text="Valor Estratégico de Acordo", font=("Arial", 14, "bold"),
                         text_color=COLORS['gold']).pack(anchor="w", padx=20, pady=(15, 5))
            af = ctk.CTkFrame(parent, fg_color=COLORS['bg_card'], corner_radius=10)
            af.pack(fill="x", padx=20, pady=5)
            ctk.CTkLabel(af, text=f"  Faixa: {formatar_moeda(val_acordo.get('min', 0))} a {formatar_moeda(val_acordo.get('max', 0))}",
                         font=("Arial", 13), text_color=COLORS['success']).pack(anchor="w", padx=15, pady=10)

        # Ranking de juízes
        ranking = analytics.get('ranking_juizes', [])
        if ranking:
            ctk.CTkLabel(parent, text="Ranking de Magistrados", font=("Arial", 14, "bold"),
                         text_color=COLORS['accent']).pack(anchor="w", padx=20, pady=(15, 5))
            cols = [("nome", "Magistrado", 200), ("score", "Score", 80), ("proc", "Processos", 80),
                    ("acordo", "% Acordo", 80)]
            data = [(r['nome'], f"{r.get('score', 0):.1f}", r.get('processos', 0),
                     f"{r.get('taxa_acordo', 0):.1f}%") for r in ranking[:10]]
            tf, _ = self.create_table(parent, cols, data)
            tf.pack(fill="x", padx=20, pady=5)

    # ==================== MOTOR DE TESES ====================
    def build_motor_teses(self, parent):
        self.create_section_title(parent, "Motor de Teses Jurídicas", "Ranking de teses e padrões de vitória/derrota")
        lawsuits = db.get_all_lawsuits()
        analytics = self.analytics.analisar_teses(lawsuits)

        cards = ctk.CTkFrame(parent, fg_color="transparent")
        cards.pack(fill="x", padx=20, pady=10)
        for i, (lbl, val, clr) in enumerate([
            ("Vitórias", analytics.get('total_vitorias', 0), COLORS['success']),
            ("Derrotas", analytics.get('total_derrotas', 0), COLORS['danger']),
            ("Taxa Êxito", f"{analytics.get('taxa_exito', 0):.1f}%", COLORS['gold']),
            ("Teses Analisadas", analytics.get('total_teses', 0), COLORS['accent']),
        ]):
            c = self.create_stat_card(cards, lbl, val, clr)
            c.grid(row=0, column=i, padx=5, sticky="ew")
        for c in range(4):
            cards.grid_columnconfigure(c, weight=1)

        ranking = analytics.get('ranking_teses', [])
        if ranking:
            ctk.CTkLabel(parent, text="Ranking de Teses por Taxa de Sucesso", font=("Arial", 14, "bold"),
                         text_color=COLORS['accent']).pack(anchor="w", padx=20, pady=(15, 5))
            cols = [("tese", "Tese", 250), ("sucesso", "% Sucesso", 100), ("total", "Total", 80)]
            data = [(t['tese'][:60], f"{t.get('taxa_sucesso', 0):.1f}%", t.get('total', 0)) for t in ranking]
            tf, _ = self.create_table(parent, cols, data)
            tf.pack(fill="x", padx=20, pady=5)

        # Hierarquia de provas
        provas = analytics.get('hierarquia_provas', [])
        if provas:
            ctk.CTkLabel(parent, text="Hierarquia de Provas", font=("Arial", 14, "bold"),
                         text_color=COLORS['gold']).pack(anchor="w", padx=20, pady=(15, 5))
            for p in provas:
                pf = ctk.CTkFrame(parent, fg_color=COLORS['bg_card'], corner_radius=8)
                pf.pack(fill="x", padx=20, pady=2)
                ctk.CTkLabel(pf, text=f"  {p['tipo']}", font=("Arial", 11)).pack(side="left", padx=10, pady=8)
                ctk.CTkLabel(pf, text=f"Peso: {p.get('peso', 0)}/10", font=("Arial", 11, "bold"),
                             text_color=COLORS['success']).pack(side="right", padx=10, pady=8)

    # ==================== RADAR DE RISCO ====================
    def build_radar_risco(self, parent):
        self.create_section_title(parent, "Radar de Risco Processual", "Classificação de risco por processo")
        lawsuits = db.get_all_lawsuits()
        judges = db.get_all_judges()
        analytics = self.analytics.calcular_risco(lawsuits, judges)

        cards = ctk.CTkFrame(parent, fg_color="transparent")
        cards.pack(fill="x", padx=20, pady=10)
        for i, (lbl, val, clr) in enumerate([
            ("Exposição Total", formatar_moeda(analytics.get('exposicao_total', 0)), COLORS['danger']),
            ("Risco Médio", f"{analytics.get('risco_medio', 0):.1f}/10", COLORS['warning']),
            ("Em Andamento", analytics.get('em_andamento', 0), COLORS['accent']),
            ("Encerrados", analytics.get('encerrados', 0), COLORS['success']),
        ]):
            c = self.create_stat_card(cards, lbl, val, clr)
            c.grid(row=0, column=i, padx=5, sticky="ew")
        for c in range(4):
            cards.grid_columnconfigure(c, weight=1)

        processos = analytics.get('processos', [])
        if processos:
            cols = [("num", "Processo", 170), ("risco", "Risco", 80), ("nivel", "Nível", 100),
                    ("exposicao", "Exposição", 120), ("acao", "Ação Recomendada", 250)]
            data = [(p.get('numero', '-'), f"{p.get('risco', 0)}/10", p.get('nivel', '-'),
                     formatar_moeda(p.get('exposicao', 0)), p.get('acao', '-')[:50]) for p in processos]
            tf, _ = self.create_table(parent, cols, data)
            tf.pack(fill="x", padx=20, pady=10)

    # ==================== VANTAGEM COMPETITIVA ====================
    def build_competitiva(self, parent):
        self.create_section_title(parent, "Máquina de Vantagem Competitiva", "KPIs consolidados e benchmarks")
        lawsuits = db.get_all_lawsuits()
        judges = db.get_all_judges()
        settlements = db.get_all_settlements()
        analytics = self.analytics.vantagem_competitiva(lawsuits, judges, settlements)

        cards = ctk.CTkFrame(parent, fg_color="transparent")
        cards.pack(fill="x", padx=20, pady=10)
        for i, (lbl, val, clr) in enumerate([
            ("Taxa Êxito", f"{analytics.get('taxa_exito', 0):.1f}%", COLORS['success']),
            ("Redução Média", f"{analytics.get('reducao_media', 0):.1f}%", COLORS['accent']),
            ("Economia Total", formatar_moeda(analytics.get('economia_total', 0)), COLORS['gold']),
            ("Valor Médio Acordo", formatar_moeda(analytics.get('valor_medio_acordo', 0)), COLORS['warning']),
        ]):
            c = self.create_stat_card(cards, lbl, val, clr)
            c.grid(row=0, column=i, padx=5, sticky="ew")
        for c in range(4):
            cards.grid_columnconfigure(c, weight=1)

        # Distribuição por polo
        dist = analytics.get('distribuicao_polo', {})
        if dist:
            ctk.CTkLabel(parent, text="Distribuição por Polo", font=("Arial", 14, "bold"),
                         text_color=COLORS['accent']).pack(anchor="w", padx=20, pady=(15, 5))
            for polo, dados in dist.items():
                pf = ctk.CTkFrame(parent, fg_color=COLORS['bg_card'], corner_radius=8)
                pf.pack(fill="x", padx=20, pady=3)
                ctk.CTkLabel(pf, text=f"  {polo.upper()}", font=("Arial", 12, "bold")).pack(side="left", padx=10, pady=8)
                ctk.CTkLabel(pf, text=f"{dados.get('total', 0)} processos | {dados.get('taxa_exito', 0):.1f}% êxito",
                             font=("Arial", 11), text_color=COLORS['text_secondary']).pack(side="right", padx=10, pady=8)

    # ==================== GERAR PEÇAS ====================
    def build_gerar_pecas(self, parent):
        self.create_section_title(parent, "Gerar Peças Jurídicas", "10 tipos de peça — IA, manual e histórico")

        tabview = ctk.CTkTabview(parent, fg_color=COLORS['bg_dark'])
        tabview.pack(fill="both", expand=True, padx=20, pady=10)
        tab_ia = tabview.add("Gerar via IA")
        tab_manual = tabview.add("Cadastro Manual")
        tab_historico = tabview.add("Histórico")

        # === ABA GERAR VIA IA ===
        lawsuits = db.get_all_lawsuits()
        judges = db.get_all_judges()
        refs = db.get_all_legal_references()

        ctk.CTkLabel(tab_ia, text="Processo *", font=("Arial", 11)).pack(anchor="w", padx=10, pady=(5, 1))
        proc_names = [f"{l['id']} - {l['numero_processo']} ({l['reclamante']} x {l['reclamada']})" for l in lawsuits]
        proc_var = ctk.StringVar(value=proc_names[0] if proc_names else "Nenhum processo")
        ctk.CTkOptionMenu(tab_ia, variable=proc_var, fg_color=COLORS['bg_input'],
                          values=proc_names if proc_names else ["Nenhum processo"]).pack(fill="x", padx=10)

        ctk.CTkLabel(tab_ia, text="Tipo de Peça *", font=("Arial", 11)).pack(anchor="w", padx=10, pady=(10, 1))
        tipos = list(TIPOS_PECA.keys())
        tipo_labels = {k: v['nome'] for k, v in TIPOS_PECA.items()}
        tipo_display = [f"{k} - {v['nome']}" for k, v in TIPOS_PECA.items()]
        tipo_var = ctk.StringVar(value=tipo_display[0] if tipo_display else "")
        ctk.CTkOptionMenu(tab_ia, variable=tipo_var, fg_color=COLORS['bg_input'],
                          values=tipo_display).pack(fill="x", padx=10)

        ctk.CTkLabel(tab_ia, text="Instruções Adicionais (opcional)", font=("Arial", 11)).pack(anchor="w", padx=10, pady=(10, 1))
        instrucoes_tb = ctk.CTkTextbox(tab_ia, fg_color=COLORS['bg_input'], height=60)
        instrucoes_tb.pack(fill="x", padx=10)

        ia_result_frame = ctk.CTkScrollableFrame(tab_ia, fg_color=COLORS['bg_card'], corner_radius=12)
        ia_result_frame.pack(fill="both", expand=True, padx=10, pady=10)
        ctk.CTkLabel(ia_result_frame, text="Selecione o processo e tipo de peça, depois clique em 'Gerar'",
                     font=("Arial", 12), text_color=COLORS['text_secondary']).pack(pady=20)

        def gerar_peca():
            for w in ia_result_frame.winfo_children():
                w.destroy()
            ctk.CTkLabel(ia_result_frame, text="Gerando peça... aguarde",
                         font=("Arial", 12), text_color=COLORS['warning']).pack(pady=20)
            ia_result_frame.update()

            try:
                pv = proc_var.get()
                if pv == "Nenhum processo":
                    messagebox.showwarning("Aviso", "Selecione um processo")
                    return
                proc_id = int(pv.split(" - ")[0])
                tipo_key = tipo_var.get().split(" - ")[0]
                instrucoes = instrucoes_tb.get("1.0", "end").strip()

                processo = db.get_lawsuit_by_id(proc_id)
                judge = db.get_judge_by_id(processo['judge_id']) if processo.get('judge_id') else None

                conteudo = self.gerador.gerar_peca(
                    tipo=tipo_key,
                    processo=processo,
                    juiz=judge,
                    referencias=refs,
                    instrucoes_adicionais=instrucoes
                )

                # Salvar no banco
                gerado_por = "openai" if self.gerador.api_key else "template"
                db.save_generated_piece(proc_id, tipo_key, conteudo, gerado_por)

                for w in ia_result_frame.winfo_children():
                    w.destroy()

                ctk.CTkLabel(ia_result_frame, text=f"Peça gerada: {TIPOS_PECA[tipo_key]['nome']}",
                             font=("Arial", 14, "bold"), text_color=COLORS['success']).pack(anchor="w", padx=10, pady=10)
                ctk.CTkLabel(ia_result_frame, text=f"Gerado por: {gerado_por.upper()} | {len(conteudo)} caracteres",
                             font=("Arial", 10), text_color=COLORS['text_secondary']).pack(anchor="w", padx=10)

                result_tb = ctk.CTkTextbox(ia_result_frame, fg_color=COLORS['bg_input'], height=400)
                result_tb.pack(fill="both", expand=True, padx=10, pady=10)
                result_tb.insert("1.0", conteudo)

                btn_f = ctk.CTkFrame(ia_result_frame, fg_color="transparent")
                btn_f.pack(fill="x", padx=10, pady=5)
                ctk.CTkButton(btn_f, text="Copiar", fg_color=COLORS['accent'],
                              command=lambda: (self.clipboard_clear(), self.clipboard_append(conteudo),
                                               messagebox.showinfo("Copiado", "Peça copiada!"))).pack(side="left", padx=5)
                ctk.CTkButton(btn_f, text="Salvar TXT", fg_color=COLORS['success'],
                              command=lambda: self._salvar_txt(conteudo, tipo_key)).pack(side="left", padx=5)
                ctk.CTkButton(btn_f, text="Exportar PDF", fg_color=COLORS['warning'],
                              command=lambda: self._exportar_peca_pdf(conteudo, tipo_key, processo)).pack(side="left", padx=5)

            except Exception as e:
                for w in ia_result_frame.winfo_children():
                    w.destroy()
                ctk.CTkLabel(ia_result_frame, text=f"Erro: {str(e)}", font=("Arial", 12),
                             text_color=COLORS['danger']).pack(pady=20)

        ctk.CTkButton(tab_ia, text="GERAR PEÇA", fg_color=COLORS['success'], height=40,
                      font=("Arial", 13, "bold"), command=gerar_peca).pack(fill="x", padx=10, pady=(5, 10))

        # === ABA CADASTRO MANUAL ===
        ctk.CTkLabel(tab_manual, text="Título da Peça *", font=("Arial", 11)).pack(anchor="w", padx=10, pady=(10, 1))
        titulo_entry = ctk.CTkEntry(tab_manual, fg_color=COLORS['bg_input'], height=32)
        titulo_entry.pack(fill="x", padx=10)

        ctk.CTkLabel(tab_manual, text="Tipo de Peça *", font=("Arial", 11)).pack(anchor="w", padx=10, pady=(10, 1))
        tipo_manual_var = ctk.StringVar(value=tipo_display[0] if tipo_display else "")
        ctk.CTkOptionMenu(tab_manual, variable=tipo_manual_var, fg_color=COLORS['bg_input'],
                          values=tipo_display).pack(fill="x", padx=10)

        ctk.CTkLabel(tab_manual, text="Processo (opcional)", font=("Arial", 11)).pack(anchor="w", padx=10, pady=(10, 1))
        proc_manual_var = ctk.StringVar(value="(Nenhum)")
        ctk.CTkOptionMenu(tab_manual, variable=proc_manual_var, fg_color=COLORS['bg_input'],
                          values=["(Nenhum)"] + proc_names).pack(fill="x", padx=10)

        ctk.CTkLabel(tab_manual, text="Conteúdo da Peça *", font=("Arial", 11)).pack(anchor="w", padx=10, pady=(10, 1))
        manual_tb = ctk.CTkTextbox(tab_manual, fg_color=COLORS['bg_input'], height=250)
        manual_tb.pack(fill="both", expand=True, padx=10)

        # Contador de caracteres
        counter_label = ctk.CTkLabel(tab_manual, text="0 caracteres | 0 palavras",
                                     font=("Arial", 9), text_color=COLORS['text_secondary'])
        counter_label.pack(anchor="e", padx=10)

        def update_counter(event=None):
            text = manual_tb.get("1.0", "end").strip()
            chars = len(text)
            words = len(text.split()) if text else 0
            counter_label.configure(text=f"{chars} caracteres | {words} palavras")

        manual_tb.bind("<KeyRelease>", update_counter)

        def salvar_manual():
            titulo = titulo_entry.get().strip()
            conteudo = manual_tb.get("1.0", "end").strip()
            if not titulo or not conteudo:
                messagebox.showwarning("Aviso", "Título e conteúdo são obrigatórios")
                return
            tipo_key = tipo_manual_var.get().split(" - ")[0]
            pmv = proc_manual_var.get()
            proc_id = int(pmv.split(" - ")[0]) if pmv != "(Nenhum)" else None
            full_content = f"# {titulo}\n\n{conteudo}"
            if proc_id:
                db.save_generated_piece(proc_id, tipo_key, full_content, "manual")
            else:
                # Salvar sem processo vinculado (usar ID 0)
                db.save_generated_piece(0, tipo_key, full_content, "manual")
            messagebox.showinfo("Sucesso", "Peça cadastrada com sucesso!")
            titulo_entry.delete(0, "end")
            manual_tb.delete("1.0", "end")

        ctk.CTkButton(tab_manual, text="SALVAR PEÇA", fg_color=COLORS['success'], height=40,
                      font=("Arial", 13, "bold"), command=salvar_manual).pack(fill="x", padx=10, pady=10)

        # === ABA HISTÓRICO ===
        pieces = db.get_generated_pieces()
        if not pieces:
            ctk.CTkLabel(tab_historico, text="Nenhuma peça gerada ou cadastrada ainda",
                         font=("Arial", 12), text_color=COLORS['text_secondary']).pack(pady=30)
        else:
            ctk.CTkLabel(tab_historico, text=f"{len(pieces)} peças no histórico",
                         font=("Arial", 12), text_color=COLORS['text_secondary']).pack(anchor="w", padx=10, pady=5)
            hist_scroll = ctk.CTkScrollableFrame(tab_historico, fg_color="transparent")
            hist_scroll.pack(fill="both", expand=True, padx=5, pady=5)
            for piece in pieces:
                card = ctk.CTkFrame(hist_scroll, fg_color=COLORS['bg_card'], corner_radius=10)
                card.pack(fill="x", pady=3)
                header = ctk.CTkFrame(card, fg_color="transparent")
                header.pack(fill="x", padx=15, pady=(8, 2))
                tipo_nome = TIPOS_PECA.get(piece.get('tipo_peca', ''), {}).get('nome', piece.get('tipo_peca', '-'))
                ctk.CTkLabel(header, text=f"[{tipo_nome}]", font=("Arial", 10, "bold"),
                             text_color=COLORS['accent']).pack(side="left")
                ctk.CTkLabel(header, text=f"  Gerado por: {piece.get('gerado_por', '-')}",
                             font=("Arial", 9), text_color=COLORS['text_secondary']).pack(side="left", padx=5)
                ctk.CTkLabel(header, text=f"{piece.get('created_at', '-')}", font=("Arial", 9),
                             text_color=COLORS['text_secondary']).pack(side="right")

                conteudo = piece.get('conteudo', '')
                ctk.CTkLabel(card, text=conteudo[:200] + ("..." if len(conteudo) > 200 else ""),
                             font=("Arial", 10), text_color=COLORS['text_secondary'],
                             wraplength=800, justify="left").pack(anchor="w", padx=15, pady=(2, 5))

                btn_f = ctk.CTkFrame(card, fg_color="transparent")
                btn_f.pack(fill="x", padx=15, pady=(0, 8))
                piece_conteudo = conteudo
                piece_id = piece['id']
                ctk.CTkButton(btn_f, text="Copiar", width=70, height=25, fg_color=COLORS['accent'],
                              command=lambda c=piece_conteudo: (self.clipboard_clear(), self.clipboard_append(c),
                                                                 messagebox.showinfo("Copiado", "Copiado!"))).pack(side="left", padx=3)
                ctk.CTkButton(btn_f, text="Excluir", width=70, height=25, fg_color=COLORS['danger'],
                              command=lambda pid=piece_id: self._delete_piece(pid)).pack(side="left", padx=3)

    def _delete_piece(self, piece_id):
        if messagebox.askyesno("Confirmar", f"Excluir peça ID {piece_id}?"):
            db.delete_generated_piece(piece_id)
            self.show_page("gerar_pecas")

    def _salvar_txt(self, conteudo, tipo):
        path = filedialog.asksaveasfilename(defaultextension=".txt",
                                            filetypes=[("Texto", "*.txt")],
                                            initialfile=f"peca_{tipo}.txt")
        if path:
            with open(path, "w", encoding="utf-8") as f:
                f.write(conteudo)
            messagebox.showinfo("Sucesso", f"Salvo em: {path}")

    def _exportar_peca_pdf(self, conteudo, tipo, processo):
        path = filedialog.asksaveasfilename(defaultextension=".pdf",
                                            filetypes=[("PDF", "*.pdf")],
                                            initialfile=f"peca_{tipo}_{processo['numero_processo']}.pdf")
        if path:
            exp = PDFExporter()
            exp.exportar_peca(conteudo, tipo, processo, path)
            messagebox.showinfo("Sucesso", f"PDF salvo em: {path}")

    # ==================== API CONFIG ====================
    def build_api_config(self, parent):
        self.create_section_title(parent, "Configuração API OpenAI", "Configure sua chave para geração de peças via IA")

        card = ctk.CTkFrame(parent, fg_color=COLORS['bg_card'], corner_radius=12)
        card.pack(fill="x", padx=20, pady=20)

        status = "Conectada" if self.gerador.api_key else "Não configurada"
        status_color = COLORS['success'] if self.gerador.api_key else COLORS['danger']
        ctk.CTkLabel(card, text=f"Status: {status}", font=("Arial", 14, "bold"),
                     text_color=status_color).pack(anchor="w", padx=20, pady=(15, 5))
        ctk.CTkLabel(card, text="Sem a chave, as peças serão geradas por templates locais estruturados.",
                     font=("Arial", 11), text_color=COLORS['text_secondary']).pack(anchor="w", padx=20, pady=(0, 10))

        ctk.CTkLabel(card, text="Chave API OpenAI:", font=("Arial", 12)).pack(anchor="w", padx=20, pady=(10, 3))
        key_entry = ctk.CTkEntry(card, fg_color=COLORS['bg_input'], height=35, show="*")
        key_entry.pack(fill="x", padx=20)
        if self.gerador.api_key:
            key_entry.insert(0, self.gerador.api_key)

        ctk.CTkLabel(card, text="Modelo:", font=("Arial", 12)).pack(anchor="w", padx=20, pady=(10, 3))
        model_var = ctk.StringVar(value=self.gerador.model)
        ctk.CTkOptionMenu(card, variable=model_var, fg_color=COLORS['bg_input'],
                          values=["gpt-4.1", "gpt-4o", "gpt-4-turbo", "gpt-3.5-turbo"]).pack(fill="x", padx=20)

        def salvar_config():
            key = key_entry.get().strip()
            self.gerador.api_key = key if key else None
            self.gerador.model = model_var.get()
            messagebox.showinfo("Sucesso", "Configuração salva!")
            self.show_page("api_config")

        ctk.CTkButton(card, text="Salvar Configuração", fg_color=COLORS['accent'],
                      height=40, command=salvar_config).pack(fill="x", padx=20, pady=20)

        # Informações
        info = ctk.CTkFrame(parent, fg_color=COLORS['bg_card'], corner_radius=12)
        info.pack(fill="x", padx=20, pady=10)
        ctk.CTkLabel(info, text="Tipos de Peça Disponíveis (10)", font=("Arial", 14, "bold"),
                     text_color=COLORS['gold']).pack(anchor="w", padx=20, pady=(15, 5))
        for key, val in TIPOS_PECA.items():
            ctk.CTkLabel(info, text=f"  • {val['nome']}", font=("Arial", 11),
                         text_color=COLORS['text']).pack(anchor="w", padx=20, pady=1)
        ctk.CTkLabel(info, text="", font=("Arial", 1)).pack(pady=5)

    # ==================== INTEGRAÇÃO LEGAL AI ====================
    def build_integracao_legal_ai(self, parent):
        self.create_section_title(parent, "Integração com Legal AI", "Conectar ao backend Legal AI para análises NLP")

        # Status da conexão
        from modules.api_bridge import LegalAIClient
        self.legal_ai_client = LegalAIClient()
        
        status_card = ctk.CTkFrame(parent, fg_color=COLORS['bg_card'], corner_radius=12)
        status_card.pack(fill="x", padx=20, pady=10)
        
        # Testa conexão
        connected = self.legal_ai_client.test_connection()
        status_text = "✓ Conectado ao Legal AI" if connected else "✗ Desconectado do Legal AI"
        status_color = COLORS['success'] if connected else COLORS['danger']
        
        ctk.CTkLabel(status_card, text=status_text, font=("Arial", 16, "bold"),
                     text_color=status_color).pack(anchor="w", padx=20, pady=(15, 5))
        
        # URL do servidor
        ctk.CTkLabel(status_card, text="URL do Servidor Legal AI:", font=("Arial", 12)).pack(anchor="w", padx=20, pady=(10, 3))
        url_entry = ctk.CTkEntry(status_card, fg_color=COLORS['bg_input'], height=35)
        url_entry.pack(fill="x", padx=20)
        url_entry.insert(0, self.legal_ai_client.base_url)
        
        def testar_conexao():
            nova_url = url_entry.get().strip()
            if nova_url:
                self.legal_ai_client.update_server_url(nova_url)
            connected = self.legal_ai_client.test_connection()
            if connected:
                messagebox.showinfo("Sucesso", "Conectado ao Legal AI!")
            else:
                messagebox.showerror("Erro", "Não foi possível conectar ao servidor Legal AI.\nVerifique a URL e tente novamente.")
            self.show_page("integracao_legal_ai")
        
        ctk.CTkButton(status_card, text="Testar Conexão", fg_color=COLORS['accent'],
                     height=40, command=testar_conexao).pack(fill="x", padx=20, pady=20)
        
        # Funcionalidades disponíveis
        features_card = ctk.CTkFrame(parent, fg_color=COLORS['bg_card'], corner_radius=12)
        features_card.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(features_card, text="Funcionalidades Disponíveis", font=("Arial", 14, "bold"),
                     text_color=COLORS['gold']).pack(anchor="w", padx=20, pady=(15, 5))
        
        features = [
            "📄 Análise NLP de Textos - Extração de entidades, classificação e sentimento",
            "📊 Sincronização de Processos - Compartilhar processos com Legal AI",
            "🔍 Busca Full-Text - Buscar documentos no Legal AI",
            "📋 Upload de Documentos - Enviar documentos para análise",
            "📈 Relatórios Consolidados - Gerar relatórios do Legal AI",
        ]
        
        for feature in features:
            ctk.CTkLabel(features_card, text=feature, font=("Arial", 11),
                        text_color=COLORS['text']).pack(anchor="w", padx=20, pady=3)
        
        # Informações de configuração
        info_card = ctk.CTkFrame(parent, fg_color=COLORS['bg_card'], corner_radius=12)
        info_card.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(info_card, text="Informações de Configuração", font=("Arial", 14, "bold"),
                     text_color=COLORS['gold']).pack(anchor="w", padx=20, pady=(15, 5))
        
        info_text = f"""Status de Conexão: {'Conectado' if connected else 'Desconectado'}
        
URL Base: {self.legal_ai_client.base_url}
Timeout: {self.legal_ai_client.timeout}s

Para configurar corretamente:
1. Certifique-se de que o Legal AI Backend está rodando
2. Informe a URL correta (ex: http://localhost:8000)
3. Clique em 'Testar Conexão' para validar
4. Uma vez conectado, você pode sincronizar dados entre os dois sistemas"""
        
        ctk.CTkLabel(info_card, text=info_text, font=("Arial", 10),
                     text_color=COLORS['text_secondary'], justify="left").pack(anchor="w", padx=20, pady=15)

    # ==================== MÉTODOS UTILITÁRIOS ====================
    def _delete_selected(self, tree, tipo):
        sel = tree.selection()
        if not sel:
            messagebox.showwarning("Aviso", "Selecione um item")
            return
        item_id = tree.item(sel[0])['values'][0]
        if not messagebox.askyesno("Confirmar", f"Excluir {tipo} ID {item_id}?"):
            return
        if tipo == "processo":
            db.delete_lawsuit(item_id)
            self.show_page("processos")
        elif tipo == "cliente":
            db.delete_cliente(item_id)
            self.show_page("clientes")
        elif tipo == "magistrado":
            db.delete_judge(item_id)
            self.show_page("magistrados")
        elif tipo == "acordo":
            db.delete_settlement(item_id)
            self.show_page("acordos")

    def _export_csv(self, tipo):
        path = filedialog.asksaveasfilename(defaultextension=".csv",
                                            filetypes=[("CSV", "*.csv")],
                                            initialfile=f"{tipo}.csv")
        if not path:
            return
        exp = CSVExporter()
        if tipo == "processos":
            exp.exportar_processos(db.get_all_lawsuits(), path)
        elif tipo == "clientes":
            exp.exportar_clientes(db.get_all_clientes(), path)
        messagebox.showinfo("Sucesso", f"CSV salvo em: {path}")


# ==================== MAIN ====================
if __name__ == "__main__":
    app = PainelJuridico()
    app.mainloop()
