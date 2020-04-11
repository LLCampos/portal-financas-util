import pandas as pd
import argparse


def get_transactions(path):
    return pd.read_csv(path).drop(columns=['ISIN', 'Name', 'Exchange', 'Total(€)'])


def get_sell_transactions_for_year(transactions, year):
    sell_transactions = transactions[transactions.Type == "Sell"]
    return sell_transactions[sell_transactions.Date.str.contains(pat = str(year))]


def get_all_transactions_for_symbols_sold_in_year(transactions, year):
    sell_transactions = get_sell_transactions_for_year(transactions, year)
    return transactions[transactions.Symbol.isin(sell_transactions.Symbol)]


def convert_to_tao_finance_format(transactions):
    renamed_transactions = transactions.rename(columns={"Symbol": "Ticker", "Quantity": "Shares"})
    reordered_transactions = renamed_transactions[['Date', 'Ticker', 'Type', 'Shares', 'Price']]
    reordered_transactions.index.name = "#"
    return reordered_transactions.assign(Fees = 0)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('input', type=str, help='path to ETFMatic trade history csv')
    parser.add_argument('output', type=str, help='output path to csv in TaoFinance format')
    parser.add_argument('year', type=int, help='year for which to look for sell transactions')

    args = parser.parse_args()

    transactions = get_transactions(args.input)
    all_transactions_for_symbols_sold_in_year = get_all_transactions_for_symbols_sold_in_year(transactions, args.year)
    transactions_tao_format = convert_to_tao_finance_format(all_transactions_for_symbols_sold_in_year)
    transactions_tao_format.to_csv(args.output)
