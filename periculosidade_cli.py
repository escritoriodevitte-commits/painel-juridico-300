#!/usr/bin/env python3
"""
CLI da Calculadora de Periculosidade do Eletricista (cálculo trabalhista).

Exemplos:
    python periculosidade_cli.py adicional --base 2500
    python periculosidade_cli.py reflexos --base 2500
    python periculosidade_cli.py retroativo --base 2500 --meses 36
    python periculosidade_cli.py retroativo --base 2500 --meses 72 --sem-fgts
"""
import argparse
import json

from modules.periculosidade import calc


def _print(resultado):
    print(json.dumps(resultado, indent=2, ensure_ascii=False))


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Cálculo do adicional de periculosidade do eletricista e reflexos."
    )
    sub = parser.add_subparsers(dest="comando", required=True)

    p = sub.add_parser("adicional", help="Adicional mensal de periculosidade (30%)")
    p.add_argument("--base", type=float, required=True, help="Salário-base (R$)")
    p.add_argument("--percentual", type=float, default=calc.PERCENTUAL_PERICULOSIDADE)

    p = sub.add_parser("reflexos", help="Reflexos anuais do adicional")
    p.add_argument("--base", type=float, required=True, help="Salário-base (R$)")
    p.add_argument("--sem-fgts", action="store_true")

    p = sub.add_parser("retroativo", help="Valor retroativo + reflexos (com prescrição)")
    p.add_argument("--base", type=float, required=True, help="Salário-base (R$)")
    p.add_argument("--meses", type=int, required=True, help="Período em meses")
    p.add_argument("--sem-fgts", action="store_true")
    p.add_argument("--percentual", type=float, default=calc.PERCENTUAL_PERICULOSIDADE)

    args = parser.parse_args(argv)

    if args.comando == "adicional":
        _print({"adicional_mensal": calc.calcular_adicional(args.base, args.percentual)})
    elif args.comando == "reflexos":
        adic = calc.calcular_adicional(args.base)
        _print(calc.calcular_reflexos(adic, incluir_fgts=not args.sem_fgts))
    elif args.comando == "retroativo":
        _print(calc.calcular_retroativo(args.base, args.meses,
                                        incluir_fgts=not args.sem_fgts,
                                        percentual=args.percentual))


if __name__ == "__main__":
    main()
