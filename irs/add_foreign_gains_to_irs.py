import pandas as pd
import datetime
import lxml.etree as etree
import argparse


def parse_date(date_string):
    return datetime.datetime.strptime(date_string, '%Y-%m-%d')


def get_years_and_months(date_series):
    dates = list(map(parse_date, date_series))
    years_and_months = list(map(lambda x: (x.year, x.month), dates))
    years = list(map(lambda x: x[0], years_and_months))
    months = list(map(lambda x: x[1], years_and_months))
    return years, months


def convert_to_irs_format(transactions, country_code):
    transactions_renamed = transactions.rename(columns={
        "Data": "DataRealizacao",
        "Valor": "ValorRealizacao",
        "Data.1": "DataAquisicao",
        "Valor.1": "ValorAquisicao",
        "Código": "Codigo",
        "Despesas": "DespesasEncargos"
    })

    years_realizacao, months_realizacao = get_years_and_months(transactions_renamed.DataRealizacao)
    years_aquisicao, months_aquisicao = get_years_and_months(transactions_renamed.DataAquisicao)

    n_inicial = 951
    n_linhas = list(range(n_inicial, n_inicial + len(transactions_renamed)))

    transactions_irs = transactions_renamed.assign(
        AnoRealizacao=years_realizacao,
        MesRealizacao=months_realizacao,
        AnoAquisicao=years_aquisicao,
        MesAquisicao=months_aquisicao,
        CodPais=country_code,
        NLinha=n_linhas
    )

    return transactions_irs[
        ["NLinha", "CodPais", "Codigo", "AnoRealizacao", "MesRealizacao", "ValorRealizacao", "AnoAquisicao",
         "MesAquisicao", "ValorAquisicao", "DespesasEncargos"]]


def get_elements_to_add_to_anexo_j_92(transactions_irs):
    elements_to_add = []

    for index, row in transactions_irs.iterrows():
        el = etree.Element("AnexoJq092AT01-Linha", numero=str(index + 1))

        for column_name in row.keys():
            sub_element = etree.SubElement(el, column_name)
            sub_element.text = str(row[column_name])

        elements_to_add.append(el)

    return elements_to_add


def add_transactions(irs_xml, transactions_irs):
    elements_to_add = get_elements_to_add_to_anexo_j_92(transactions_irs)
    quadro92anexo_j = irs_xml.xpath("//*[local-name()='AnexoJq092AT01']")[0]
    for el in elements_to_add:
        quadro92anexo_j.append(el)


def add_totals(irs_xml, transactions_irs):
    element_total_realizacao = irs_xml.xpath("//*[local-name()='AnexoJq092AT01SomaC01']")[0]
    element_total_realizacao.text = str(transactions_irs.ValorRealizacao.sum())
    element_total_aquisicao = irs_xml.xpath("//*[local-name()='AnexoJq092AT01SomaC02']")[0]
    element_total_aquisicao.text = str(transactions_irs.ValorAquisicao.sum())


def insert_foreign_gains(irs_xml_path, tao_finance_csv_path, output_xml_path, country_code):
    transactions = pd.read_csv(tao_finance_csv_path, header=1).drop(columns=['NIF', 'Lucro', 'Ticker'])
    transactions_irs = convert_to_irs_format(transactions, country_code)
    irs_xml = etree.parse(irs_xml_path).getroot()

    add_transactions(irs_xml, transactions_irs)
    add_totals(irs_xml, transactions_irs)

    with open(output_xml_path, 'wb') as f:
        f.write(etree.tostring(irs_xml, pretty_print=True))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('irs_xml', type=str, help='path to IRS xml file')
    parser.add_argument('tao_finance_csv', type=str, help='path to CSV file returning from TaoFinance script')
    parser.add_argument('output', type=str, help='output path to the resulting xml file')
    parser.add_argument('country_code', type=str, help='country code for the transactions (assumes transactions happened all in one country)')

    args = parser.parse_args()

    insert_foreign_gains(args.irs_xml, args.tao_finance_csv, args.output, args.country_code)
