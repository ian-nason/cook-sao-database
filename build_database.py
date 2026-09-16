#!/usr/bin/env python3
"""Build cook-sao.duckdb from the Cook County State's Attorney's Office felony case datasets.
Source: Cook County open-data portal (Socrata), five case-level tables covering felony cases
received 2011 through 2024-12-30 (the Office stopped maintaining the series on that date):
    intake        3k7z-hchi   one row per potential defendant brought in for felony review
    initiation    7mck-ehwz   one row per charge at case initiation (arraignment/bond)
    dispositions  apwk-dzx8   one row per charge disposition
    sentencing    tg8v-tm6u   one row per sentence on a disposed charge
    diversion     gpu3-5dfh   one row per diversion-program referral
Usage:
    ./download_data.sh && uv run python build_database.py [--output cook-sao.duckdb]
Column types come from the portal's own column metadata (docs/socrata_metadata.json):
calendar_date -> TIMESTAMP, or DATE when the portal exported the column without a time part; checkbox -> BOOLEAN,
number -> BIGINT or DOUBLE, text -> VARCHAR. Dates the portal exported outside 1900-2030 are
NULLed and counted (the raw text is kept in <col>_raw only when the rate exceeds 0.1%).
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

from datapond_build import Checker, build_columns_table, ensure_metadata, export_dictionary
from datapond_build.session import connect

RAW = Path("data/raw")
META = json.load(open(Path("docs/socrata_metadata.json")))
DEFAULT_OUTPUT = "cook-sao.duckdb"
TABLES = ["intake", "initiation", "dispositions", "sentencing", "diversion"]
SOURCE_URL = "https://datacatalog.cookcountyil.gov/browse?q=State%27s%20Attorney"

TABLE_DESCRIPTIONS = {
    "intake": "One row per potential defendant brought to the State's Attorney for felony review, 2011-2024: "
              "received date, offense category, felony-review result, arrest and incident dates, demographics, arresting agency",
    "initiation": "One row per charge on a case at initiation (after felony review approval), 2011-2024: charge statute/class, "
                  "initiation event and date, arraignment date, initial and current bond type/amount, demographics",
    "dispositions": "One row per charge disposition, 2011-2024: charged offense as disposed, disposition and reason, judge, court, "
                    "plus the case-level intake fields",
    "sentencing": "One row per sentence imposed on a disposed charge, 2011-2024: sentence type, commitment type/term/unit, sentence "
                  "judge and court, whether it is the current sentence, case length",
    "diversion": "One row per diversion-program referral, 2011-2024: program, referral date, primary charge, result, closed date",
}
JOIN_HINTS = {
    "case_id": "SAO case identifier; joins all five tables (one case can have several participants)",
    "case_participant_id": "Defendant within a case; joins all five tables",
    "charge_id": "Charge identifier; joins initiation, dispositions and sentencing",
    "charge_version_id": "Version of the charge (charges are amended); joins initiation, dispositions and sentencing",
    "received_date": "Date the case was received by the SAO (the series' time axis)",
}
DOUBLE_COLS = {"bond_amount_initial", "bond_amount_current"}
DATE_MIN, DATE_MAX = "1900-01-01", "2030-12-31"
DATE_AUDIT: dict[tuple[str, str], tuple[int, int]] = {}  # (table, col) -> (out of range or unparsed, non-blank)


def snake(name: str) -> str:
    return name.strip().lower().replace(" ", "_")


def load_table(con, t: str) -> int:
    path = RAW / f"{t}.csv"
    con.execute(f"CREATE OR REPLACE TABLE _raw AS SELECT * FROM read_csv('{path}', all_varchar=true, header=true, sample_size=-1)")
    header = [r[0] for r in con.execute("DESCRIBE _raw").fetchall()]
    # the CSV export is headed by the portal's display names (e.g. LAW_ENFORCEMENT_UNIT), whose
    # API field name can differ (unit); the display name, snake_cased, is the column name here
    types = {snake(c["name"]): c["type"] for c in META[t]["columns"]}
    unknown = [h for h in header if snake(h) not in types]
    if unknown:
        raise RuntimeError(f"{t}: columns not in portal metadata: {unknown}")
    missing = [f for f in types if f not in {snake(h) for h in header}]
    if missing:
        raise RuntimeError(f"{t}: portal columns missing from the CSV: {missing}")
    exprs = []
    for h in header:
        c, q = snake(h), f'"{h}"'
        clean = f"NULLIF(TRIM({q}), '')"
        ty = types[c]
        if ty == "calendar_date":
            # the portal exports either 'MM/DD/YYYY hh:mm:ss AM' or a bare 'MM/DD/YYYY' per column
            has_time = con.execute(f"SELECT COUNT(*) FROM _raw WHERE {clean} LIKE '%:%'").fetchone()[0] > 0
            ts = f"COALESCE(TRY_STRPTIME({clean}, '%m/%d/%Y %I:%M:%S %p'), TRY_STRPTIME({clean}, '%m/%d/%Y'))"
            cast = "" if has_time else "::DATE"
            exprs.append(f"(CASE WHEN {ts} BETWEEN '{DATE_MIN}' AND '{DATE_MAX}' THEN {ts} END){cast} AS {c}")
            bad, nn = con.execute(
                f"SELECT COUNT(*) FILTER (WHERE {clean} IS NOT NULL AND ({ts} IS NULL OR {ts} NOT BETWEEN '{DATE_MIN}' AND '{DATE_MAX}')), "
                f"COUNT({clean}) FROM _raw").fetchone()
            DATE_AUDIT[(t, c)] = (bad, nn)
            if nn and bad / nn > 0.001:
                exprs.append(f"{clean} AS {c}_raw")
        elif ty == "checkbox":
            exprs.append(f"CASE lower({clean}) WHEN 'true' THEN TRUE WHEN 'false' THEN FALSE END AS {c}")
        elif ty == "number":
            exprs.append(f"TRY_CAST({clean} AS {'DOUBLE' if c in DOUBLE_COLS else 'BIGINT'}) AS {c}")
        else:
            exprs.append(f"{clean} AS {c}")
    con.execute(f"CREATE OR REPLACE TABLE {t} AS SELECT {', '.join(exprs)} FROM _raw")
    con.execute("DROP TABLE _raw")
    return con.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]


def run_validation(con) -> int:
    ck = Checker("Validation")
    for t in TABLES:
        ck.query(con, f"{t} non-empty", f"SELECT COUNT(*) FROM {t}", lambda n: n > 10000, lambda n: f"{n:,} rows")
        ck.query(con, f"{t} received_date parsed (> 99.9%)", f"SELECT COUNT(received_date) * 1.0 / COUNT(*) FROM {t}",
                 lambda v: v > 0.999, lambda v: f"{v:.3%}")
        ck.query(con, f"{t} received_date within 2010-2024", f"SELECT MIN(received_date)::DATE, MAX(received_date)::DATE FROM {t}",
                 lambda r: str(r[0]) >= "2010-01-01" and str(r[1]) <= "2024-12-31", lambda r: f"{r[0]} .. {r[1]}")
        ck.query(con, f"{t} case_id and case_participant_id present", f"SELECT COUNT(*) FROM {t} WHERE case_id IS NULL OR case_participant_id IS NULL",
                 lambda n: n == 0, str)
    ck.query(con, "intake: one row per case participant", "SELECT COUNT(*) - COUNT(DISTINCT case_participant_id) FROM intake", lambda n: n == 0, str)
    ck.query(con, "initiation: (charge_id, charge_version_id) unique", "SELECT COUNT(*) - COUNT(DISTINCT (charge_id, charge_version_id)) FROM initiation",
             lambda n: n == 0, str)
    ck.query(con, "dispositions participants exist in intake (> 95%)",
             "SELECT COUNT(DISTINCT d.case_participant_id) FILTER (WHERE i.case_participant_id IS NOT NULL) * 1.0 / COUNT(DISTINCT d.case_participant_id) "
             "FROM dispositions d LEFT JOIN intake i USING (case_participant_id)", lambda v: v > 0.95, lambda v: f"{v:.1%}")
    ck.query(con, "sentencing rows join a disposition (> 99%)",
             "SELECT COUNT(*) FILTER (WHERE d.charge_id IS NOT NULL) * 1.0 / COUNT(*) FROM sentencing s "
             "LEFT JOIN (SELECT DISTINCT charge_id, charge_version_id FROM dispositions) d USING (charge_id, charge_version_id)",
             lambda v: v > 0.99, lambda v: f"{v:.2%}")
    ck.query(con, "sentencing: one current sentence per charge version at most",
             "SELECT COUNT(*) FROM (SELECT charge_id, charge_version_id FROM sentencing WHERE current_sentence GROUP BY 1, 2 HAVING COUNT(*) > 1)",
             lambda n: n == 0, str)
    ck.query(con, "bond amounts are DOUBLE", "SELECT data_type FROM information_schema.columns WHERE table_name = 'initiation' AND column_name = 'bond_amount_initial'",
             lambda s: s == "DOUBLE", str)
    for (t, c), (bad, nn) in sorted(DATE_AUDIT.items()):
        if nn:
            ck.check(f"{t}.{c}: unparsed/out-of-range dates < 1%", bad / nn < 0.01, f"{bad:,} of {nn:,}")
    return ck.report()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", type=Path, default=Path(DEFAULT_OUTPUT))
    a = ap.parse_args()
    t0 = time.time()
    con = connect(a.output, fresh=True, memory_limit="3GB", threads=2)
    counts = {}
    for t in TABLES:
        t1 = time.time()
        counts[t] = load_table(con, t)
        print(f"  {t}: {counts[t]:,} rows ({time.time() - t1:.0f}s)")
    for (t, c), (bad, nn) in sorted(DATE_AUDIT.items()):
        if bad:
            print(f"    {t}.{c}: {bad:,} of {nn:,} dates unparsed or outside {DATE_MIN[:4]}-{DATE_MAX[:4]} -> NULL")
    print("\nMetadata + dictionary")
    ensure_metadata(con, descriptions=TABLE_DESCRIPTIONS, tables=TABLES, source_url=SOURCE_URL, license="Public domain", replace=True)
    build_columns_table(con, join_hints=JOIN_HINTS, tables=TABLES)
    export_dictionary(con, Path("DICTIONARY.md"), title="cook-sao Data Dictionary",
                      intro=[f"Source: [Cook County State's Attorney's Office case-level datasets]({SOURCE_URL}) on the Cook County open-data portal, "
                             "felony cases received 2011 through 2024-12-30 (the series is closed).",
                             "Column definitions: `docs/CCSAO_Data_Glossary.pdf`; the case flow: `docs/CCSAO_Felony_Cases_Flowchart.pdf`.",
                             "Timestamps are the portal's; dates outside 1900-2030 are NULL."],
                      style="registry", tables=TABLES)
    con.execute("CHECKPOINT")
    failures = run_validation(con)
    con.close()
    print(f"\nBUILD DONE in {(time.time() - t0) / 60:.1f} min; " + ", ".join(f"{k} {v:,}" for k, v in counts.items())
          + f"; {a.output.stat().st_size / 1024**2:.0f} MB")
    if failures:
        print(f"BUILD FAILED: {failures} check(s) failed -- do not publish this file")
        sys.exit(1)


if __name__ == "__main__":
    main()
