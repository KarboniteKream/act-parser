#!/usr/bin/env python3

import csv
import datetime
import json
import os
import sys


def load_data(name):
    base = os.path.dirname(__file__)
    path = f"data/{name}.json"

    with open(os.path.join(base, path)) as file:
        return json.load(file)


def find_entry(data, payee):
    if payee in data:
        return data[payee]

    for prefix, value in data.items():
        if payee.startswith(prefix):
            return value

    return None


def get_payee(payee):
    entry = find_entry(PAYEE, payee)
    return entry or payee


def get_notes(payee, notes):
    if entry := find_entry(NOTES, payee):
        return entry

    # We don't care about these, we're already paying in JPY.
    if ".00 JPY" in notes:
        return ""

    return notes.removeprefix("現地通貨額:")


def get_category(payee):
    entry = find_entry(CATEGORY, payee)
    return entry or ""


def format_row(date, payee, notes, amount):
    date = datetime.datetime.strptime(date, "%Y/%m/%d").strftime("%Y-%m-%d")
    notes = get_notes(payee, notes)
    category = get_category(payee)
    payee = get_payee(payee)
    amount = f"{-float(amount):g}"

    return [date, payee, notes, category, amount]


def handle_saison(row):
    date, payee, _, _, _, amount, notes, *_ = row

    # Ignore rows with notes.
    if date == "":
        return None

    return format_row(date, payee, notes, amount)


def handle_smbc_current(row):
    date, payee, _, _, _, _, amount, *_ = row
    return format_row(date, payee, "", amount)


def handle_smbc_finalized(row):
    date, payee, _, _, _, amount, *_ = row
    return format_row(date, payee, "", amount)


if len(sys.argv) < 2:
    print(f"Usage: {sys.argv[0]} <CSV-FILE>")
    exit(1)

csv_file = sys.argv[1]

PAYEE = load_data("payee")
NOTES = load_data("notes")
CATEGORY = load_data("category")

# Readable with: iconv -f Shift-JIS -t UTF-8 <file>
with open(csv_file, newline="", encoding="shift_jis") as file:
    rows = list(csv.reader(file, delimiter=","))

    if len(rows) == 0:
        print("ERROR: No data in file!")
        sys.exit(1)

    if rows[0] == ["カード名称", "ＪＱ　ＣＡＲＤセゾン"]:
        # Remove headers.
        rows = rows[5:]
        handler = handle_saison
    else:  # SMBC.
        if "**-****-****" in rows[0][1]:
            # Remove account names.
            rows = list(filter(lambda row: len(row) > 3, rows))
            # Remove row with month total.
            rows = rows[:-1]
            handler = handle_smbc_finalized
        else:
            handler = handle_smbc_current

    output = filter(lambda row: row is not None, map(handler, rows))
    output = sorted(output, key=lambda row: row[0])

    print("Date,Payee,Notes,Category,Amount")
    for row in output:
        print(",".join(row))
