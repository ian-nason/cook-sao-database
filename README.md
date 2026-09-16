# Cook County State's Attorney felony cases as a DuckDB database

Every felony case received by the Cook County (Chicago) State's Attorney's Office from
2011 until the Office closed the series on 2024-12-30, from its five case-level datasets on
the [Cook County open-data portal](https://datacatalog.cookcountyil.gov/browse?q=State%27s%20Attorney).
A local complement to the federal pipeline in
[fjc](https://github.com/ian-nason/fjc-database) and
[ussc](https://github.com/ian-nason/ussc-database): one large jurisdiction, prosecutor-side,
charge by charge.

| Table | One row per | Rows | Portal dataset |
|-------|-------------|-----:|----------------|
| `intake` | potential defendant brought in for felony review | 528,111 | [3k7z-hchi](https://datacatalog.cookcountyil.gov/d/3k7z-hchi) |
| `initiation` | charge at case initiation (statute, class, bond, arraignment) | 1,228,260 | [7mck-ehwz](https://datacatalog.cookcountyil.gov/d/7mck-ehwz) |
| `dispositions` | charge disposed (plea, verdict, dismissal, judge, court) | 1,080,014 | [apwk-dzx8](https://datacatalog.cookcountyil.gov/d/apwk-dzx8) |
| `sentencing` | sentence imposed on a disposed charge | 305,884 | [tg8v-tm6u](https://datacatalog.cookcountyil.gov/d/tg8v-tm6u) |
| `diversion` | diversion-program referral | 29,421 | [gpu3-5dfh](https://datacatalog.cookcountyil.gov/d/gpu3-5dfh) |

Keys: `case_id` (a case can have several participants), `case_participant_id` (the
defendant within a case, present in every table), `charge_id` + `charge_version_id`
(initiation, dispositions, sentencing). Row counts, columns and null rates: `DICTIONARY.md`.
Column definitions: `docs/CCSAO_Data_Glossary.pdf`; the case flow: `docs/CCSAO_Felony_Cases_Flowchart.pdf`.

## Quick start

```python
import datapond
con = datapond.connect("cook-sao")
con.sql("""
    SELECT EXTRACT(YEAR FROM received_date) AS year, felony_review_result, COUNT(*) AS n
    FROM intake GROUP BY 1, 2 ORDER BY 1, 3 DESC
""").show()
```

```sql
-- sentences on the primary charge, by offense category and sentence type
SELECT offense_category, sentence_type, COUNT(*) AS n
FROM sentencing
WHERE primary_charge_flag AND current_sentence_flag
GROUP BY 1, 2 ORDER BY 3 DESC LIMIT 20;
```

## How it was built

Each portal dataset is exported as CSV and loaded with the column types the portal itself
declares (`docs/socrata_metadata.json`): `calendar_date` becomes `TIMESTAMP`, or `DATE`
where the export carries no time part; `checkbox` becomes `BOOLEAN`; `number` becomes
`BIGINT` (bond amounts `DOUBLE`). Column names are the export's headers in snake_case
(`LAW_ENFORCEMENT_UNIT` -> `law_enforcement_unit`, `PRIMARY_CHARGE_FLAG` ->
`primary_charge_flag`). Dates outside 1900-2030 (a handful of 1883 incident dates) are
NULL and counted in the build log; when more than 0.1% of a column is affected the raw text
is kept in `<column>_raw`.

## Researcher caveats

- **The series is closed.** The Office stopped maintaining these datasets on 2024-12-30
  (cases received through November 2024 are present) and now publishes dashboards instead.
  Late-2024 cases are under-disposed simply because they had not concluded.
- **PROMIS conversion records.** Cases converted from the previous case-management system
  in 2011 carry placeholder values (`participant_status` / `law_enforcement_agency` =
  "PROMIS Conversion"); their dates before 2011 are the original incident dates.
- **Dispositions and sentencing reach back before 2011.** Those two tables hold every charge
  disposed or sentenced 2011-2024, including cases received as early as the 1980s (9.0% of
  disposition rows, 8.2% of sentencing rows); intake, initiation and diversion start with cases
  received in 2011, so pre-2011 cases have no intake row.
- **Co-defendants share `charge_id`.** A charge version is unique only together with
  `case_participant_id`; join on all three.
- **Rows are charges, not people.** `dispositions` and `sentencing` have one row per
  charge version; filter `primary_charge_flag` for a per-defendant view and
  `current_sentence_flag` for the sentence that stands (a charge can have several current
  rows, one per sentence component such as prison plus probation). `charge_version_id`
  increments when a charge is amended.
- **`received_date` is the time axis** the Office used in its own reports; `arrest_date`
  and the incident dates come from the arresting agency and can be years earlier.
- Demographics are as recorded by the Office; `age_at_incident` is at the incident date.

## Build

```bash
uv sync
./download_data.sh               # five CSVs (~1.3 GB) from the portal's export endpoint
uv run python build_database.py  # a few minutes, DuckDB capped at 3 GB
uv run python publish_to_hf.py --verify
```

## License

Code: MIT. Data: public domain (Cook County State's Attorney's Office, via the county portal).
