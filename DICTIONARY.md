# cook-sao Data Dictionary

Source: [Cook County State's Attorney's Office case-level datasets](https://datacatalog.cookcountyil.gov/browse?q=State%27s%20Attorney) on the Cook County open-data portal, felony cases received 2011 through 2024-12-30 (the series is closed).
Column definitions: `docs/CCSAO_Data_Glossary.pdf`; the case flow: `docs/CCSAO_Felony_Cases_Flowchart.pdf`.
Timestamps are the portal's; dates outside 1900-2030 are NULL.

## intake

One row per potential defendant brought to the State's Attorney for felony review, 2011-2024: received date, offense category, felony-review result, arrest and incident dates, demographics, arresting agency

Rows: 528,111

| Column | Type | Nulls | Example | Join |
|--------|------|-------|---------|------|
| case_id | BIGINT | 0.0% | 189180541468 | SAO case identifier; joins all five tables (one case can have several participants) |
| case_participant_id | BIGINT | 0.0% | 1227866079959 | Defendant within a case; joins all five tables |
| received_date | DATE | 0.0% | 2011-01-01 | Date the case was received by the SAO (the series' time axis) |
| offense_category | VARCHAR | 0.0% | Aggravated Assault Police Officer |  |
| participant_status | VARCHAR | 5.6% | Approved |  |
| age_at_incident | BIGINT | 3.1% | 101 |  |
| race | VARCHAR | 3.8% | ASIAN |  |
| gender | VARCHAR | 3.2% | Female |  |
| incident_city | VARCHAR | 4.3% | Abbott Park |  |
| incident_begin_date | DATE | 2.2% | 1901-01-01 |  |
| incident_end_date | DATE | 92.3% | 1912-01-23 |  |
| law_enforcement_agency | VARCHAR | 0.7% | ADDISON PD |  |
| law_enforcement_unit | VARCHAR | 65.5% | District 1 - Central |  |
| arrest_date | TIMESTAMP | 10.3% | 1911-02-12 19:00:00 |  |
| felony_review_date | DATE | 38.8% | 1930-06-03 |  |
| felony_review_result | VARCHAR | 38.8% | Advice |  |
| update_offense_category | VARCHAR | 0.0% | Aggravated Assault Police Officer |  |

## initiation

One row per charge on a case at initiation (after felony review approval), 2011-2024: charge statute/class, initiation event and date, arraignment date, initial and current bond type/amount, demographics

Rows: 1,228,260

| Column | Type | Nulls | Example | Join |
|--------|------|-------|---------|------|
| case_id | BIGINT | 0.0% | 189180541468 | SAO case identifier; joins all five tables (one case can have several participants) |
| case_participant_id | BIGINT | 0.0% | 1227866079959 | Defendant within a case; joins all five tables |
| received_date | TIMESTAMP | 0.0% | 2011-01-01 00:00:00 | Date the case was received by the SAO (the series' time axis) |
| offense_category | VARCHAR | 0.0% | Aggravated Assault Police Officer |  |
| primary_charge_flag | BOOLEAN | 0.0% | false |  |
| charge_id | BIGINT | 0.0% | 13542736733571 | Charge identifier; joins initiation, dispositions and sentencing (co-defendants share it: key with case_participant_id) |
| charge_version_id | BIGINT | 0.0% | 154712873937 | Version of the charge (charges are amended); joins initiation, dispositions and sentencing |
| charge_offense_title | VARCHAR | 0.0% | 15<100 GRAMS LSD/ANALOG |  |
| charge_count | BIGINT | 0.0% | 1 |  |
| chapter | VARCHAR | 0.0% | 10 |  |
| act | VARCHAR | 0.0% | - |  |
| section | VARCHAR | 0.0% | (16-1(a)(2)(A)) |  |
| class | VARCHAR | 0.0% | 1 |  |
| aoic | VARCHAR | 0.0% | 0000001606 |  |
| event | VARCHAR | 9.0% | Grand Jury |  |
| event_date | TIMESTAMP | 9.0% | 2005-07-15 09:00:00 |  |
| finding_no_probable_cause | BIGINT | 96.6% | 1 |  |
| arraignment_date | TIMESTAMP | 14.0% | 1931-03-30 00:00:00 |  |
| bond_date_initial | TIMESTAMP | 34.1% | 1900-01-01 00:00:00 |  |
| bond_date_current | TIMESTAMP | 34.1% | 1930-01-30 00:00:00 |  |
| bond_type_initial | VARCHAR | 34.1% | C Bond |  |
| bond_type_current | VARCHAR | 34.1% | C Bond |  |
| bond_amount_initial | DOUBLE | 39.8% | 0.0 |  |
| bond_amount_current | DOUBLE | 39.6% | 0.0 |  |
| bond_electronic_monitor_flag_initial | BOOLEAN | 95.9% | true |  |
| bond_electroinic_monitor_flag_current | BOOLEAN | 95.7% | true |  |
| age_at_incident | BIGINT | 2.2% | 101 |  |
| race | VARCHAR | 0.9% | ASIAN |  |
| gender | VARCHAR | 0.7% | Female |  |
| incident_city | VARCHAR | 4.0% | Abbott Park |  |
| incident_begin_date | TIMESTAMP | 1.6% | 1912-01-23 00:00:00 |  |
| incident_end_date | TIMESTAMP | 90.0% | 1912-01-23 00:00:00 |  |
| law_enforcement_agency | VARCHAR | 0.5% | ALSIP PD |  |
| law_enforcement_unit | VARCHAR | 74.0% | District 1 - Central |  |
| arrest_date | TIMESTAMP | 4.3% | 1915-04-04 17:45:00 |  |
| felony_review_date | TIMESTAMP | 24.5% | 1930-06-03 00:00:00 |  |
| felony_review_result | VARCHAR | 24.5% | Advice |  |
| updated_offense_category | VARCHAR | 0.0% | Aggravated Assault Police Officer |  |

## dispositions

One row per charge disposition, 2011-2024: charged offense as disposed, disposition and reason, judge, court, plus the case-level intake fields

Rows: 1,080,014

| Column | Type | Nulls | Example | Join |
|--------|------|-------|---------|------|
| case_id | BIGINT | 0.0% | 130011887122 | SAO case identifier; joins all five tables (one case can have several participants) |
| case_participant_id | BIGINT | 0.0% | 1000697225279 | Defendant within a case; joins all five tables |
| received_date | TIMESTAMP | 0.0% | 1901-07-24 00:00:00 | Date the case was received by the SAO (the series' time axis) |
| offense_category | VARCHAR | 0.0% | Aggravated Assault Police Officer |  |
| primary_charge_flag | BOOLEAN | 0.0% | false |  |
| charge_id | BIGINT | 0.0% | 10003165162773 | Charge identifier; joins initiation, dispositions and sentencing (co-defendants share it: key with case_participant_id) |
| charge_version_id | BIGINT | 0.0% | 100004789052 | Version of the charge (charges are amended); joins initiation, dispositions and sentencing |
| disposition_charged_offense_title | VARCHAR | 0.0% | 15<100 GRAMS METH/ANALOG |  |
| charge_count | BIGINT | 0.0% | 1 |  |
| disposition_date | TIMESTAMP | 0.0% | 2011-01-03 00:00:00 |  |
| disposition_charged_chapter | VARCHAR | 0.0% | 0515 |  |
| disposition_charged_act | VARCHAR | 2.3% | - |  |
| disposition_charged_section | VARCHAR | 2.3% | (8-4)6-302(a)(3) |  |
| disposition_charged_class | VARCHAR | 0.0% | 1 |  |
| disposition_charged_aoic | VARCHAR | 0.0% | 0000000705 |  |
| charge_disposition | VARCHAR | 0.0% | BFW |  |
| charge_disposition_reason | VARCHAR | 73.3% | AONIC GJ |  |
| judge | VARCHAR | 7.1% | Adam Donald Bourgeois |  |
| disposition_court_name | VARCHAR | 0.5% | District 1 - Chicago |  |
| disposition_court_facility | VARCHAR | 1.1% | 26TH Street |  |
| age_at_incident | BIGINT | 1.8% | 101 |  |
| race | VARCHAR | 0.6% | ASIAN |  |
| gender | VARCHAR | 0.4% | Female |  |
| incident_city | VARCHAR | 8.1% | Addison |  |
| incident_begin_date | DATE | 1.2% | 1912-01-23 |  |
| incident_end_date | TIMESTAMP | 89.5% | 1912-01-23 00:00:00 |  |
| law_enforcement_agency | VARCHAR | 0.1% | ADULT TRANSITION CNT |  |
| law_enforcement_unit | VARCHAR | 74.6% | District 1 - Central |  |
| arrest_date | TIMESTAMP | 2.4% | 1915-04-04 17:45:00 |  |
| felony_review_date | TIMESTAMP | 22.7% | 1900-01-01 00:00:00 |  |
| felony_review_result | VARCHAR | 22.7% | Advice |  |
| arraignment_date | TIMESTAMP | 12.6% | 1931-03-30 00:00:00 |  |
| updated_offense_category | VARCHAR | 0.0% | Aggravated Assault Police Officer |  |

## sentencing

One row per sentence imposed on a disposed charge, 2011-2024: sentence type, commitment type/term/unit, sentence judge and court, whether it is the current sentence, case length

Rows: 305,884

| Column | Type | Nulls | Example | Join |
|--------|------|-------|---------|------|
| case_id | BIGINT | 0.0% | 130011887122 | SAO case identifier; joins all five tables (one case can have several participants) |
| case_participant_id | BIGINT | 0.0% | 1001860678031 | Defendant within a case; joins all five tables |
| received_date | TIMESTAMP | 0.0% | 1901-07-24 00:00:00 | Date the case was received by the SAO (the series' time axis) |
| offense_category | VARCHAR | 0.0% | Aggravated Assault Police Officer |  |
| primary_charge_flag | BOOLEAN | 0.0% | false |  |
| charge_id | BIGINT | 0.0% | 10006480542508 | Charge identifier; joins initiation, dispositions and sentencing (co-defendants share it: key with case_participant_id) |
| charge_version_id | BIGINT | 0.0% | 100014309850 | Version of the charge (charges are amended); joins initiation, dispositions and sentencing |
| disposition_charged_offense_title | VARCHAR | 0.0% | 2ND DEGREE MURDER |  |
| charge_count | BIGINT | 0.0% | 1 |  |
| disposition_date | TIMESTAMP | 0.0% | 2011-01-03 00:00:00 |  |
| disposition_charged_chapter | VARCHAR | 0.0% | 10 |  |
| disposition_charged_act | VARCHAR | 1.8% | - |  |
| disposition_charged_section | VARCHAR | 1.8% | (8-4)6-302(a)(3) |  |
| disposition_charged_class | VARCHAR | 0.0% | 1 |  |
| disposition_charged_aoic | VARCHAR | 0.0% | 0000001547 |  |
| charge_disposition | VARCHAR | 0.0% | BFW |  |
| charge_disposition_reason | VARCHAR | 99.6% | Adjudicated Minor |  |
| sentence_judge | VARCHAR | 0.2% | Abishi C Cunningham |  |
| sentence_court_name | VARCHAR | 0.5% | District 1 - Chicago |  |
| sentence_court_facility | VARCHAR | 0.8% | 26TH Street |  |
| sentence_phase | VARCHAR | 0.0% | Amended/Corrected Sentencing |  |
| sentence_date | TIMESTAMP | 0.0% | 1930-06-30 00:00:00 |  |
| sentence_type | VARCHAR | 0.0% | 2nd Chance Probation |  |
| current_sentence_flag | BOOLEAN | 0.0% | false |  |
| commitment_type | VARCHAR | 0.6% | 2nd Chance Probation |  |
| commitment_term | VARCHAR | 0.6% | 0 |  |
| commitment_unit | VARCHAR | 0.6% | Days |  |
| length_of_case_in_days | BIGINT | 6.5% | -1 |  |
| age_at_incident | BIGINT | 1.5% | 101 |  |
| race | VARCHAR | 0.5% | ASIAN |  |
| gender | VARCHAR | 0.3% | Female |  |
| incident_city | VARCHAR | 7.2% | Addison |  |
| incident_begin_date | TIMESTAMP | 1.2% | 1912-01-23 00:00:00 |  |
| incident_end_date | TIMESTAMP | 91.5% | 1912-01-23 00:00:00 |  |
| law_enforcement_agency | VARCHAR | 0.1% | ALSIP PD |  |
| law_enforcement_unit | VARCHAR | 71.4% | District 1 - Central |  |
| arrest_date | TIMESTAMP | 2.2% | 1915-04-04 17:45:00 |  |
| felony_review_date | TIMESTAMP | 28.1% | 1930-06-03 00:00:00 |  |
| felony_review_result | VARCHAR | 28.1% | Advice |  |
| arraignment_date | TIMESTAMP | 6.5% | 1931-03-30 00:00:00 |  |
| updated_offense_category | VARCHAR | 0.0% | Aggravated Assault Police Officer |  |

## diversion

One row per diversion-program referral, 2011-2024: program, referral date, primary charge, result, closed date

Rows: 29,421

| Column | Type | Nulls | Example | Join |
|--------|------|-------|---------|------|
| case_id | BIGINT | 0.0% | 332199991559 | SAO case identifier; joins all five tables (one case can have several participants) |
| case_participant_id | BIGINT | 0.0% | 4168444757860 | Defendant within a case; joins all five tables |
| received_date | TIMESTAMP | 0.0% | 2011-01-01 00:00:00 | Date the case was received by the SAO (the series' time axis) |
| offense_category | VARCHAR | 0.0% | Aggravated Assault Police Officer |  |
| diversion_program | VARCHAR | 0.0% | ACT |  |
| referral_date | TIMESTAMP | 0.0% | 1932-04-21 00:00:00 |  |
| diversion_count | BIGINT | 0.0% | 1 |  |
| primary_charge_offense_title | VARCHAR | 0.0% | 15<100 GRAMS LSD/ANALOG |  |
| statute | VARCHAR | 0.0% | 15 ILCS 335/14A(b)(1) |  |
| race | VARCHAR | 0.0% | Asian |  |
| gender | VARCHAR | 0.0% | Female |  |
| diversion_result | VARCHAR | 28.0% | Failed |  |
| diversion_closed_date | TIMESTAMP | 28.0% | 2010-12-28 00:00:00 |  |
