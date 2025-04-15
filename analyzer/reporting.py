import pandas as pd
import logging

class ReportGenerator:
    """
    Classe responsável por gerar e exportar relatórios a partir dos resultados da análise.
    """
    def __init__(self, findings):
        self.findings = findings

    def generate_dataframe(self):
        """Gera um DataFrame pandas com os resultados da análise."""
        return pd.DataFrame(self.findings)

    def export_to_excel(self, filename):
        """Exporta os resultados da análise para um arquivo Excel formatado."""
        df = self.generate_dataframe()
        writer = pd.ExcelWriter(filename, engine='xlsxwriter')
        df.to_excel(writer, sheet_name='Análise CNPJ', index=False)
        workbook = writer.book
        worksheet = writer.sheets['Análise CNPJ']
        header_format = workbook.add_format({
            'bold': True,
            'bg_color': '#4472C4',
            'font_color': 'white',
            'border': 1,
            'text_wrap': True,
            'align': 'center',
            'valign': 'vcenter'
        })
        cell_format = workbook.add_format({
            'border': 1,
            'text_wrap': True,
            'valign': 'top'
        })
        number_format = workbook.add_format({
            'border': 1,
            'num_format': '0.0',
            'align': 'right'
        })
        for col_num, value in enumerate(df.columns.values):
            worksheet.write(0, col_num, value, header_format)
        col_widths = {
            'arquivo': 40,
            'linguagem': 12,
            'metodo': 20,
            'linha': 8,
            'tipo_uso': 12,
            'operacoes_numericas': 30,
            'impactos': 40,
            'riscos': 40,
            'modificacoes': 40,
            'severidade': 12,
            'horas_dev': 12,
            'horas_teste': 12,
            'horas_total': 12,
            'dependencias': 50,
            'sistemas_impactados': 30
        }
        for col_name, width in col_widths.items():
            if col_name in df.columns:
                col_idx = df.columns.get_loc(col_name)
                worksheet.set_column(col_idx, col_idx, width)
        for row_num in range(1, len(df) + 1):
            for col_num in range(len(df.columns)):
                if df.columns[col_num] in ['horas_dev', 'horas_teste', 'horas_total']:
                    worksheet.write(row_num, col_num, df.iloc[row_num-1, col_num], number_format)
                else:
                    worksheet.write(row_num, col_num, df.iloc[row_num-1, col_num], cell_format)
        dep_sheet = workbook.add_worksheet('Dependências')
        dep_sheet.write(0, 0, 'Linguagem', header_format)
        dep_sheet.write(0, 1, 'Método', header_format)
        dep_sheet.write(0, 2, 'Dependências', header_format)
        row = 1
        for finding in self.findings:
            if 'linguagem' in finding:
                dep_sheet.write(row, 0, finding['linguagem'])
            dep_sheet.write(row, 1, finding['metodo'])
            dep_sheet.write(row, 2, finding['dependencias'])
            row += 1
        dep_sheet.set_column(0, 0, 15)
        dep_sheet.set_column(1, 1, 30)
        dep_sheet.set_column(2, 2, 100)
        writer.close()
        logging.info(f'Relatório Excel exportado para: {filename}')
