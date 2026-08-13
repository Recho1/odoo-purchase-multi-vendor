# Purchase Multi Vendor

Odoo 19 custom addon built for the Odoo Community Edition developer assignment.
Extends the standard **Purchases** app to support assigning a single RFQ to
multiple vendors, collecting bids, selecting a winner, and routing employee
purchase requests into the RFQ process.

## What this module does

| # | Requirement | Implementation |
|---|---|---|
| 1 | Assign an RFQ to multiple vendors | `vendor_ids` many2many field on `purchase.order`, shown as a multi-select tag widget on the RFQ form (`Vendors` field, next to the existing `Vendor` field). |
| 2 | Receive bids from suppliers | New `purchase.bid` model with a many2one back to the RFQ (`purchase_order_id`) and a corresponding one2many (`bid_ids`) shown as an editable list under a new **Bids** tab on the RFQ form. |
| 3 | Select a winning bid → generate a PO | `action_select_as_winner()` on `purchase.bid` marks the winning bid, marks sibling bids as lost, sets the winning vendor as the RFQ's `partner_id`, and calls Odoo's own `button_confirm()` to turn the RFQ into a confirmed Purchase Order. |
| 4 | Employee purchase requests → RFQ | New `purchase.request` model with a draft → submitted → approved/rejected workflow. `action_convert_to_rfq()` creates a new RFQ pre-filled with the requested product/quantity, ready for Procurement to assign vendors. |

## Installation

1. Copy this folder into your Odoo `addons` path (e.g. `odoo/addons/purchase_multi_vendor`).
2. Restart the server with `-i purchase_multi_vendor` (first install) or `-u purchase_multi_vendor` (upgrade).
3. The **Purchase** app must already be installed (`depends: ['purchase']`).

## Design decisions and known simplifications

- **`partner_id` (Vendor) is kept as-is.** Odoo's core purchase logic
  (pricelists, currency, terms) depends on this field always being set, so
  it wasn't removed. `vendor_ids` (Vendors) was added alongside it to satisfy
  the multi-vendor requirement without a full redesign of `purchase.order`.
  An `onchange` auto-fills `partner_id` from the first selected `vendor_ids`
  entry when `partner_id` is empty, so in practice the user usually only
  needs to touch the `Vendors` field.
- **`action_rfq_send` is overridden** so clicking "Send RFQ" includes every
  vendor in `vendor_ids` as an email recipient, not just the primary vendor.
- **Winning-bid price logic is simplified**: if the RFQ has exactly one
  order line, the winning bid's price is applied to it. RFQs with multiple
  product lines are not automatically re-priced per line — this was judged
  out of scope for the assignment's core requirement (selecting a winner
  and generating a PO), but is a known limitation.
- **Purchase Requests use `res.users`, not `hr.employee`**, for the
  requester field, to avoid adding a hard dependency on the HR module.
- **Placeholder vendor on RFQ creation**: Odoo requires `partner_id` to be
  set when a `purchase.order` is created. Since a Purchase Request is
  converted to an RFQ *before* Procurement has chosen vendors, the module
  falls back to the first available supplier-tagged contact (or, if none
  exist, the first contact in the system) as a temporary placeholder.
  Procurement is expected to replace this via the `Vendor`/`Vendors` fields
  immediately after conversion.

## Manual test flow

1. Purchases → Requests for Quotation → New → add 2+ vendors in the
   `Vendors` field → Save.
2. Open the **Bids** tab → add 2+ bids with different prices → Save.
3. Click **Select as Winner** on the lowest bid → confirm the RFQ becomes a
   confirmed Purchase Order with that vendor.
4. Purchases → Purchase Requests → New → fill in description/quantity →
   Submit → Approve → Convert to RFQ → confirm a new RFQ is created with
   the request's product/quantity pre-filled.

## Author

Racheal Acio
