# Formal Permission Request: CDN Publishing / Greysheet API Wholesale Data Display

**To:** CDN Publishing / Greysheet API Licensing Team (`support@greysheet.com` / `api@greysheet.com`)  
**From:** Numista.AI Integration Engineering (`support@numista.ai`)  
**Date:** July 30, 2026  
**Subject:** Permission Request under Section 4.3 — Wholesale Pricing Rendering for Authenticated Subscriber Accounts  

---

### Dear CDN Publishing API Licensing Team,

We are active subscribers to the **Greysheet Advanced API Tier** (`apiLevel=advanced`). Our application, **Numista.AI**, is a specialized numismatic collection management and estate planning platform designed for collectors, estate executors, and numismatic professionals.

In strict compliance with **Section 4.3 and Section 4.4/4.5** of the CDN API License Agreement, we currently limit all public-facing pricing displays to permitted retail guides (**CPG® Retail / Red Book**) accompanied by hyperlinked attributions to `https://www.greysheet.com`.

### Proposed Authenticated-User Feature Request
We are requesting formal written authorization under **Section 4.3** to render **Greysheet® Wholesale Bid & Ask** values strictly within **private, authenticated subscriber account views** for the following specific use cases:

1. **Private Estate Planning & Liquidation Estimates**: Enabling estate executors and collectors to view an *"Estimated Dealer Liquidation Basis"* (derived from Greysheet Wholesale Bid) inside their password-protected private vault dashboard.
2. **Dealer Buy/Sell Margin Spread Analysis**: Allowing authenticated users to view the wholesale bid-ask spread when evaluating their private inventory before transacting with authorized dealers.

### Our Compliance & Security Commitments
- **No Unauthenticated Public Display**: Wholesale numbers (`GreyVal` / `GreyAskVal`) will **never** be rendered on unauthenticated public web pages, landing pages, or open web crawlers.
- **No Data Scraper / CSV Export**: Raw Greysheet data feeds will **never** be made available for bulk download, scraping, or raw API redistribution.
- **Mandatory Attribution**: All screens rendering CDN data will display prominent, clickable attributions: *"Market value estimates based on CPG® and Greysheet® data from Greysheet.com"*.
- **24-Hour Cache Policy**: All cached values strictly obey the 24-hour TTL restriction under Section 7.2.

We kindly request your formal written approval for this authenticated subscriber account rendering. Please let us know if you require any additional technical details or staging previews of our private user dashboard layout.

Sincerely,  

**The Numista.AI Engineering & Leadership Team**  
Email: `support@numista.ai`  
Website: `https://numista-vault.web.app`  
