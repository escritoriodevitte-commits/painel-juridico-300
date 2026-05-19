"""Exportador CSV"""
import csv


class CSVExporter:
    @staticmethod
    def exportar_processos(lawsuits: list, filepath: str):
        if not lawsuits:
            with open(filepath, 'w', encoding='utf-8-sig') as f:
                f.write("Sem dados\n")
            return
        with open(filepath, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.DictWriter(f, fieldnames=lawsuits[0].keys(), delimiter=';')
            writer.writeheader()
            writer.writerows(lawsuits)

    @staticmethod
    def exportar_clientes(clientes: list, filepath: str):
        if not clientes:
            with open(filepath, 'w', encoding='utf-8-sig') as f:
                f.write("Sem dados\n")
            return
        with open(filepath, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.DictWriter(f, fieldnames=clientes[0].keys(), delimiter=';')
            writer.writeheader()
            writer.writerows(clientes)
