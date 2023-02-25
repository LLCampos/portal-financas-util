#!/usr/bin/env python3

import pandas as pd
import argparse


def get_transactions(path):
    return pd.read_csv(path).drop(columns=['ISIN', 'Name', 'Exchange'])


def get_sell_transactions_for_year(transactions, year):
    sell_transactions = transactions[transactions.Type == "Sell"]
    return sell_transactions[sell_transactions.Date.str.contains(pat=str(year))]


def get_all_transactions_for_symbols_sold_in_year(transactions, year):
    sell_transactions = get_sell_transactions_for_year(transactions, year)
    return transactions[transactions.Symbol.isin(sell_transactions.Symbol)]


def convert_to_onefinance_format(transactions):
    renamed_transactions = transactions.rename(
        columns={"Symbol": "Ticker", "Quantity": "Shares", "Price": "PriceBase", "Total(€)": "Total"})
    reordered_transactions = renamed_transactions[['Date', 'Ticker', 'Type', 'Shares', 'PriceBase', 'Total']]
    reordered_transactions.insert(0, "Broker", "ETFMATIC.GB")
    return reordered_transactions.assign(Fees=0)


if __name__ == "__main__":
    description = """Converts ETFMatic trade history .csv file to the format accepted by OneFinance 
    (https://onefinance.pt/my/transactions/gsheets-import)"""

    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('input', type=str, help='path to ETFMatic trade history csv')
    parser.add_argument('output', type=str, help='output path to csv in OneFinance format')

    args = parser.parse_args()

    transactions = get_transactions(args.input)
    transactions_tao_format = convert_to_onefinance_format(transactions)
    transactions_tao_format.to_csv(args.output, index=False)
