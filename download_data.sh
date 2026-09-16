#!/usr/bin/env bash
# Cook County State's Attorney's Office felony case-level datasets (Socrata open-data portal).
# https://datacatalog.cookcountyil.gov/browse?q=State%27s%20Attorney  (current series, 2011-present)
set -uo pipefail
cd "$(dirname "$0")"
mkdir -p data/raw
failed=0
declare -A IDS=([intake]=3k7z-hchi [initiation]=7mck-ehwz [dispositions]=apwk-dzx8 [sentencing]=tg8v-tm6u [diversion]=gpu3-5dfh)
for t in intake initiation dispositions sentencing diversion; do
  id=${IDS[$t]}; f="data/raw/$t.csv"
  [[ -s "$f" ]] && { echo "have $f"; continue; }
  curl --fail -L --retry 5 --retry-delay 15 -sS -A "Mozilla/5.0 (datapond-maintenance)" -o "$f.part" \
    "https://datacatalog.cookcountyil.gov/api/views/$id/rows.csv?accessType=DOWNLOAD" \
    && mv "$f.part" "$f" && echo "ok $f $(stat -c %s "$f") bytes $(wc -l < "$f") lines" || { rm -f "$f.part"; echo "FAIL $f" >&2; failed=$((failed + 1)); }
done
if [[ $failed -gt 0 ]]; then echo "$failed download(s) failed" >&2; exit 1; fi
