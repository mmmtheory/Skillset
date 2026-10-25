# Domain packs

States that generic traits miss. Use the packs for every domain in play. For each state, ask whether it can happen here and who sees it.

## Payments and commerce

- **Pending**: authorised but not settled; bank transfer initiated; payment awaiting the customer's bank app approval
- **Held for review**: fraud or compliance check; who is told, and how long it usually takes
- **Declined**: insufficient funds, card expired, limit reached, blocked by the issuer. Different causes need different next steps, but never reveal fraud rules
- **Unknown outcome**: the request timed out after it was sent. The person must not pay twice. Say the payment may have gone through and how they will find out
- **Partly paid**: split payment where one method failed; voucher covered part
- **Refunded, partly refunded, reversed, charged back**: and how long until the money arrives
- **Price changed**: between cart and checkout; currency conversion moved
- **Out of stock**: after it was added to the cart; after payment
- **Duplicate**: double tap, retry after timeout; idempotency on the server, and what the person sees
- **Merchant side**: payment received but not yet settled to their account; dispute opened; payout failed

## Accounts and sign-in

- New, invited but not accepted, unverified email, locked after failed attempts, suspended, deleted but recoverable
- Session expired mid-task: what happens to unsaved work
- Signed in on another device; signed out elsewhere
- Plan or trial ended; payment method failed on renewal
- Signing in with a different method than the one used to sign up
- Account recovery when the person has lost access to their email or phone

## Collaboration

- Someone else edited this while you were editing it (conflict)
- Item deleted or moved by someone else while you were viewing it
- Your access was removed or reduced mid-session
- Shared with someone who does not have an account
- Assigned to someone who has left the team
- Mentioned or notified about something you can no longer open

## Booking and scheduling

- Slot taken while the person was deciding
- Time zones: the person and the venue or other attendee in different zones; daylight saving changes
- Booking requested but not confirmed; waitlisted
- Cancelled by the other side; rescheduled; no-show
- Past, in progress, starting soon
- Recurring events: one occurrence changed

## AI features

- Generating (with real progress where possible), stopped by the person, partly complete
- Low confidence or no answer; the answer cites sources that are unavailable
- Refused for policy reasons; what the person can do instead
- Output that acted on something (sent, changed, booked): receipt and undo
- Rate limited or out of credits
- Model or tool unavailable; slower than usual
- Person's data used as context: which data, and how to remove it

## Forms and onboarding

- Partly filled, saved as draft, abandoned and returned to later
- Validation: on blur, on submit, server-side after submit; errors on fields not currently visible
- Data that could not be verified (address, company number) and what happens next
- Prefilled from elsewhere and wrong
- Skipped optional steps; coming back to them later

## Files and media

- Uploading with progress, paused, failed, too large, wrong type, virus scan pending
- Processing (transcoding, OCR) after upload
- Duplicate file name; version conflicts
- Preview unavailable for this type; file corrupt
- Storage full; download links expired

## Notifications and messages

- Unread, read, archived; the thing it points to was deleted
- Delivery failed (email bounced, push disabled)
- Muted, snoozed, digest instead of immediate
- A burst: twenty notifications about one thing
