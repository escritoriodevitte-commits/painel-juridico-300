#!/usr/bin/env python3
"""
CLI da Ferramenta para Eletricista de Painel Eletrônico Industrial.

Exemplos:
    python eletrica_cli.py motor --cv 10 --tensao 380
    python eletrica_cli.py disjuntor --corrente 20
    python eletrica_cli.py condutor --corrente 76 --fator 0.8
    python eletrica_cli.py queda --corrente 30 --comprimento 50 --secao 6 --tensao 380
    python eletrica_cli.py fp --potencia 50000 --fp-atual 0.78 --fp-desejado 0.92
    python eletrica_cli.py icc --kva 500 --tensao 380 --z 4.5
"""
import argparse
import json

from modules.eletrica import calc


def _print(resultado):
    print(json.dumps(resultado, indent=2, ensure_ascii=False))


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Cálculos elétricos para painéis industriais (NBR 5410)."
    )
    sub = parser.add_subparsers(dest="comando", required=True)

    p = sub.add_parser("motor", help="Corrente nominal de motor")
    p.add_argument("--cv", type=float, required=True, help="Potência no eixo (CV)")
    p.add_argument("--tensao", type=float, required=True)
    p.add_argument("--monofasico", action="store_true")
    p.add_argument("--rendimento", type=float, default=0.88)
    p.add_argument("--fp", type=float, default=0.85)

    p = sub.add_parser("disjuntor", help="Seleção de disjuntor comercial")
    p.add_argument("--corrente", type=float, required=True)
    p.add_argument("--fator-seguranca", type=float, default=1.25)

    p = sub.add_parser("contator", help="Seleção de contator AC-3")
    p.add_argument("--corrente", type=float, required=True)

    p = sub.add_parser("condutor", help="Dimensionamento de condutor por ampacidade")
    p.add_argument("--corrente", type=float, required=True)
    p.add_argument("--fator", type=float, default=1.0, help="Fator de correção (<=1)")

    p = sub.add_parser("queda", help="Queda de tensão num condutor")
    p.add_argument("--corrente", type=float, required=True)
    p.add_argument("--comprimento", type=float, required=True)
    p.add_argument("--secao", type=float, required=True)
    p.add_argument("--tensao", type=float, required=True)
    p.add_argument("--monofasico", action="store_true")
    p.add_argument("--material", default="cobre", choices=["cobre", "aluminio"])

    p = sub.add_parser("secao", help="Seção mínima para limitar a queda de tensão")
    p.add_argument("--corrente", type=float, required=True)
    p.add_argument("--comprimento", type=float, required=True)
    p.add_argument("--tensao", type=float, required=True)
    p.add_argument("--queda-max", type=float, default=calc.QUEDA_MAX_TERMINAL)
    p.add_argument("--monofasico", action="store_true")
    p.add_argument("--material", default="cobre", choices=["cobre", "aluminio"])

    p = sub.add_parser("fp", help="Correção de fator de potência")
    p.add_argument("--potencia", type=float, required=True, help="Potência ativa (W)")
    p.add_argument("--fp-atual", type=float, required=True)
    p.add_argument("--fp-desejado", type=float, default=0.92)

    p = sub.add_parser("icc", help="Corrente de curto-circuito no secundário do trafo")
    p.add_argument("--kva", type=float, required=True)
    p.add_argument("--tensao", type=float, required=True)
    p.add_argument("--z", type=float, required=True, help="Impedância (%)")

    args = parser.parse_args(argv)

    if args.comando == "motor":
        _print(calc.corrente_motor(args.cv, args.tensao, not args.monofasico,
                                    args.rendimento, args.fp))
    elif args.comando == "disjuntor":
        _print(calc.dimensionar_disjuntor(args.corrente, args.fator_seguranca))
    elif args.comando == "contator":
        _print(calc.dimensionar_contator(args.corrente))
    elif args.comando == "condutor":
        _print(calc.dimensionar_condutor(args.corrente, args.fator))
    elif args.comando == "queda":
        _print(calc.queda_tensao(args.corrente, args.comprimento, args.secao,
                                 args.tensao, not args.monofasico, args.material))
    elif args.comando == "secao":
        _print(calc.secao_minima_por_queda(args.corrente, args.comprimento, args.tensao,
                                           args.queda_max, not args.monofasico, args.material))
    elif args.comando == "fp":
        _print(calc.corrigir_fator_potencia(args.potencia, args.fp_atual, args.fp_desejado))
    elif args.comando == "icc":
        _print(calc.corrente_curto_circuito(args.kva, args.tensao, args.z))


if __name__ == "__main__":
    main()
