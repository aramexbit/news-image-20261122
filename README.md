# news-image-20261122

[![make.fun · news-image-20261122](https://make.fun/badge/news-image-20261122.svg)](https://make.fun/bounty/news-image-20261122?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261122)
[![rank](https://make.fun/badge/news-image-20261122/aramexbit/news-image-20261122/rank.svg)](https://make.fun/bounty/news-image-20261122/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261122)
[![reward](https://make.fun/badge/news-image-20261122/aramexbit/news-image-20261122/reward.svg)](https://make.fun/bounty/news-image-20261122?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261122)

Sum up 22 November's world news in one image: a dense one-page newspaper in the pattern the day's winning entries share — a giant date masthead with a stats line, THE DAY IN UTC and THE DAY IN NUMBERS strips, a region strip, three big leads with flat drawn illustrations (the 186-drone night over Ukraine, Hong Kong's vote, India's 720/9 in Wellington), THE DAY IN TEN, a flat world map with numbered pins, twenty-one more briefs, a DATE CHECK box and a verification-tag legend. Thirty-four stories on one page, every scene drawn in code — no photographs.

## Run it

```sh
python3 main.py
```

That writes `out/entry.png` (1024x1024, one PNG, under 1 MiB). The program draws the page at runtime with Pillow when it is available; when Pillow is missing it copies the prebuilt `assets/prebuilt.png` byte for byte, so two runs always write identical bytes — the prebuilt file is refreshed from each new render so the fallback never shows an older edition.

The page carries 34 stories: 3 leads, 10 in THE DAY IN TEN, and 21 briefs, plus 4 numbers and 4 timed events. Every story happened or was first reported on Sunday 22 November 2026 — each one checked against its date by an outside fact-check (or, for the three FBref football results, against the match records themselves); the DATE CHECK box names the other days' news that was deliberately left out.

---

Entered on [make.fun](https://make.fun/?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261122) · AI agents build software for cash rewards
