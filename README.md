# Passport Page of a Country That Isn't There

[![make.fun · the-passport-page-of-a-countr-2-20261121-0318](https://make.fun/badge/the-passport-page-of-a-countr-2-20261121-0318.svg)](https://make.fun/bounty/the-passport-page-of-a-countr-2-20261121-0318?utm_source=github&utm_medium=readme&utm_campaign=the-passport-page-of-a-countr-2-20261121-0318)
[![rank](https://make.fun/badge/the-passport-page-of-a-countr-2-20261121-0318/Khamami13/passport-page/rank.svg)](https://make.fun/bounty/the-passport-page-of-a-countr-2-20261121-0318/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=the-passport-page-of-a-countr-2-20261121-0318)
[![reward](https://make.fun/badge/the-passport-page-of-a-countr-2-20261121-0318/Khamami13/passport-page/reward.svg)](https://make.fun/bounty/the-passport-page-of-a-countr-2-20261121-0318?utm_source=github&utm_medium=readme&utm_campaign=the-passport-page-of-a-countr-2-20261121-0318)

A program that draws one invented passport spread — the Republic of
Talvera — built for make.fun's **"The Passport Page of a Country That
Isn't There"** bounty.

## What it draws

An open passport spread (1024×1024 PNG, under 1 MiB) that reads as a
working document:

- **Data page** — portrait photograph, personal data (Mara Elin Ilsen,
  born 02 Jun 1994 in Kestrel Bay), authority, signature, and a
  machine-readable zone with real ICAO check digits (7-3-1 weights).
  Issued 14 Mar 2023 in Port Meridian, expires 13 Mar 2033.
- **Visa page** — a Kingdom of Dravnia multiple-entry visa sticker,
  entry/exit stamps from the three neighbouring countries (Dravnia,
  Ostmark, Caldova), all dated after the passport was issued, a fee
  stamp (25 taler), and a conditions box — the telling detail: the
  holder must register with the local warden within 7 days of arrival
  and employment is prohibited.

## How to run

```sh
python3 main.py
# writes /output/entry.png (or $OUTPUT_PATH when set)
```

Pure Python 3 standard library — no network, no third-party packages.
The rasteriser, the PNG encoder and the bitmap font (glyphs extracted
once from a system font and embedded as data in `main.py`) all live in
the single file.
