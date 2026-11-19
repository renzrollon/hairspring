# TillPoint POS interface (summary of spec v2.1)

- The POS sends a purchase event for every completed purchase with a member QR code.
- The POS calls the voucher validation endpoint before applying a voucher.
- The POS shows the member's points balance on the customer display.
- Member tier and points summary are sent from the loyalty service to the CRM every night.
