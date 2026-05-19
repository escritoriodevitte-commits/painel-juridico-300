"""
Gerador de Peças Jurídicas - Integração OpenAI GPT-4.1
Gera 10 tipos de peças jurídicas usando dados reais do processo,
perfil do magistrado e jurisprudência da biblioteca.
"""
import os
import json
from typing import Optional, Dict, List

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

TIPOS_PECA = {
    'reclamatoria_trabalhista': {'nome': 'RECLAMATÓRIA TRABALHISTA'},
    'contestacao': {'nome': 'CONTESTAÇÃO TRABALHISTA'},
    'alegacoes_finais': {'nome': 'ALEGAÇÕES FINAIS'},
    'rol_perguntas': {'nome': 'ROL DE PERGUNTAS PARA TESTEMUNHAS'},
    'recurso_ordinario': {'nome': 'RECURSO ORDINÁRIO'},
    'impugnacao': {'nome': 'IMPUGNAÇÃO AOS CÁLCULOS DE LIQUIDAÇÃO'},
    'manifestacao': {'nome': 'MANIFESTAÇÃO'},
    'pedido_habilitacao': {'nome': 'PEDIDO DE HABILITAÇÃO'},
    'procuracao': {'nome': 'PROCURAÇÃO AD JUDICIA'},
    'replica': {'nome': 'RÉPLICA À CONTESTAÇÃO'},
}


class GeradorPecas:
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY", "")
        self.model = "gpt-4.1"
        self.client = None
        if OPENAI_AVAILABLE and self.api_key:
            self.client = OpenAI(api_key=self.api_key)

    def atualizar_configuracao(self, api_key: Optional[str], model: Optional[str] = None):
        self.api_key = api_key or ""
        if model:
            self.model = model
        self.client = None
        if OPENAI_AVAILABLE and self.api_key:
            self.client = OpenAI(api_key=self.api_key)

    def is_available(self) -> bool:
        return self.client is not None

    def gerar_peca(self, lawsuit: Dict, judge: Optional[Dict], refs: List[Dict],
                   tipo: str, instrucoes: str = "") -> str:
        if not self.is_available():
            return self._gerar_template_local(lawsuit, judge, refs, tipo, instrucoes)

        system_prompt = self._build_system_prompt(tipo)
        user_prompt = self._build_user_prompt(lawsuit, judge, refs, tipo, instrucoes)

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3,
                max_tokens=8000,
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"[ERRO na geração via IA: {str(e)}]\n\n" + self._gerar_template_local(
                lawsuit, judge, refs, tipo, instrucoes)

    def _build_system_prompt(self, tipo: str) -> str:
        label = TIPOS_PECA.get(tipo, {}).get('nome', tipo.upper())
        polo = "RECLAMANTE" if tipo == 'reclamatoria_trabalhista' else "RECLAMADA"
        return f"""Você é um advogado trabalhista brasileiro especializado na elaboração de peças jurídicas.
Sua tarefa é redigir uma {label} de alto nível técnico, atuando pelo polo {polo}.

REGRAS OBRIGATÓRIAS:
1. Use APENAS súmulas, jurisprudência e legislação REAIS. NUNCA invente referências.
2. Fundamente cada argumento com base legal específica (artigo da CLT, súmula do TST, etc.).
3. Adapte a estratégia ao perfil do magistrado quando fornecido.
4. Use linguagem jurídica formal e precisa.
5. Estruture a peça com seções claras e numeradas.
6. Inclua pedidos específicos e fundamentados ao final.
7. Assine como "William Patrezzi Devitte - OAB/SP".
8. Foque no convencimento do juiz com argumentação estratégica.
9. NÃO use emojis ou linguagem informal.
10. Cite as fontes jurisprudenciais fornecidas quando pertinentes."""

    def _build_user_prompt(self, lawsuit: Dict, judge: Optional[Dict],
                           refs: List[Dict], tipo: str, instrucoes: str) -> str:
        prompt_parts = []
        prompt_parts.append("=== DADOS DO PROCESSO ===")
        prompt_parts.append(f"Número: {lawsuit.get('numero_processo', 'N/A')}")
        prompt_parts.append(f"Vara: {lawsuit.get('vara', 'N/A')}")
        prompt_parts.append(f"Reclamante: {lawsuit.get('reclamante', 'N/A')}")
        prompt_parts.append(f"Reclamada: {lawsuit.get('reclamada', 'N/A')}")
        prompt_parts.append(f"Status: {lawsuit.get('status', 'N/A')}")
        if lawsuit.get('valor_pedido'):
            prompt_parts.append(f"Valor Pedido: R$ {lawsuit['valor_pedido']:,.2f}")
        if lawsuit.get('tese_inicial'):
            prompt_parts.append(f"\nTese do Reclamante: {lawsuit['tese_inicial']}")
        if lawsuit.get('tese_defesa'):
            prompt_parts.append(f"\nTese de Defesa: {lawsuit['tese_defesa']}")

        if judge:
            prompt_parts.append("\n=== PERFIL DO MAGISTRADO ===")
            prompt_parts.append(f"Nome: {judge.get('name', 'N/A')}")
            prompt_parts.append(f"Vara: {judge.get('vara', 'N/A')}")
            prompt_parts.append(f"Tendência conciliatória: {judge.get('tendencia_conciliatoria', 'N/A')}")
            for campo in ['postura_justa_causa', 'postura_acidente', 'postura_danos_morais',
                          'postura_horas_extras', 'postura_rescisao_indireta']:
                val = judge.get(campo)
                if val:
                    label = campo.replace('postura_', '').replace('_', ' ').title()
                    prompt_parts.append(f"Postura em {label}: {val}")

        if refs:
            prompt_parts.append("\n=== JURISPRUDÊNCIA E SÚMULAS DISPONÍVEIS ===")
            for ref in refs[:15]:
                prompt_parts.append(f"- [{ref['tipo'].upper()}] {ref['titulo']}")
                prompt_parts.append(f"  Tema: {ref['tema']} | Fonte: {ref.get('fonte', 'N/A')}")
                trecho = ref.get('trecho', '')
                if trecho:
                    prompt_parts.append(f"  Trecho: {trecho[:300]}")
                prompt_parts.append("")

        if instrucoes:
            prompt_parts.append(f"\n=== INSTRUÇÕES ADICIONAIS DO ADVOGADO ===\n{instrucoes}")

        label = TIPOS_PECA.get(tipo, {}).get('nome', tipo.upper())
        prompt_parts.append(f"\nElabore uma {label} com base nos dados acima.")

        return '\n'.join(prompt_parts)

    def _gerar_template_local(self, lawsuit: Dict, judge: Optional[Dict],
                               refs: List[Dict], tipo: str, instrucoes: str) -> str:
        """Fallback: gera template estruturado sem IA"""
        label = TIPOS_PECA.get(tipo, {}).get('nome', tipo.upper())
        num = lawsuit.get('numero_processo', 'N/A')
        vara = lawsuit.get('vara', 'N/A')
        reclamante = lawsuit.get('reclamante', 'N/A')
        reclamada = lawsuit.get('reclamada', 'N/A')
        juiz_nome = judge.get('name', 'N/A') if judge else 'N/A'

        lines = []
        lines.append("=" * 70)
        lines.append(f"  {label}")
        lines.append(f"  [Gerado por template local - Configure a chave OpenAI para geração via IA]")
        lines.append("=" * 70)
        lines.append("")
        lines.append(f"Processo nº: {num}")
        lines.append(f"Vara: {vara}")
        if judge:
            lines.append(f"Juiz(a): {juiz_nome}")
        lines.append(f"Reclamante: {reclamante}")
        lines.append(f"Reclamada: {reclamada}")
        lines.append("")

        # ===== RECLAMATÓRIA TRABALHISTA =====
        if tipo == 'reclamatoria_trabalhista':
            lines.append(f"EXCELENTÍSSIMO(A) SENHOR(A) JUIZ(A) DO TRABALHO DA")
            lines.append(f"{vara.upper()}")
            lines.append("")
            lines.append(f"{reclamante.upper()}, brasileiro(a), [estado civil], [profissão],")
            lines.append(f"portador(a) do RG nº [___] e CPF nº [___], residente e domiciliado(a)")
            lines.append(f"em [endereço completo], vem, respeitosamente, à presença de Vossa")
            lines.append(f"Excelência, por seu advogado que esta subscreve, propor a presente")
            lines.append(f"RECLAMAÇÃO TRABALHISTA em face de")
            lines.append(f"{reclamada.upper()}, pessoa jurídica de direito privado, inscrita no")
            lines.append(f"CNPJ sob nº [___], com sede em [endereço completo], pelos fatos e")
            lines.append(f"fundamentos a seguir expostos:")
            lines.append("")
            lines.append("-" * 70)
            lines.append("I - DO CONTRATO DE TRABALHO")
            lines.append("-" * 70)
            lines.append("")
            lines.append(f"O(A) Reclamante foi admitido(a) pela Reclamada em [data de admissão],")
            lines.append(f"para exercer a função de [função], com salário mensal de R$ [valor],")
            lines.append(f"tendo sido dispensado(a) em [data de demissão] [sem justa causa / por]")
            lines.append(f"[pedido de demissão / rescisão indireta].")
            if lawsuit.get('tese_inicial'):
                lines.append("")
                lines.append(f"Contexto: {lawsuit['tese_inicial']}")
            lines.append("")
            lines.append("-" * 70)
            lines.append("II - DOS FATOS")
            lines.append("-" * 70)
            lines.append("")
            lines.append("[Narrar os fatos que fundamentam os pedidos, incluindo:")
            lines.append("- Irregularidades no contrato de trabalho")
            lines.append("- Verbas não pagas ou pagas incorretamente")
            lines.append("- Condições de trabalho inadequadas")
            lines.append("- Assédio moral ou sexual, se aplicável")
            lines.append("- Acidente de trabalho, se aplicável]")
            lines.append("")
            lines.append("-" * 70)
            lines.append("III - DO DIREITO")
            lines.append("-" * 70)
            lines.append("")
            lines.append("a) Das Verbas Rescisórias (art. 477 da CLT)")
            lines.append("   - Saldo de salário")
            lines.append("   - Aviso prévio indenizado (art. 487, §1º, CLT + Lei 12.506/2011)")
            lines.append("   - 13º salário proporcional (Lei 4.090/62)")
            lines.append("   - Férias proporcionais + 1/3 (art. 7º, XVII, CF)")
            lines.append("   - FGTS + multa de 40% (art. 18, §1º, Lei 8.036/90)")
            lines.append("   - Multa do art. 477, §8º, da CLT")
            lines.append("   - Guias de seguro-desemprego (Lei 7.998/90)")
            lines.append("")
            relevant_refs = [r for r in refs if r.get('trecho')][:5]
            if relevant_refs:
                lines.append("b) Da Fundamentação Jurisprudencial")
                for ref in relevant_refs:
                    lines.append(f'   • {ref["titulo"]}')
                    lines.append(f'     "{ref["trecho"][:200]}..."')
                    if ref.get('fonte'):
                        lines.append(f"     (Fonte: {ref['fonte']})")
                    lines.append("")
            lines.append("-" * 70)
            lines.append("IV - DOS PEDIDOS")
            lines.append("-" * 70)
            lines.append("")
            lines.append("Ante o exposto, requer:")
            lines.append("a) A citação da Reclamada para, querendo, contestar a presente;")
            lines.append("b) A condenação ao pagamento das verbas rescisórias devidas;")
            lines.append("c) A condenação ao pagamento de horas extras e reflexos;")
            lines.append("d) A condenação ao pagamento de indenização por danos morais;")
            lines.append("e) A condenação ao pagamento de honorários advocatícios (art. 791-A CLT);")
            lines.append("f) A concessão dos benefícios da justiça gratuita (art. 790, §3º, CLT);")
            lines.append("g) A produção de todas as provas em direito admitidas.")
            lines.append("")
            if lawsuit.get('valor_pedido'):
                lines.append(f"Dá-se à causa o valor de R$ {lawsuit['valor_pedido']:,.2f}.")
            else:
                lines.append("Dá-se à causa o valor de R$ [valor].")
            lines.append("")
            lines.append("Termos em que,")
            lines.append("Pede deferimento.")
            lines.append("")
            lines.append(f"[Cidade], [data].")
            lines.append("")
            lines.append("_______________________________")
            lines.append("William Patrezzi Devitte")
            lines.append("OAB/SP")

        # ===== CONTESTAÇÃO =====
        elif tipo == 'contestacao':
            lines.append(f"EXCELENTÍSSIMO(A) SENHOR(A) JUIZ(A) DO TRABALHO DA")
            lines.append(f"{vara.upper()}")
            lines.append("")
            lines.append(f"Processo nº {num}")
            lines.append("")
            lines.append(f"{reclamada.upper()}, já qualificada nos autos da Reclamação")
            lines.append(f"Trabalhista que lhe move {reclamante.upper()}, vem, respeitosamente,")
            lines.append("à presença de Vossa Excelência, por seu advogado que esta subscreve,")
            lines.append("apresentar CONTESTAÇÃO, pelos fatos e fundamentos a seguir expostos:")
            lines.append("")
            lines.append("-" * 70)
            lines.append("I - DOS FATOS")
            lines.append("-" * 70)
            lines.append("")
            if lawsuit.get('tese_defesa'):
                lines.append(lawsuit['tese_defesa'])
            else:
                lines.append("[Inserir narrativa dos fatos conforme versão da defesa]")
            lines.append("")
            if lawsuit.get('tese_inicial'):
                lines.append("-" * 70)
                lines.append("II - DA IMPUGNAÇÃO AOS PEDIDOS")
                lines.append("-" * 70)
                lines.append("")
                lines.append(f"A reclamante alega: {lawsuit['tese_inicial']}")
                lines.append("")
                lines.append("Tais alegações não merecem prosperar, conforme se demonstrará:")
                lines.append("")
            relevant_refs = [r for r in refs if r.get('trecho')][:5]
            if relevant_refs:
                lines.append("-" * 70)
                lines.append("III - DA FUNDAMENTAÇÃO JURÍDICA")
                lines.append("-" * 70)
                lines.append("")
                for ref in relevant_refs:
                    lines.append(f"• {ref['titulo']}")
                    lines.append(f'  "{ref["trecho"][:200]}..."')
                    if ref.get('fonte'):
                        lines.append(f"  (Fonte: {ref['fonte']})")
                    lines.append("")
            if judge:
                lines.append("-" * 70)
                lines.append("IV - CONSIDERAÇÕES ESTRATÉGICAS [NOTA INTERNA]")
                lines.append("-" * 70)
                lines.append("")
                lines.append(f"Magistrado: {juiz_nome}")
                lines.append(f"Tendência conciliatória: {judge.get('tendencia_conciliatoria', 'N/A')}")
                for campo in ['postura_justa_causa', 'postura_danos_morais', 'postura_horas_extras']:
                    val = judge.get(campo)
                    if val:
                        label_c = campo.replace('postura_', '').replace('_', ' ').title()
                        lines.append(f"Postura em {label_c}: {val}")
                lines.append("")
            lines.append("-" * 70)
            lines.append("DOS PEDIDOS")
            lines.append("-" * 70)
            lines.append("")
            lines.append("Ante o exposto, requer-se:")
            lines.append("a) A total improcedência dos pedidos formulados na inicial;")
            lines.append("b) A condenação da reclamante ao pagamento de honorários advocatícios;")
            lines.append("c) A produção de todas as provas em direito admitidas.")
            lines.append("")
            lines.append("Termos em que,")
            lines.append("Pede deferimento.")
            lines.append("")
            lines.append("_______________________________")
            lines.append("William Patrezzi Devitte")
            lines.append("OAB/SP")

        # ===== RÉPLICA =====
        elif tipo == 'replica':
            lines.append(f"EXCELENTÍSSIMO(A) SENHOR(A) JUIZ(A) DO TRABALHO DA")
            lines.append(f"{vara.upper()}")
            lines.append("")
            lines.append(f"Processo nº {num}")
            lines.append("")
            lines.append(f"{reclamante.upper()}, já qualificado(a) nos autos da Reclamação")
            lines.append(f"Trabalhista que move em face de {reclamada.upper()}, vem,")
            lines.append("respeitosamente, à presença de Vossa Excelência, apresentar")
            lines.append("RÉPLICA À CONTESTAÇÃO, pelos fatos e fundamentos a seguir:")
            lines.append("")
            lines.append("-" * 70)
            lines.append("I - DA CONTESTAÇÃO APRESENTADA")
            lines.append("-" * 70)
            lines.append("")
            lines.append("[Resumir os principais argumentos da contestação da reclamada]")
            if lawsuit.get('tese_defesa'):
                lines.append(f"\nA reclamada alega: {lawsuit['tese_defesa']}")
            lines.append("")
            lines.append("-" * 70)
            lines.append("II - DA IMPUGNAÇÃO PONTO A PONTO")
            lines.append("-" * 70)
            lines.append("")
            lines.append("[Impugnar cada argumento da contestação com fundamentação]")
            lines.append("")
            relevant_refs = [r for r in refs if r.get('trecho')][:5]
            if relevant_refs:
                lines.append("-" * 70)
                lines.append("III - DA FUNDAMENTAÇÃO JURÍDICA")
                lines.append("-" * 70)
                lines.append("")
                for ref in relevant_refs:
                    lines.append(f"• {ref['titulo']}")
                    lines.append(f'  "{ref["trecho"][:200]}..."')
                    lines.append("")
            lines.append("-" * 70)
            lines.append("IV - DO REQUERIMENTO")
            lines.append("-" * 70)
            lines.append("")
            lines.append("Ante o exposto, reitera todos os pedidos formulados na inicial,")
            lines.append("requerendo a total procedência da reclamação.")
            lines.append("")
            lines.append("_______________________________")
            lines.append("William Patrezzi Devitte")
            lines.append("OAB/SP")

        # ===== MANIFESTAÇÃO =====
        elif tipo == 'manifestacao':
            lines.append(f"EXCELENTÍSSIMO(A) SENHOR(A) JUIZ(A) DO TRABALHO DA")
            lines.append(f"{vara.upper()}")
            lines.append("")
            lines.append(f"Processo nº {num}")
            lines.append("")
            lines.append(f"[PARTE], já qualificada nos autos, vem, respeitosamente,")
            lines.append("à presença de Vossa Excelência, apresentar MANIFESTAÇÃO nos")
            lines.append("seguintes termos:")
            lines.append("")
            lines.append("-" * 70)
            lines.append("I - DO OBJETO DA MANIFESTAÇÃO")
            lines.append("-" * 70)
            lines.append("")
            lines.append("[Descrever o objeto da manifestação: despacho, decisão, documento,")
            lines.append("intimação ou qualquer ato processual que demande manifestação]")
            lines.append("")
            lines.append("-" * 70)
            lines.append("II - DA MANIFESTAÇÃO")
            lines.append("-" * 70)
            lines.append("")
            lines.append("[Apresentar os argumentos e fundamentação da manifestação]")
            lines.append("")
            lines.append("-" * 70)
            lines.append("III - DO REQUERIMENTO")
            lines.append("-" * 70)
            lines.append("")
            lines.append("Ante o exposto, requer o deferimento do quanto pleiteado.")
            lines.append("")
            lines.append("Termos em que,")
            lines.append("Pede deferimento.")
            lines.append("")
            lines.append("_______________________________")
            lines.append("William Patrezzi Devitte")
            lines.append("OAB/SP")

        # ===== PEDIDO DE HABILITAÇÃO =====
        elif tipo == 'pedido_habilitacao':
            lines.append(f"EXCELENTÍSSIMO(A) SENHOR(A) JUIZ(A) DO TRABALHO DA")
            lines.append(f"{vara.upper()}")
            lines.append("")
            lines.append(f"Processo nº {num}")
            lines.append("")
            lines.append(f"[NOME DO HABILITANDO], [qualificação completa], vem,")
            lines.append("respeitosamente, à presença de Vossa Excelência, requerer sua")
            lines.append("HABILITAÇÃO nos autos do processo em epígrafe, pelos seguintes")
            lines.append("fundamentos:")
            lines.append("")
            lines.append("-" * 70)
            lines.append("I - DOS FATOS")
            lines.append("-" * 70)
            lines.append("")
            lines.append("[Narrar os fatos que justificam a habilitação:")
            lines.append("- Falecimento da parte original (art. 110, CPC)")
            lines.append("- Cessão de crédito")
            lines.append("- Sucessão empresarial")
            lines.append("- Outro motivo legal]")
            lines.append("")
            lines.append("-" * 70)
            lines.append("II - DO DIREITO")
            lines.append("-" * 70)
            lines.append("")
            lines.append("A habilitação encontra amparo nos arts. 687 a 692 do CPC/2015,")
            lines.append("aplicáveis subsidiariamente ao processo do trabalho (art. 769 CLT).")
            lines.append("")
            lines.append("-" * 70)
            lines.append("III - DOS DOCUMENTOS")
            lines.append("-" * 70)
            lines.append("")
            lines.append("[Listar documentos comprobatórios: certidão de óbito, contrato de")
            lines.append("cessão, documentos de identificação do habilitando, etc.]")
            lines.append("")
            lines.append("-" * 70)
            lines.append("IV - DO REQUERIMENTO")
            lines.append("-" * 70)
            lines.append("")
            lines.append("Ante o exposto, requer a habilitação nos autos, com a consequente")
            lines.append("intimação da parte contrária para manifestação.")
            lines.append("")
            lines.append("_______________________________")
            lines.append("William Patrezzi Devitte")
            lines.append("OAB/SP")

        # ===== PROCURAÇÃO =====
        elif tipo == 'procuracao':
            lines.append("PROCURAÇÃO AD JUDICIA ET EXTRA")
            lines.append("")
            lines.append(f"OUTORGANTE: {reclamante.upper() if reclamante != 'N/A' else '[NOME COMPLETO]'},")
            lines.append(f"[nacionalidade], [estado civil], [profissão], portador(a) do RG nº [___]")
            lines.append(f"e inscrito(a) no CPF sob nº [___], residente e domiciliado(a) em")
            lines.append(f"[endereço completo].")
            lines.append("")
            lines.append("OUTORGADO: WILLIAM PATREZZI DEVITTE, advogado, inscrito na OAB/SP sob")
            lines.append("nº [___], com escritório profissional em [endereço do escritório],")
            lines.append("e-mail: [email], telefone: [telefone].")
            lines.append("")
            lines.append("PODERES: Pelo presente instrumento particular de procuração, o(a)")
            lines.append("OUTORGANTE nomeia e constitui o OUTORGADO como seu bastante procurador,")
            lines.append("a quem confere amplos poderes para o foro em geral, com a cláusula")
            lines.append('"ad judicia et extra", podendo propor ações, contestar, reconvir,')
            lines.append("transigir, desistir, renunciar, receber e dar quitação, firmar")
            lines.append("compromissos, substabelecer com ou sem reserva de poderes, e praticar")
            lines.append("todos os atos necessários ao fiel cumprimento deste mandato, inclusive")
            lines.append("receber citação inicial (art. 105 do CPC).")
            lines.append("")
            lines.append(f"Processo nº: {num}")
            lines.append(f"Vara: {vara}")
            lines.append("")
            lines.append(f"[Cidade], [data].")
            lines.append("")
            lines.append("_______________________________")
            lines.append(f"{reclamante.upper() if reclamante != 'N/A' else '[NOME DO OUTORGANTE]'}")
            lines.append("OUTORGANTE")

        # ===== ALEGAÇÕES FINAIS =====
        elif tipo == 'alegacoes_finais':
            lines.append("ALEGAÇÕES FINAIS")
            lines.append("")
            lines.append(f"[PARTE], nos autos da Reclamação Trabalhista")
            lines.append(f"nº {num}, vem apresentar suas ALEGAÇÕES FINAIS:")
            lines.append("")
            lines.append("I - DA INSTRUÇÃO PROCESSUAL")
            lines.append("[Resumo da instrução e provas produzidas]")
            lines.append("")
            lines.append("II - DA ANÁLISE DAS PROVAS")
            lines.append("[Análise das provas favoráveis]")
            lines.append("")
            lines.append("III - DO DIREITO")
            for ref in [r for r in refs if r.get('trecho')][:3]:
                lines.append(f'• {ref["titulo"]}: "{ref["trecho"][:150]}..."')
            lines.append("")
            lines.append("IV - DOS PEDIDOS")
            lines.append("Requer a total procedência/improcedência dos pedidos.")
            lines.append("")
            lines.append("_______________________________")
            lines.append("William Patrezzi Devitte")
            lines.append("OAB/SP")

        # ===== ROL DE PERGUNTAS =====
        elif tipo == 'rol_perguntas':
            lines.append("ROL DE PERGUNTAS PARA TESTEMUNHAS")
            lines.append("")
            lines.append("TESTEMUNHA DA RECLAMANTE:")
            lines.append("1. Qual era a função do(a) reclamante na empresa?")
            lines.append("2. Qual era o horário de trabalho?")
            lines.append("3. Havia registro de ponto?")
            lines.append("4. Como era o ambiente de trabalho?")
            lines.append("5. Presenciou algum fato relevante narrado na inicial?")
            lines.append("6. O(A) reclamante utilizava EPIs fornecidos pela empresa?")
            lines.append("7. Havia controle de ponto na empresa?")
            lines.append("8. Sabe informar sobre o pagamento de horas extras?")
            lines.append("9. Presenciou alguma situação de assédio ou discriminação?")
            lines.append("10. Sabe informar sobre as condições de segurança do trabalho?")
            lines.append("")
            lines.append("TESTEMUNHA DA RECLAMADA:")
            lines.append("1. Qual era a função do(a) depoente na empresa?")
            lines.append("2. Trabalhava no mesmo setor que o(a) reclamante?")
            lines.append("3. Como era controlada a jornada de trabalho?")
            lines.append("4. O(A) reclamante cumpria as normas da empresa?")
            lines.append("5. Tem conhecimento dos fatos narrados na inicial?")
            lines.append("6. Como era o relacionamento entre colegas e superiores?")
            lines.append("7. Houve alguma advertência ou medida disciplinar?")
            lines.append("8. A empresa fornecia EPIs adequados?")
            lines.append("9. Havia treinamentos de segurança do trabalho?")
            lines.append("10. Sabe informar sobre o motivo da rescisão contratual?")

        # ===== RECURSO ORDINÁRIO =====
        elif tipo == 'recurso_ordinario':
            lines.append("RECURSO ORDINÁRIO")
            lines.append("")
            lines.append(f"Processo nº {num}")
            lines.append("")
            lines.append("I - DA TEMPESTIVIDADE")
            lines.append("O presente recurso é tempestivo, interposto dentro do prazo")
            lines.append("legal de 8 dias úteis (art. 895, I, da CLT).")
            lines.append("")
            lines.append("II - DO PREPARO")
            lines.append("Custas processuais e depósito recursal recolhidos conforme")
            lines.append("guias em anexo (art. 899, §§ 1º e 4º, da CLT).")
            lines.append("")
            lines.append("III - DAS RAZÕES DO RECURSO")
            lines.append("[Fundamentar os pontos de reforma da sentença]")
            lines.append("")
            lines.append("IV - DO DIREITO")
            for ref in [r for r in refs if r.get('trecho')][:3]:
                lines.append(f'• {ref["titulo"]}: "{ref["trecho"][:150]}..."')
            lines.append("")
            lines.append("V - DO PEDIDO")
            lines.append("Requer o conhecimento e provimento do presente recurso para")
            lines.append("reformar a r. sentença nos pontos impugnados.")
            lines.append("")
            lines.append("_______________________________")
            lines.append("William Patrezzi Devitte")
            lines.append("OAB/SP")

        # ===== IMPUGNAÇÃO =====
        elif tipo == 'impugnacao':
            lines.append("IMPUGNAÇÃO AOS CÁLCULOS DE LIQUIDAÇÃO")
            lines.append("")
            lines.append(f"Processo nº {num}")
            if lawsuit.get('valor_pedido'):
                lines.append(f"Valor da causa: R$ {lawsuit['valor_pedido']:,.2f}")
            lines.append("")
            lines.append("I - DOS CÁLCULOS APRESENTADOS")
            lines.append("[Analisar os cálculos e apontar divergências]")
            lines.append("")
            lines.append("II - DOS PARÂMETROS CORRETOS")
            lines.append("[Apresentar os cálculos corretos com fundamentação]")
            lines.append("")
            lines.append("III - DA CORREÇÃO MONETÁRIA")
            lines.append("Conforme ADCs 58/59 do STF, aplica-se a SELIC como índice")
            lines.append("único na fase judicial.")
            lines.append("")
            lines.append("_______________________________")
            lines.append("William Patrezzi Devitte")
            lines.append("OAB/SP")

        # ===== TIPO NÃO RECONHECIDO =====
        else:
            lines.append(f"[Peça do tipo '{tipo}' - Preencha o conteúdo manualmente]")
            lines.append("")
            lines.append(f"Processo nº {num}")
            lines.append(f"Vara: {vara}")
            lines.append("")

        if instrucoes:
            lines.append("")
            lines.append("-" * 70)
            lines.append("INSTRUÇÕES ADICIONAIS DO ADVOGADO:")
            lines.append(instrucoes)

        return '\n'.join(lines)
