"""Seed - Popular banco com dados iniciais da biblioteca jurídica (50+ referências)"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from core.database import init_db, get_connection, create_legal_reference, get_all_legal_references


def seed_legal_references():
    existing = get_all_legal_references()
    if len(existing) > 0:
        print(f"Biblioteca já possui {len(existing)} referências. Seed ignorado.")
        return

    refs = [
        # ==================== JUSTA CAUSA ====================
        {"tipo": "sumula", "tema": "justa_causa", "titulo": "Súmula 73 TST - Despedida por Justa Causa",
         "fonte": "TST", "trecho": "A ocorrência de justa causa, salvo a de abandono de emprego, no decurso do prazo do aviso prévio dado pelo empregador, retira do empregado qualquer direito às verbas rescisórias de natureza indenizatória.", "ano": 2003},
        {"tipo": "sumula", "tema": "justa_causa", "titulo": "Súmula 32 TST - Abandono de Emprego",
         "fonte": "TST", "trecho": "Presume-se o abandono de emprego se o trabalhador não retornar ao serviço no prazo de 30 dias após a cessação do benefício previdenciário nem justificar o motivo de não o fazer.", "ano": 2003},
        {"tipo": "sumula", "tema": "justa_causa", "titulo": "Súmula 212 TST - Despedimento. Ônus da Prova",
         "fonte": "TST", "trecho": "O ônus de provar o término do contrato de trabalho, quando negados a prestação de serviço e o despedimento, é do empregador, pois o princípio da continuidade da relação de emprego constitui presunção favorável ao empregado.", "ano": 2003},
        {"tipo": "sumula", "tema": "justa_causa", "titulo": "Súmula 77 TST - Punição",
         "fonte": "TST", "trecho": "Nula é a punição de empregado se não precedida de inquérito ou sindicância internos a que se obrigou a empresa por norma regulamentar.", "ano": 2003},

        # ==================== ACIDENTE DE TRABALHO ====================
        {"tipo": "sumula", "tema": "acidente_trabalho", "titulo": "Súmula 378 TST - Estabilidade Provisória",
         "fonte": "TST", "trecho": "São pressupostos para a concessão da estabilidade o afastamento superior a 15 dias e a consequente percepção do auxílio-doença acidentário, salvo se constatada, após a despedida, doença profissional que guarde relação de causalidade com a execução do contrato de emprego.", "ano": 2012},
        {"tipo": "sumula", "tema": "acidente_trabalho", "titulo": "Súmula 440 TST - Auxílio-Doença Acidentário",
         "fonte": "TST", "trecho": "Assegura-se o direito à manutenção de plano de saúde ou de assistência médica oferecido pela empresa ao empregado, não obstante suspenso o contrato de trabalho em virtude de auxílio-doença acidentário ou de aposentadoria por invalidez.", "ano": 2012},
        {"tipo": "sumula", "tema": "acidente_trabalho", "titulo": "Súmula 229 TST - Sobreaviso Eletricitários",
         "fonte": "TST", "trecho": "Por aplicação analógica do art. 244, § 2º, da CLT, as horas de sobreaviso dos eletricitários são remuneradas à base de 1/3 sobre a totalidade das parcelas de natureza salarial.", "ano": 2003},

        # ==================== DANOS MORAIS ====================
        {"tipo": "sumula", "tema": "danos_morais", "titulo": "Súmula 392 TST - Competência Dano Moral",
         "fonte": "TST", "trecho": "Nos termos do art. 114, inc. VI, da Constituição da República, a Justiça do Trabalho é competente para processar e julgar ações de indenização por dano moral e material, decorrentes da relação de trabalho.", "ano": 2005},
        {"tipo": "jurisprudencia", "tema": "danos_morais", "titulo": "Tema 143 TST - Dano Moral e Verbas Rescisórias (Tese Vinculante)",
         "fonte": "TST - IRR, DJ 15/05/2025", "trecho": "A ausência ou o atraso na quitação das verbas rescisórias, por si só, não configura dano moral indenizável, sendo necessária a comprovação de lesão concreta aos direitos de personalidade do trabalhador.", "ano": 2025},
        {"tipo": "jurisprudencia", "tema": "danos_morais", "titulo": "RR-10647-19.2014.5.15.0035 - Dano Moral por Não Pagamento",
         "fonte": "TST, 5ª Turma, Rel. Min. Breno Medeiros, DEJT 2018", "trecho": "Firmou-se na jurisprudência desta Corte entendimento no sentido de que a ausência de pagamento das verbas rescisórias, por si só, não enseja indenização por danos morais, sendo necessária a demonstração efetiva dos prejuízos causados à imagem e à honra do trabalhador.", "ano": 2018},

        # ==================== HORAS EXTRAS ====================
        {"tipo": "sumula", "tema": "horas_extras", "titulo": "Súmula 85 TST - Compensação de Jornada",
         "fonte": "TST", "trecho": "A compensação de jornada de trabalho deve ser ajustada por acordo individual escrito, acordo coletivo ou convenção coletiva. O não-atendimento das exigências legais para a compensação de jornada, inclusive quando encetada mediante acordo tácito, não implica a repetição do pagamento das horas excedentes à jornada normal diária, se não dilatada a jornada máxima semanal.", "ano": 2012},
        {"tipo": "sumula", "tema": "horas_extras", "titulo": "Súmula 338 TST - Jornada de Trabalho. Registro",
         "fonte": "TST", "trecho": "É ônus do empregador que conta com mais de 10 empregados o registro da jornada de trabalho na forma do art. 74, § 2º, da CLT. A não-apresentação injustificada dos controles de frequência gera presunção relativa de veracidade da jornada de trabalho.", "ano": 2003},
        {"tipo": "sumula", "tema": "horas_extras", "titulo": "Súmula 437 TST - Intervalo Intrajornada",
         "fonte": "TST", "trecho": "A não concessão ou a concessão parcial do intervalo intrajornada mínimo, para repouso e alimentação, a empregados urbanos e rurais, implica o pagamento total do período correspondente, e não apenas daquele suprimido, com acréscimo de, no mínimo, 50% sobre o valor da remuneração da hora normal de trabalho.", "ano": 2012},
        {"tipo": "sumula", "tema": "horas_extras", "titulo": "Súmula 172 TST - Repouso Remunerado. Horas Extras",
         "fonte": "TST", "trecho": "Computam-se no cálculo do repouso remunerado as horas extras habitualmente prestadas.", "ano": 2003},
        {"tipo": "sumula", "tema": "horas_extras", "titulo": "Súmula 264 TST - Hora Suplementar. Cálculo",
         "fonte": "TST", "trecho": "A remuneração do serviço suplementar é composta do valor da hora normal, integrado por parcelas de natureza salarial e acrescido do adicional previsto em lei, contrato, acordo, convenção coletiva ou sentença normativa.", "ano": 2003},
        {"tipo": "sumula", "tema": "horas_extras", "titulo": "Súmula 376 TST - Horas Extras. Limitação. Art. 59 CLT",
         "fonte": "TST", "trecho": "A limitação legal da jornada suplementar a duas horas diárias não exime o empregador de pagar todas as horas trabalhadas.", "ano": 2005},
        {"tipo": "oj", "tema": "horas_extras", "titulo": "OJ 394 SDI-1 TST - Horas Extras. Turnos Ininterruptos",
         "fonte": "TST - SDI-1", "trecho": "A majoração do valor do repouso semanal remunerado, em razão da integração das horas extras habitualmente prestadas, não repercute no cálculo das férias, da gratificação natalina, do aviso prévio e do FGTS, sob pena de caracterização de bis in idem.", "ano": 2010},

        # ==================== VERBAS RESCISÓRIAS ====================
        {"tipo": "sumula", "tema": "verbas_rescisorias", "titulo": "Súmula 14 TST - Culpa Recíproca",
         "fonte": "TST", "trecho": "Reconhecida a culpa recíproca na rescisão do contrato de trabalho (art. 484 da CLT), o empregado tem direito a 50% do valor do aviso prévio, do décimo terceiro salário e das férias proporcionais.", "ano": 2003},
        {"tipo": "sumula", "tema": "verbas_rescisorias", "titulo": "Súmula 171 TST - Férias Proporcionais",
         "fonte": "TST", "trecho": "Salvo na hipótese de dispensa do empregado por justa causa, a extinção do contrato de trabalho sujeita o empregador ao pagamento da remuneração das férias proporcionais, ainda que incompleto o período aquisitivo de 12 meses.", "ano": 2003},
        {"tipo": "sumula", "tema": "verbas_rescisorias", "titulo": "Súmula 12 TST - Carteira Profissional",
         "fonte": "TST", "trecho": "As anotações apostas pelo empregador na carteira profissional do empregado não geram presunção juris et de jure, mas apenas juris tantum.", "ano": 2003},
        {"tipo": "sumula", "tema": "verbas_rescisorias", "titulo": "Súmula 305 TST - FGTS. Incidência sobre Aviso Prévio",
         "fonte": "TST", "trecho": "O pagamento relativo ao período de aviso prévio, trabalhado ou não, está sujeito à contribuição para o FGTS.", "ano": 2003},
        {"tipo": "sumula", "tema": "verbas_rescisorias", "titulo": "Súmula 261 TST - Férias Proporcionais. Pedido de Demissão",
         "fonte": "TST", "trecho": "O empregado que se demite antes de completar 12 meses de serviço tem direito a férias proporcionais.", "ano": 2003},
        {"tipo": "sumula", "tema": "verbas_rescisorias", "titulo": "Súmula 7 TST - Férias",
         "fonte": "TST", "trecho": "A indenização pelo não-deferimento das férias no tempo oportuno será calculada com base na remuneração devida ao empregado na época da reclamação ou, se for o caso, na da extinção do contrato.", "ano": 2003},

        # ==================== RESCISÃO INDIRETA ====================
        {"tipo": "sumula", "tema": "rescisao_indireta", "titulo": "Súmula 13 TST - Mora Salarial",
         "fonte": "TST", "trecho": "O só pagamento dos salários atrasados em audiência não ilide a mora capaz de determinar a rescisão do contrato de trabalho.", "ano": 2003},

        # ==================== PRESCRIÇÃO ====================
        {"tipo": "sumula", "tema": "prescricao", "titulo": "Súmula 308 TST - Prescrição Quinquenal",
         "fonte": "TST", "trecho": "Respeitado o biênio subsequente à cessação contratual, a prescrição da ação trabalhista concerne às pretensões imediatamente anteriores a cinco anos, contados da data do ajuizamento da reclamação.", "ano": 2003},
        {"tipo": "sumula", "tema": "prescricao", "titulo": "Súmula 294 TST - Prescrição Total",
         "fonte": "TST", "trecho": "Tratando-se de ação que envolva pedido de prestações sucessivas decorrente de alteração do pactuado, a prescrição é total, exceto quando o direito à parcela esteja também assegurado por preceito de lei.", "ano": 2003},
        {"tipo": "sumula", "tema": "prescricao", "titulo": "Súmula 268 TST - Prescrição. Interrupção. Ação Trabalhista Arquivada",
         "fonte": "TST", "trecho": "A ação trabalhista, ainda que arquivada, interrompe a prescrição somente em relação aos pedidos idênticos.", "ano": 2003},

        # ==================== HONORÁRIOS ====================
        {"tipo": "sumula", "tema": "honorarios", "titulo": "Súmula 219 TST - Honorários Advocatícios",
         "fonte": "TST", "trecho": "Na Justiça do Trabalho, a condenação ao pagamento de honorários advocatícios não decorre pura e simplesmente da sucumbência, devendo a parte, concomitantemente: a) estar assistida por sindicato da categoria profissional; b) comprovar a percepção de salário inferior ao dobro do salário mínimo ou encontrar-se em situação econômica que não lhe permita demandar sem prejuízo do próprio sustento.", "ano": 2016},
        {"tipo": "jurisprudencia", "tema": "honorarios", "titulo": "ADI 5766 STF - Honorários e Justiça Gratuita",
         "fonte": "STF, Plenário, j. 20/10/2021", "trecho": "O STF julgou parcialmente procedente a ADI 5766, declarando inconstitucionais dispositivos que condicionavam a gratuidade de justiça ao pagamento de honorários periciais e sucumbenciais. Manteve a condenação em honorários mesmo para beneficiários da justiça gratuita, com suspensão de exigibilidade por 2 anos (art. 791-A §4º CLT).", "ano": 2021},
        {"tipo": "jurisprudencia", "tema": "honorarios", "titulo": "Tema 188 IRR TST - Honorários Sucumbenciais Trabalhistas",
         "fonte": "TST - IRR", "trecho": "Os honorários advocatícios sucumbenciais previstos no art. 791-A da CLT são devidos desde a entrada em vigor da Lei 13.467/2017 (Reforma Trabalhista), aplicando-se inclusive aos processos em curso.", "ano": 2022},

        # ==================== TERCEIRIZAÇÃO ====================
        {"tipo": "sumula", "tema": "terceirizacao", "titulo": "Súmula 331 TST - Contrato de Prestação de Serviços",
         "fonte": "TST", "trecho": "A contratação de trabalhadores por empresa interposta é ilegal, formando-se o vínculo diretamente com o tomador dos serviços, salvo no caso de trabalho temporário.", "ano": 2011},
        {"tipo": "jurisprudencia", "tema": "terceirizacao", "titulo": "ADPF 324 e RE 958252 STF - Terceirização Ampla",
         "fonte": "STF, Plenário, j. 30/08/2018", "trecho": "É lícita a terceirização ou qualquer outra forma de divisão do trabalho entre pessoas jurídicas distintas, independentemente do objeto social das empresas envolvidas, mantida a responsabilidade subsidiária da empresa contratante.", "ano": 2018},

        # ==================== EQUIPARAÇÃO SALARIAL ====================
        {"tipo": "sumula", "tema": "equiparacao_salarial", "titulo": "Súmula 6 TST - Equiparação Salarial",
         "fonte": "TST", "trecho": "Para os fins previstos no § 1º do art. 461 da CLT, só é válido o quadro de pessoal organizado em carreira quando homologado pelo Ministério do Trabalho, excluindo-se, apenas, dessa exigência o quadro de carreira das entidades de direito público da administração direta, autárquica e fundacional.", "ano": 2015},

        # ==================== INSALUBRIDADE / PERICULOSIDADE ====================
        {"tipo": "sumula", "tema": "insalubridade", "titulo": "Súmula 228 TST - Adicional de Insalubridade. Base de Cálculo",
         "fonte": "TST", "trecho": "O adicional de insalubridade será calculado sobre o salário básico, salvo critério mais vantajoso fixado em instrumento coletivo. (Súmula com eficácia suspensa por liminar do STF - Rcl 6.266)", "ano": 2008},
        {"tipo": "sumula", "tema": "insalubridade", "titulo": "Súmula 289 TST - Insalubridade. Adicional. Fornecimento de EPI",
         "fonte": "TST", "trecho": "O simples fornecimento do aparelho de proteção pelo empregador não o exime do pagamento do adicional de insalubridade. Cabe-lhe tomar as medidas que conduzam à diminuição ou eliminação da nocividade, entre as quais as relativas ao uso efetivo do equipamento pelo empregado.", "ano": 2003},
        {"tipo": "sumula", "tema": "insalubridade", "titulo": "Súmula 364 TST - Adicional de Periculosidade. Exposição Eventual",
         "fonte": "TST", "trecho": "Tem direito ao adicional de periculosidade o empregado exposto permanentemente ou que, de forma intermitente, sujeita-se a condições de risco. Indevido, apenas, quando o contato dá-se de forma eventual, assim considerado o fortuito, ou o que, sendo habitual, dá-se por tempo extremamente reduzido.", "ano": 2005},
        {"tipo": "sumula", "tema": "insalubridade", "titulo": "Súmula 191 TST - Adicional de Periculosidade. Base de Cálculo",
         "fonte": "TST", "trecho": "O adicional de periculosidade incide apenas sobre o salário básico e não sobre este acrescido de outros adicionais.", "ano": 2012},

        # ==================== VÍNCULO EMPREGATÍCIO ====================
        {"tipo": "sumula", "tema": "vinculo", "titulo": "Súmula 386 TST - Policial Militar. Reconhecimento de Vínculo",
         "fonte": "TST", "trecho": "Preenchidos os requisitos do art. 3º da CLT, é legítimo o reconhecimento de relação de emprego entre policial militar e empresa privada, independentemente do eventual cabimento de penalidade disciplinar prevista no Estatuto do Policial Militar.", "ano": 2005},
        {"tipo": "sumula", "tema": "vinculo", "titulo": "Súmula 12 TST - Carteira Profissional. Presunção",
         "fonte": "TST", "trecho": "As anotações apostas pelo empregador na carteira profissional do empregado não geram presunção juris et de jure, mas apenas juris tantum.", "ano": 2003},

        # ==================== AVISO PRÉVIO ====================
        {"tipo": "sumula", "tema": "aviso_previo", "titulo": "Súmula 276 TST - Aviso Prévio. Renúncia pelo Empregado",
         "fonte": "TST", "trecho": "O direito ao aviso prévio é irrenunciável pelo empregado. O pedido de dispensa de cumprimento não exime o empregador de pagar o respectivo valor, salvo comprovação de haver o prestador dos serviços obtido novo emprego.", "ano": 2003},
        {"tipo": "sumula", "tema": "aviso_previo", "titulo": "Súmula 230 TST - Aviso Prévio. Substituição pelo Pagamento",
         "fonte": "TST", "trecho": "É ilegal substituir o período que se reduz da jornada de trabalho, no aviso prévio, pelo pagamento das horas correspondentes.", "ano": 2003},
        {"tipo": "sumula", "tema": "aviso_previo", "titulo": "Súmula 305 TST - FGTS. Incidência sobre Aviso Prévio",
         "fonte": "TST", "trecho": "O pagamento relativo ao período de aviso prévio, trabalhado ou não, está sujeito à contribuição para o FGTS.", "ano": 2003},

        # ==================== SALÁRIO / REMUNERAÇÃO ====================
        {"tipo": "sumula", "tema": "salario", "titulo": "Súmula 91 TST - Salário Complessivo",
         "fonte": "TST", "trecho": "Nula é a cláusula contratual que fixa determinada importância ou percentagem para atender englobadamente vários direitos legais ou contratuais do trabalhador.", "ano": 2003},
        {"tipo": "sumula", "tema": "salario", "titulo": "Súmula 241 TST - Salário-Utilidade. Alimentação",
         "fonte": "TST", "trecho": "O vale para refeição, fornecido por força do contrato de trabalho, tem caráter salarial, integrando a remuneração do empregado, para todos os efeitos legais.", "ano": 2003},
        {"tipo": "sumula", "tema": "salario", "titulo": "Súmula 457 TST - Honorários Periciais. Beneficiário Justiça Gratuita",
         "fonte": "TST", "trecho": "A União é responsável pelo pagamento dos honorários de perito quando a parte sucumbente no objeto da perícia for beneficiária da assistência judiciária gratuita, observado o procedimento disposto nos arts. 1º, 2º e 5º da Resolução n.º 66/2010 do CSJT.", "ano": 2013},

        # ==================== CORREÇÃO MONETÁRIA / JUROS ====================
        {"tipo": "jurisprudencia", "tema": "correcao_monetaria", "titulo": "ADCs 58/59 e ADIs 5867/6021 STF - SELIC na Justiça do Trabalho",
         "fonte": "STF, Plenário, j. 18/12/2020", "trecho": "O STF fixou a SELIC como índice único de correção monetária e juros de mora na fase judicial trabalhista, prevalecendo sobre a TR prevista no §7º do art. 879 da CLT e sobre o IPCA-E. Na fase pré-judicial, aplica-se o IPCA-E acrescido de juros de mora.", "ano": 2020},

        # ==================== ESTABILIDADE ====================
        {"tipo": "sumula", "tema": "estabilidade", "titulo": "Súmula 244 TST - Gestante. Estabilidade Provisória",
         "fonte": "TST", "trecho": "I - O desconhecimento do estado gravídico pelo empregador não afasta o direito ao pagamento da indenização decorrente da estabilidade (art. 10, II, b do ADCT). III - A empregada gestante tem direito à estabilidade provisória prevista no art. 10, inciso II, alínea b, do ADCT, mesmo na hipótese de admissão mediante contrato por tempo determinado.", "ano": 2012},
        {"tipo": "sumula", "tema": "estabilidade", "titulo": "Súmula 369 TST - Dirigente Sindical. Estabilidade Provisória",
         "fonte": "TST", "trecho": "É assegurada a estabilidade provisória ao empregado dirigente sindical, ainda que a comunicação do registro da candidatura ou da eleição e da posse seja realizada fora do prazo previsto no art. 543, § 5º, da CLT, desde que a ciência ao empregador, por qualquer meio, ocorra na vigência do contrato de trabalho.", "ano": 2003},

        # ==================== REFORMA TRABALHISTA ====================
        {"tipo": "jurisprudencia", "tema": "reforma_trabalhista", "titulo": "Art. 457 §2º CLT pós-Reforma - Ajuda de Custo",
         "fonte": "CLT, art. 457, §2º (Lei 13.467/2017)", "trecho": "As importâncias, ainda que habituais, pagas a título de ajuda de custo, auxílio-alimentação (vedado seu pagamento em dinheiro), diárias para viagem, prêmios e abonos não integram a remuneração do empregado, não se incorporam ao contrato de trabalho e não constituem base de incidência de qualquer encargo trabalhista e previdenciário.", "ano": 2017},
        {"tipo": "jurisprudencia", "tema": "reforma_trabalhista", "titulo": "Art. 484-A CLT - Distrato por Acordo Mútuo",
         "fonte": "CLT, art. 484-A (Lei 13.467/2017)", "trecho": "O contrato de trabalho poderá ser extinto por acordo entre empregado e empregador, caso em que serão devidas: metade do aviso prévio (se indenizado) e metade da multa do FGTS (20%). O empregado poderá movimentar até 80% do saldo do FGTS, mas não terá direito ao seguro-desemprego.", "ano": 2017},

        # ==================== RITO SUMARÍSSIMO ====================
        {"tipo": "jurisprudencia", "tema": "rito_sumarissimo", "titulo": "RRAg-10008-06.2023.5.03.0104 - Rito Sumaríssimo. Liquidação",
         "fonte": "TST, 8ª Turma, DEJT 07/10/2024", "trecho": "No rito sumaríssimo, a petição inicial deve conter pedido certo e determinado, com indicação do valor correspondente (art. 852-B, I, CLT). A ausência de liquidação dos pedidos pode ensejar o arquivamento da reclamação.", "ano": 2024},
    ]

    count = 0
    for ref in refs:
        create_legal_reference(ref)
        count += 1
    print(f"Seed: {count} referências jurídicas inseridas na biblioteca.")


def run_seed():
    init_db()
    seed_legal_references()


if __name__ == "__main__":
    run_seed()
