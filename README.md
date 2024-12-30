# actual-parser

A simple parser for [Saison Card][saison] and [SMBC][smbc] credit card statements,
to easily import them into [Actual][actual].

## Usage
To use this script, download a CSV file from one of the supported sites, and run the following:
```bash
./actual-parser.py my-statement.csv
```

The output will be in CSV format, which can be [imported][import] into Actual:
```csv
"Date","Payee","Notes","Category","Amount"
"2024-12-01","GitHub","Sponsors","Donations","-500"
"2024-12-02","Open Collective","Actual","Donations","-1000"
```

## Configuration
Transactions can be transformed using the mapping files under the `data` directory.
All files are simple JSON mappings between the payee name and the target value.

Once the transaction is identified using exact or prefix matching on the payee name,
the desired field is replaced using the target value.

For example, the `payee.json` file can contain the following object:
```json
{
    "GITHUB": "GitHub"
}
```

In this case, the **payee** field of any transaction with the payee `GITHUB` or `GITHUB.COM`
will be changed to `GitHub`.

The same works for the `notes.json` file:
```json
{
    "GOOGLE*GSUITE": "G Suite"
}
```

In this case, the **notes** field of any transaction with the payee `GOOGLE*GSUITE`
will be changed to `G Suite`.

## Notes
To avoid committing changes to the `data` directory, run the following:
```bash
git update-index --skip-worktree data/*.json
```

[saison]: https://www.saisoncard.co.jp
[smbc]: https://www.smbc-card.com
[actual]: https://actualbudget.org
[import]: https://actualbudget.org/docs/transactions/importing
