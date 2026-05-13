# Member Link Checklist — making your E3 profile findable on Google

**Audience:** every E3 lab member (current and graduated) with a profile page on `e3center.caece.net`.
**Reading time:** 5 minutes. **Action time:** 10–15 minutes per platform.
**Why this exists:** as of 2026-05-13, only 5 of 28 member pages have been indexed by Google. The diagnosed cause is *no external links pointing to most member pages*. One or two solid inbound links per member is usually enough to move a page from "Crawled – currently not indexed" to "Indexed". See [`../analysis/2026-05-13_3mo-insights.md`](../analysis/2026-05-13_3mo-insights.md) §9 for the full diagnosis.

---

## For the lab admin (read first, then hand the rest to members)

**What this is.** A bilingual-ish (English instructions, Chinese where needed) checklist members can follow on their own time to add their E3 profile URL to high-authority external sites. Each external link gives Google a reason to index that member's page.

**Rollout suggestion.** Send the §"For each member" section by email or post in the lab Slack with each member's URL prefilled (lookup table at the bottom). Set a 2-week deadline. Track completions in a shared sheet.

**Expected outcome.** Indexing typically follows the inbound link by 2–6 weeks. If you re-run a GSC export 3 months from now, the indexed-URL count should move from 5 → 15+ if half the lab completes Tier 1.

**Don't do this for.**
- Members on leave or who have asked to be excluded from the public roster.
- Anyone who has explicitly asked for a low online profile (privacy preference trumps SEO).

---

## For each member: the checklist

### Step 0 — find your E3 URL

Your unique URL is at the bottom of this document in the lookup table. It looks like:

```
https://e3center.caece.net/members/<your-id>/
```

Copy that URL once. You'll paste it into every platform below.

### Tier 1 — highest leverage (5 minutes; do these even if you do nothing else)

Add your E3 URL as a website / homepage link on these two profiles. Both are high-authority academic platforms that Google trusts deeply, and one inbound link from either is usually enough to unlock indexing.

#### 1. ORCID
*Why first: ORCID is the canonical identity registry for researchers. Google weights ORCID-originating links highly.*

1. Go to [orcid.org](https://orcid.org) and sign in.
2. Profile (top right) → **Websites & Social Links** section → click the pencil to edit.
3. Click **Add another**.
4. Fill in:
   - **Description:** `E3 Center, NTU`
   - **URL:** *your E3 URL*
5. Set visibility to **Everyone** (otherwise Google can't see it).
6. Save.

If you don't have an ORCID yet, register at [orcid.org/register](https://orcid.org/register) — it's free, takes 2 minutes, and is required for most journal submissions anyway.

#### 2. Google Scholar
*Why second: Scholar profiles are the most-clicked academic search result type. The "Homepage" link there is a direct Googlebot-followable backlink.*

1. Go to [scholar.google.com](https://scholar.google.com) and sign in.
2. Click your profile name → **Edit** (pencil icon next to your name).
3. In the **Homepage** field, paste *your E3 URL*.
4. Save.

If you don't have a Scholar profile yet, create one at [scholar.google.com](https://scholar.google.com) → "My profile". It's free and indexed almost immediately.

### Tier 2 — solid (5 minutes; do these too if you can)

#### 3. LinkedIn
1. Profile → **Edit intro** (pencil under your name) → **Contact info**.
2. **Websites** → **Add website**.
3. **Type:** `Personal` (or `Company` if you prefer).
4. **URL:** *your E3 URL*.
5. Save.

#### 4. ResearchGate
1. Profile → **Info** → **About** → **External links**.
2. **Add link** → paste *your E3 URL*.
3. Save.

### Tier 3 — institutional links (10 minutes; one-time email)

#### 5. NTU department / advisor's lab page

If your home department (Civil Engineering, Chemical Engineering, etc.) maintains a student roster page, email the department admin and ask them to add a link from your name to your E3 URL. Sample text in English and Chinese below — copy, fill in the brackets, send.

> *English:*
> Hi [admin name], could you add a link from my name on the department student roster to my E3 Center profile? The URL is [your E3 URL]. This is part of an SEO effort to make student research pages discoverable on Google. Thank you!

> *中文：*
> 您好，可否在系上的學生名單頁面，將我的名字連結到我的 E3 Center 個人頁面？網址是 [your E3 URL]。這是為了讓學生研究頁面在 Google 搜尋中可見。謝謝！

If your advisor (Prof. Hsieh) has a personal homepage or research-group landing page outside `e3center.caece.net`, ask that it link to your member URL as well.

### Tier 4 — optional, nice-to-have

These don't create Google-crawlable backlinks but drive direct traffic and reinforce the URL across the web:

- **Email signature.** Add `My E3 profile: <your E3 URL>` below your name.
- **Conference slides.** Include the URL in the footer of your title slide.
- **Twitter/X / Bluesky bio.** Many academics list their lab profile URL here.
- **Personal website.** If you have one, add an "Affiliations" section linking to your E3 page.

### Step N — verify it worked (do this 2–3 weeks later)

1. Open a private/incognito browser window.
2. Search Google for either of:
   ```
   site:e3center.caece.net "<your full English name>"
   site:e3center.caece.net "<your Chinese name>"
   ```
3. If your member page appears in the results → you are indexed. Done.
4. If nothing appears → check Search Console URL Inspection (ask the lab admin) to see if status has changed from "Crawled – not indexed" to "Indexed", or to a different state that needs follow-up.

**Don't worry if it takes a month.** Google's indexing decisions are deliberately slow. The signal you sent by adding the ORCID/Scholar link doesn't reach the index in real-time — it propagates through Google's crawl of those source platforms, which can take 1–4 weeks.

---

## Member URL lookup table

Find your row. Copy the URL in column 3. Use it everywhere above.

| Chinese name | English name (nickname) | Your E3 URL | Year |
|---|---|---|---|
| 謝依芸 | I-Yun Lisa Hsieh | `https://e3center.caece.net/members/iyunlisahsieh/` | — |
| 譚竣文 | Jason (Chon Man Tam) | `https://e3center.caece.net/members/chonmantam/` | '21 |
| 薛丞翔 | Sean (Cheng-Hsiang Shei) | `https://e3center.caece.net/members/chenghsiangshei/` | '22 |
| 曾暐畯 | Jim (Wei-Chun Tseng) | `https://e3center.caece.net/members/weichuntseng/` | '22 |
| 簡元璽 | Thomas (Yuan-Hsi Chien) | `https://e3center.caece.net/members/yuanhsichien/` | '22 |
| 井本祐吾 | Yugo Imoto | `https://e3center.caece.net/members/yugoimoto/` | '23 |
| 鍾安慶 | Anching | `https://e3center.caece.net/members/anchingchung/` | '24 |
| 呂芷儀 | Harper (Chih-Yi Lu) | `https://e3center.caece.net/members/chihyilu/` | '24 |
| 周恩毅 | Derek (En-Yi Chou) | `https://e3center.caece.net/members/enyichou/` | '24 |
| 吳巽言 | Dulcinea (Hsun-Yen Wu) | `https://e3center.caece.net/members/hsunyenwu/` | '24 |
| 林宏叡 | Ray (Hung-Jui Lin) | `https://e3center.caece.net/members/hungjuilin/` | '24 |
| 楊建恆 | Jianhern Yeoh | `https://e3center.caece.net/members/jianhernyeoh/` | '24 |
| 丁俊瑋 | Gary (Jun-Wei Ding) | `https://e3center.caece.net/members/junweiding/` | '24 |
| 于懿雅 | Sonya (Yi-Ya Yu) | `https://e3center.caece.net/members/yiyayu/` | '24 |
| 東雅樹 | Masaki Higashi | `https://e3center.caece.net/members/higashimasaki/` | '25 |
| 陳厚銓 | Eric (Hou-Chuan Chen) | `https://e3center.caece.net/members/houchuanchen/` | '25 |
| 莊紹晹 | Shao-Yang Cheung | `https://e3center.caece.net/members/shaoyangcheung/` | '25 |
| 李碩宸 | Leo (Shuo-Chen Li) | `https://e3center.caece.net/members/shuochenli/` | '25 |
| 張宜鈁 | Yifang Chang | `https://e3center.caece.net/members/yifangchang/` | '25 |
| 耿又苒 | Claire (Yu-Ran Keng) | `https://e3center.caece.net/members/yurankeng/` | '25 |
| 黃榆庭 | YuTing Huang | `https://e3center.caece.net/members/yutinghuang/` | '25 |
| 鄭至亞 | Kevin (Chih-Ya Cheng) | `https://e3center.caece.net/members/chihyacheng/` | '26 |
| 黃竣昊 | Chun-Hao Huang | `https://e3center.caece.net/members/chunhaohuang/` | '26 |
| 游霈緹 | Betty (Pei-Ti Yu) | `https://e3center.caece.net/members/peitiyu/` | '26 |
| 林廷曄 | Ting-Ye Lin | `https://e3center.caece.net/members/tingyelin/` | '26 |
| 沈妤芳 | Fiona (Yu-Fang Shen) | `https://e3center.caece.net/members/yufangshen/` | '26 |

(26 unique member URLs as of 2026-05-13. List regenerates from `contents/structures/members.json` on every build.)

---

## FAQ

**Q: Do I have to do all four tiers?**
No. Tier 1 alone (ORCID + Scholar) is typically sufficient. Tiers 2–4 are extra leverage.

**Q: I added the link weeks ago and nothing happened.**
Two things to check:
1. Is the link **publicly visible** on the source platform? (Some platforms default to "private" or "only verified researchers can see"). Try opening the source URL in an incognito browser — if you can't see your E3 link there, Googlebot can't either.
2. Has Google re-crawled the source platform since you added the link? ORCID and Scholar are crawled frequently (days), LinkedIn less so (weeks). Wait a full month before concluding nothing's happening.

**Q: What if I don't want my page indexed?**
Tell the lab admin. We can mark your `members.json` entry with `noindex` (we'd need to add this field to the build) and you won't show up in Google Search, while still appearing on the site itself.

**Q: I have a personal website. Should I link from there too?**
Yes, but it carries less weight than ORCID/Scholar unless your personal site is itself well-indexed. Don't rely on it as your only inbound link.

**Q: I'm a graduated member — does this still apply?**
Yes, especially. Graduated members' pages are the hardest to index (no recent paper bylines, fewer fresh institutional links). The ORCID/Scholar links you add today will continue working long after you leave.

---

## Maintenance

Re-share this checklist:
- When a new member joins → email them their row from the lookup table within their first month.
- Quarterly → ping members who haven't completed Tier 1 yet.
- After every major lab event (paper acceptance, conference talk, award) → that's a natural moment to ask co-authors / hosts to link your E3 URL from their write-ups.

Last reviewed: 2026-05-13.
