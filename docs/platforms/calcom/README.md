Last verified: 2026-11-06

# Cal.com (booking platform)

Used as a client's booking system and connected to Retell as a native integration
(see `docs/platforms/retell/capabilities.md` §3). Platform knowledge only; client IDs live in
the client folders.

## API basics
- Base URL: `https://api.cal.com/v2`
- Auth: `Authorization: Bearer $CALCOM_API_KEY` (keys look like `cal_live_…`)
- **`cal-api-version` header required**, and it differs by endpoint:
  - `/schedules` → `2024-06-11`
  - `/event-types` → `2024-06-14`
  - `/slots` → `2024-09-04`
- **Send a `User-Agent` header.** Python's default `urllib` agent gets an HTML block page
  (non-JSON) from Cal.com's edge. curl works as is.
- Network: `api.cal.com` must be on the cloud environment's allowed hosts.

## Key test (read-only)
```bash
curl -sS https://api.cal.com/v2/me -H "Authorization: Bearer $CALCOM_API_KEY"
```
Returns 200 with the account `{id, email, timeZone, defaultScheduleId, …}`.

## Calls we use
| Task | Call | Notes |
|---|---|---|
| List schedules | `GET /schedules` | |
| Create schedule | `POST /schedules` `{name, timeZone, isDefault:false, availability:[{days,startTime,endTime}], overrides:[{date,startTime,endTime}]}` | Keep `isDefault:false` so the account default isn't changed |
| Close a whole day | override `{"date":"YYYY-MM-DD","startTime":"00:00","endTime":"00:01"}` | A 1-minute window means no slot fits — effectively closed |
| List event types | `GET /event-types` | |
| Create event type | `POST /event-types` `{title, slug, lengthInMinutes, description, scheduleId, slotInterval, minimumBookingNotice, locations:[{type:"address",address,public:true}], bookingFields:[{type:"phone",slug:"attendeePhoneNumber",label,required:true}]}` | Default booking fields: name + email (required) |
| Check slots | `GET /slots?eventTypeId=&start=YYYY-MM-DD&end=YYYY-MM-DD&timeZone=` | Last start time respects the service length (e.g. a 3 h service on a day ending 18:00 → last start 15:00) |

## Gotchas
- **One Cal.com user = one calendar.** Every event type on the account shares the same busy
  time. That includes other businesses' event types on a shared account. Per-stylist parallel
  availability needs Cal.com **Teams** (each stylist a member; round-robin or collective event
  types).
- The account's profile `timeZone` is separate from each schedule's `timeZone`. Slots follow
  the schedule; host emails and the UI may follow the profile.
- Through Retell, `book_calcom_appointment` asks for every required booking field of the event
  type (e.g. `attendeePhoneNumber` must be E.164).

## Sources
- Live API calls on 2026-11-06 (`/me`, `/schedules`, `/event-types`, `/slots`).
- https://cal.com/docs/api-reference/v2
