<a id="cook-county-states-attorney-felony-cases-as-a-duckdb-database"></a>

# Cook County State's Attorney Felony Case Database

Cook County (Chicago) State’s Attorney’s Office prosecutor records covering felony review, charges, dispositions, sentencing and diversion. A disposition is how a charge was resolved; diversion records describe referrals to diversion programs. The office closed this series on December 30, 2024. Intake starts with cases received in 2011; disposition and sentencing records also include older cases resolved during 2011–2024. Tables have different units, including defendants presented for review, charge versions and sentence components, so do not add their row counts as unique cases or people.

<a id="quick-start"></a>

## Start querying

Preview up to five felony-review intake records received in 2024, showing the received date, offense category and recorded review result. A review record is not a unique defendant or case count.

Choose R or Python. Install the datapond package once: use `install.packages("datapond")` in R, or run `python -m pip install datapond` in a terminal.

### R

```r
library(datapond)
con <- dp_connect("cook-sao")
tryCatch({
  DBI::dbExecute(con, "SET threads=1")
  DBI::dbExecute(con, "SET memory_limit='128MiB'")
  DBI::dbExecute(con, "SET max_temp_directory_size='0B'")
  print(DBI::dbGetQuery(con, "SELECT received_date,offense_category,felony_review_result FROM intake WHERE received_date>=DATE '2024-01-01' LIMIT 5"))
}, finally = dp_disconnect(con))
```

### Python

```python
import datapond
con = datapond.connect('cook-sao')
try:
    con.execute("SET threads=1")
    con.execute("SET memory_limit='128MiB'")
    con.execute("SET max_temp_directory_size='0B'")
    print(con.execute("""SELECT received_date,offense_category,felony_review_result FROM intake WHERE received_date>=DATE '2024-01-01' LIMIT 5""").fetchall())
finally:
    con.close()
```

Queries run on your computer and read the byte ranges they need. A small result can still require a large scan. These examples limit DuckDB to one thread and a 128 MiB buffer pool with disk spill disabled; that is not a limit on the entire R or Python process. Larger analyses may need more memory or a local download with enough disk space.

<a id="additional-dataset-notes"></a>

<a id="coverage-fields-and-sources"></a>

## Tables and case stages

| Table | One row per | Rows | Portal dataset |
|-------|-------------|-----:|----------------|
| `intake` | potential defendant brought in for felony review | 528,111 | [3k7z-hchi](https://datacatalog.cookcountyil.gov/d/3k7z-hchi) |
| `initiation` | charge at case initiation (statute, class, bond, arraignment) | 1,228,260 | [7mck-ehwz](https://datacatalog.cookcountyil.gov/d/7mck-ehwz) |
| `dispositions` | charge disposed (plea, verdict, dismissal, judge, court) | 1,080,014 | [apwk-dzx8](https://datacatalog.cookcountyil.gov/d/apwk-dzx8) |
| `sentencing` | sentence component imposed on a disposed charge | 305,884 | [tg8v-tm6u](https://datacatalog.cookcountyil.gov/d/tg8v-tm6u) |
| `diversion` | diversion-program referral | 29,421 | [gpu3-5dfh](https://datacatalog.cookcountyil.gov/d/gpu3-5dfh) |

Keys: `case_id` (a case can have several participants), `case_participant_id` (the
defendant within a case, present in every table), `charge_id` + `charge_version_id`
(initiation, dispositions, sentencing). A charge-level join requires `case_participant_id`, `charge_id` and `charge_version_id` together because co-defendants can share a charge ID. `charge_version_id` increments when a charge is amended. Row counts, columns and null rates: `DICTIONARY.md`.
Column definitions: `docs/CCSAO_Data_Glossary.pdf`; the case flow: `docs/CCSAO_Felony_Cases_Flowchart.pdf`.

A charge may have several current sentence components, such as prison plus probation. Count those rows as components, not additional people.

See the [data dictionary](https://github.com/ian-nason/cook-sao-database/blob/main/DICTIONARY.md) for column definitions.

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
- **Rows describe charges and sentence components, not people.** `dispositions`
  describes charge versions; `sentencing` can have several rows per charge version,
  one per component such as prison plus probation. Filter `primary_charge_flag` to
  focus on the primary charge and `current_sentence_flag` for the sentence that
  stands; several current components can remain for one defendant.
- **`received_date` is the time axis** the Office used in its own reports; `arrest_date`
  and the incident dates come from the arresting agency and can be years earlier.
- Demographics are as recorded by the Office; `age_at_incident` is at the incident date.
- **Placeholder dates survive.** Only dates outside 1900-2030 are NULLed; the portal also
  carries in-range placeholders (`incident_begin_date` 1901-01-01, `felony_review_date`
  in the 1930s, `age_at_incident` above 100). Bound any date arithmetic to 2000+. If more than 0.1% of a date column is affected by out-of-range dates, the original values are retained in `<column>_raw`.

<a id="advanced-access-quick-start"></a>

## More example queries

Count intake review records by received year and review result:

```python
import datapond
con = datapond.connect("cook-sao")
con.sql("""
    SELECT EXTRACT(YEAR FROM received_date) AS year, felony_review_result, COUNT(*) AS n
    FROM intake GROUP BY 1, 2 ORDER BY 1, 3 DESC
""").show()
```

Count current sentence components on the primary charge by offense category and sentence type. The filters do not make this a unique-person count: one charge can have both prison and probation components.

```sql
-- sentences on the primary charge, by offense category and sentence type
SELECT offense_category, sentence_type, COUNT(*) AS n
FROM sentencing
WHERE primary_charge_flag AND current_sentence_flag
GROUP BY 1, 2 ORDER BY 3 DESC LIMIT 20;
```

## Sources and maintenance

### Sources and related datasets

Source: [Cook County State's Attorney's Office (county open-data portal)](https://datacatalog.cookcountyil.gov/browse?q=State%27s%20Attorney). License: Public domain.

The office published the five case-level datasets on the [Cook County open-data portal](https://datacatalog.cookcountyil.gov/browse?q=State%27s%20Attorney). A local complement to the federal pipeline in
[fjc](https://github.com/ian-nason/fjc-database) and
[ussc](https://github.com/ian-nason/ussc-database): one large jurisdiction, prosecutor-side,
charge by charge.

### How it was built

Each portal dataset is exported as CSV and loaded with the column types the portal itself
declares (`docs/socrata_metadata.json`): `calendar_date` becomes `TIMESTAMP`, or `DATE`
where the export carries no time part; `checkbox` becomes `BOOLEAN`; `number` becomes
`BIGINT` (bond amounts `DOUBLE`). Column names are the export's headers in snake_case
(`LAW_ENFORCEMENT_UNIT` -> `law_enforcement_unit`, `PRIMARY_CHARGE_FLAG` ->
`primary_charge_flag`). Dates outside 1900-2030 (a handful of 1883 incident dates) are
NULL and counted in the build log; when more than 0.1% of a column is affected the raw text
is kept in `<column>_raw`.

### Build

```bash
uv sync
./download_data.sh               # five CSVs (~1.3 GB) from the portal's export endpoint
uv run python build_database.py  # a few minutes, DuckDB capped at 3 GB
uv run python publish_to_hf.py --verify
```

### License

Code: MIT. Data: public domain (Cook County State's Attorney's Office, via the county portal).
