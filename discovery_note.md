# Phase 1: Discovery Note
**Client:** Dhaga & Co.  
**Engagement:** Mini Project 1 — Pattern-Based Workflow  
**Date:** October 3, 2026 (Dated before first code commit)  
**Authors:** Five-Member Project Team

---

### 1. The Problem (In the Client's Language)
> *"Our drop calendar slips almost every week because listing 400 new SKUs by hand takes 6 to 9 days, making us miss the Tuesday and Friday traffic spikes that drive our weekly revenue."*

---

### 2. Who Owns This Problem & How It Runs Today
* **Problem Owner:** Vivek (Listing Lead) and his 6-person listing team.
* **What They Do Today:**
  1. A new physical sample arrives from vendors in Tiruppur or Jaipur.
  2. The sample goes through a studio photoshoot.
  3. The 6-person listing team manually opens the internal admin panel and types roughly 60 attributes per item by hand (copying from vendor notes or looking at pictures).
  4. 4 people write product descriptions by hand (~200 written each week).
  5. The whole process takes **6 to 9 days**, which causes the drop schedule to slip past Tuesday or Friday.

---

### 3. Case Study Evidence
* **Direct Quote from Vivek:** *"Six to nine days from sample to live. The drop calendar slips most weeks, and when it slips we lose the Tuesday traffic spike entirely."*
* **High Volume & Fast Turnover:** Dhaga adds ~400 new SKUs every week and has ~14,000 SKUs live at any time. Items that do not sell within 6 weeks are pulled.
* **Messy Data Reality:**
  * **Color:** Has been manually typed in about **90 different ways** (e.g., "navy blue", "dark royal navy", "light faded blue"). This breaks customer filters.
  * **Fabric:** Stored as messy free text with no fixed format.
  * **Size Charts:** Vary by vendor, causing confusion.
  * **Tone Inconsistency:** Descriptions are written by hand with inconsistent brand voice, and older listings are never revisited.
* **Customer Search Behavior:** 92% of orders are on the Android app, and customers search in Hinglish by occasion (like *"mehndi function dress"*, *"office wear kurti"*), which manual listing often misses.

---

### 4. What It Costs Dhaga & Co. Today
* **Lost Revenue from Traffic Surges:** Tuesday and Friday are Dhaga's scheduled drop days where shoppers open the app expecting fresh items. When listings slip, they lose the surge traffic for that entire drop cycle.
* **High Labor & Time Cost:** 6 full-time listing staff spend 6 to 9 days typing attributes and writing copy manually for 400 SKUs every single week.
* **Broken Search & Discovery:** Because colors have 90 spellings and tags lack Hinglish occasion terms, customers on low-end phones cannot find what they want, hurting conversion.

---

### 5. What Success Looks Like & How to Measure It
* **What Success Looks Like:**
  * Listing team time per batch drops from **6–9 days down to under 2 days** (with automated attribute extraction and copy drafting).
  * 0 missed Tuesday and Friday drop deadlines due to catalog bottlenecks.
  * Colors automatically standardized into canonical buckets (fixing search filters).
  * Product copy generated with consistent brand voice and occasion tags.
  * Listing team acts as an approval editor rather than a manual data-entry typist.
* **How to Measure It (Using Data Dhaga Already Has):**
  * **Lead Time Metric:** Timestamp difference in the database between photoshoot upload and SKU "Status = Live".
  * **Drop Schedule Compliance:** Percentage of weekly Tuesday/Friday drops that launch on time without slipping.
  * **Listing Time Spent:** Weekly hours Vivek's team spends on manual typing vs. review.

---

### 6. Ranked Shortlist of Problems Considered

| Rank | Problem | Owner | Why It Sits Here |
| :---: | :--- | :--- | :--- |
| **#1** | **Cataloging Delay & Attribute Standardizer** | Vivek (Listing Lead) | **Top Choice:** Direct revenue impact on weekly drop traffic, solves the 90-color mess, has an obvious internal user, and naturally provides a human review step before publishing. |
| **#2** | **Support Ticket Tagging & WISMO Copilot** | Arpita (Head of CX) | **Rank 2:** 58% of 9k tickets/week are simple "Where is my order" queries taking 9 hours to reply. Great operational saving, but less direct impact on top-line revenue than missing drop traffic. |
| **#3** | **Unstructured Return Reasons & Fit Invisibility** | Neha (Category) & Faizan (Supply Chain) | **Rank 3:** 44% of returns sit unanalyzed in "Other", costing ₹120 per COD RTO. High business impact, but fixing fit requires long-term vendor physical changes rather than an immediate software workflow. |
| **#4** | **Unstructured Reviews for Retention Insights** | Karthik (Analyst) & Ritu (CEO) | **Rank 4:** 410,000 product reviews sit unread while repeat purchase is stuck at 22%. Insightful for strategy, but acts as a background reporting tool rather than an active daily workflow tool. |

---

### 7. Biggest Assumption & What Would Disprove It
* **Our Biggest Assumption:** The primary bottleneck causing the 6–9 day delay is the *manual data entry and copy typing* by the listing team, meaning vendor specs and photos are ready earlier in that window.
* **What Evidence Would Disprove It:** If internal logs reveal that the studio photoshoot or physical sample delivery takes 6 or 7 of those 9 days, then automating the listing admin work would only save 1–2 days and wouldn't solve the whole drop slip problem on its own.
