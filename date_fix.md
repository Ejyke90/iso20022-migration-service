Code Review: MCP Tool System Prompt — Date/Time Handling
Summary
Your MCP tools (Outlook, Calendar, etc.) are suffering from a cluster of date/time bugs that all share the same root cause: the system prompt doesn't give Agents a reliable, unambiguous time anchor, and the tool descriptions have gaps in relative-date vocabulary and week/boundary semantics. The Client side Agent fills those gaps with assumptions — and its assumptions are wrong or inconsistent. The fix is a single, authoritative date/time preamble block added to the system prompt, plus patched tool descriptions.

🔴 Critical — Must Fix
[BUG] No authoritative "now" injected at runtime

Issue: Some AI model (e.g Claude Haiku) doesn't know what time it is unless you tell it. Without today = <ISO datetime + timezone> injected into every request, phrases like "tomorrow", "this week", "recent", "latest" are resolved by Claude's training heuristics — which are inconsistent and sometimes wrong (e.g. it may use UTC midnight as "now", or anchor to its training cutoff).
Fix: Inject a preamble at the top of every system prompt or as the first user-turn system message:

## Time Context (injected at request time)
Current datetime: {{CURRENT_DATETIME_ISO8601}}   # e.g. 2026-05-28T14:32:00-04:00
User timezone: {{USER_TIMEZONE}}                  # e.g. America/Toronto
Today's date: {{TODAY_DATE}}                      # e.g. 2026-05-28 (Thursday)
Day of week: {{DAY_OF_WEEK}}                      # e.g. Thursday


This must be dynamically rendered server-side before the prompt reaches the model. Never rely on Claude knowing the date.

[BUG] "Tomorrow", "yesterday", "next week" not defined

Issue: Relative terms are not grounded. "Tomorrow" requires knowing today. "Next Monday" is ambiguous if today is Monday (does it mean in 7 days, or the next occurrence?).
Fix: Add this vocabulary block to the system prompt:

## Relative Date Definitions
- "today"        → {{TODAY_DATE}} (full day, 00:00–23:59 in user timezone)
- "tomorrow"     → {{TOMORROW_DATE}}
- "yesterday"    → {{YESTERDAY_DATE}}
- "this week"    → Monday {{THIS_WEEK_MON}} through Sunday {{THIS_WEEK_SUN}}
- "next week"    → Monday {{NEXT_WEEK_MON}} through Sunday {{NEXT_WEEK_SUN}}
- "last week"    → Monday {{LAST_WEEK_MON}} through Sunday {{LAST_WEEK_SUN}}
- "this month"   → {{THIS_MONTH_START}} through {{THIS_MONTH_END}}
- "this weekend" → Saturday {{THIS_SAT}} and Sunday {{THIS_SUN}}

All values rendered server-side before the prompt is sent.

[BUG] Week start is not defined — Claude defaults to Sunday

Issue: Claude's training data is heavily US-centric; it assumes weeks start on Sunday. "This week's emails" will miss Monday–Tuesday if today is Wednesday and Claude anchors to the prior Sunday.
Fix: Explicit statement in the system prompt:

## Calendar Rules
- The week starts on MONDAY and ends on SUNDAY (ISO 8601 standard).
- "First day of the week" = Monday.
- "Last day of the week" = Sunday.

[BUG] Timezone not applied to search range boundaries

Issue: MCP APIs (Gmail, Google Calendar) accept datetime ranges in UTC or RFC 3339. If Claude constructs after:2026-05-28 without converting from the user's local midnight to UTC, searches miss emails sent in the user's evening hours (which fall on the next UTC day) or include the wrong day's results entirely. For Toronto (UTC−4), midnight local = 04:00 UTC — a 4-hour gap.
Fix: In the tool description, be explicit:
When constructing date range parameters for search queries:
- Convert all date boundaries to UTC using the user's timezone offset.
- "Start of day" = 00:00:00 in user's local timezone, converted to UTC.
- "End of day" = 23:59:59 in user's local timezone, converted to UTC.
- Always use RFC 3339 format with explicit timezone offset: 2026-05-28T00:00:00-04:00

🟡 Significant — Strongly Recommended
"Earliest" / "Latest" / "Oldest" / "Most recent" semantics

Issue: These are not defined. "Show me the latest email" — latest by received time? Sent time? Subject sort? Claude guesses. "Oldest" is particularly dangerous: without a sort order specified, some APIs return results in an undefined order.
Fix: Add to the tool description:
## Sort and Recency Definitions
- "latest" / "most recent" / "newest" → sort by received/start time DESCENDING, return first result(s)
- "earliest" / "oldest" → sort by received/start time ASCENDING, return first result(s)
- When a count is not specified for "latest" or "oldest", return the top 5.
- Never infer recency from subject line, sender name, or thread position.

Search range boundary inclusivity is ambiguous

Issue: "Emails from this week" — does that include today? Does the end of the range include 23:59 of Sunday, or is it exclusive at Monday 00:00? Off-by-one errors at range edges cause missed emails.
Fix: Define explicitly:
All date ranges are INCLUSIVE on both ends.
"From [date A] to [date B]" means: received >= start_of_day(A) AND received <= end_of_day(B).

"Recent" is undefined

Issue: "Show me recent emails" — last hour? Last 24 hours? Last 7 days? Claude picks arbitrarily.
Fix:
"Recent" without further qualification = last 7 calendar days (today and 6 days prior).
"Recent" for calendar events = next 14 days from today.

🟢 Minor — Nice to Have

Define "morning", "afternoon", "evening" in time terms if your calendar tool handles event scheduling (e.g. morning = 08:00–12:00, afternoon = 12:00–17:00, evening = 17:00–21:00).
Specify that all day-of-week names are interpreted in the user's local timezone, not UTC.
Add: "If a date or time reference is ambiguous, ask for clarification before executing a search — do not assume."


✅ What's Working Well
The decision to use MCP for Gmail/Calendar integration rather than screen-scraping or brittle OAuth flows is sound architecture. The problems here are entirely in the prompt layer — the underlying tooling is fine.

The Complete Patch (drop this into your system prompt)

## ⏰ Date & Time Context
Current datetime : {{CURRENT_DATETIME_ISO8601}}   # e.g. 2026-05-28T14:32:00-04:00
User timezone    : {{USER_TIMEZONE}}               # e.g. America/Toronto  (UTC-4 in summer)
Today            : {{TODAY_DATE}} ({{DAY_OF_WEEK}})
Tomorrow         : {{TOMORROW_DATE}}
Yesterday        : {{YESTERDAY_DATE}}

## 📅 Week Boundaries  (ISO 8601 — week starts MONDAY)
This week  : {{THIS_WEEK_MON}} – {{THIS_WEEK_SUN}}
Last week  : {{LAST_WEEK_MON}} – {{LAST_WEEK_SUN}}
Next week  : {{NEXT_WEEK_MON}} – {{NEXT_WEEK_SUN}}
This month : {{THIS_MONTH_START}} – {{THIS_MONTH_END}}
This weekend: {{THIS_SAT}} – {{THIS_SUN}}

## 🌍 Timezone Rules
Before constructing any date range query:
1. Check the ingestion DB schema to determine how timestamps are stored
   (UTC, local time with offset, or Unix epoch).
2. Check whether a user_timezone or offset column exists in the DB.
3. If timestamps are already stored in the user's local time → query as-is,
   no conversion needed.
4. If timestamps are stored in UTC → convert all range boundaries from
   user's local time to UTC before querying.
5. ALL responses to the user must display times in their local timezone
   ({{USER_TIMEZONE}}), regardless of how the DB stores them.
   Never surface UTC or epoch values directly to the user.

## 📬 Recency & Sort Rules
- "latest" / "most recent" / "newest" → sort DESCENDING by received/start time
- "earliest" / "oldest"               → sort ASCENDING by received/start time
- "recent" (unqualified)              → last 7 days for email; next 14 days for calendar
- Default result count when unspecified: 5

## 📐 Range Inclusivity
All date ranges are INCLUSIVE on both ends.
"This week" includes all of Monday 00:00 through Sunday 23:59 in user's local timezone.

## ❓ Ambiguity Rule
If a date/time reference cannot be resolved with certainty, ask the user for clarification
before executing any search or action. Do not assume.


Every {{variable}} must be filled server-side at request time. This patch eliminates every class of bug you described.


Correct — and here's why it won't.
The entire patch is ~30 lines of plain text, which is roughly 300–400 tokens. That's a one-time fixed cost per request, not something that grows with the conversation. To put it in perspective:

A single average email body is 200–500 tokens
A typical Calendar event with description is 100–200 tokens
The patch: ~350 tokens, always

So the patch costs less than one email, every time, unconditionally.
The variables ({{TODAY_DATE}}, {{UTC_OFFSET}}, etc.) are all short strings — dates, timezone names, offsets. They don't expand into paragraphs. The rendered patch looks like:
Current datetime : 2026-05-28T14:32:00-04:00
User timezone    : America/Toronto
Today            : 2026-05-28 (Thursday)
Tomorrow         : 2026-05-29
...
That's it. Flat, dense, small.
The actual context growth in your setup comes from elsewhere — retrieved email bodies, long calendar event descriptions, conversation history, search results. The date preamble is noise-floor level compared to any of those. It's also not cumulative: it doesn't appear in every turn of a multi-turn conversation, only once in the system prompt or the first message. It doesn't grow as the conversation grows.
The short version: you're buying disambiguation and correctness at a cost that rounds to zero.
