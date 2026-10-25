# Copy for states

## Problem states

Answer three questions in order: what happened, what happened to my data or money, what can I do now.

| Weak | Better | Why |
| --- | --- | --- |
| Something went wrong. | We couldn't load your orders. Check your connection and try again. | Names the thing that failed and the way out |
| Payment failed. | Your bank declined this payment. You haven't been charged. Try another card or contact your bank. | Says the money did not move, and gives two ways out |
| Error 504 | We didn't hear back from your bank in time. Your payment may still go through. We'll email you within 10 minutes, so please don't pay again. | Honest about the unknown outcome; prevents a double payment |
| Invalid input | Enter a date after today. | Says what valid looks like |
| Access denied | You need to be an admin to change billing. Ask Priya or another admin. | Says why and who can help |

## Empty states

Say why it is empty and what to do, in that order. First use, no results and cleared data are different states.

- **First use**: "No invoices yet. When you send one, it'll appear here." Action: Create invoice
- **No results**: "No invoices match 'Aroha'. Check the spelling or clear the filters." Action: Clear filters
- **Cleared**: "You've archived every invoice." Action: View archive

## Waiting states

- Under a second: no indicator.
- One to ten seconds: skeleton or spinner in place, layout steady.
- Longer: say what is happening and, if possible, how long it takes. Let people leave and come back.

## Success states

Confirm what happened with the specifics people will check: the amount, the recipient, the time. Say what happens next if anything does ("Aroha will get an email with a link to pay"). Offer undo when the action is reversible.

## Phrases to avoid

Something went wrong, Oops, Uh oh, An error occurred, Invalid input, Unknown error, Please try again later (without a reason), Are you sure? (without saying what will be lost). Avoid blaming the person ("You entered the wrong code") when a neutral version works ("That code didn't match").
