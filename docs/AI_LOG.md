# AI Usage Log – DvG Projektarbeit (ShopEasy Returns)

**AI tool used:** Claude (Anthropic), via chat.
**How I use it:** as a tutor and sparring partner. The AI explains concepts and proposes
options; I make the decisions and type the code myself, so I understand every part.

## Share levels
- **Explained** – AI explained concepts; I did the work
- **Proposed** – AI suggested options; I chose or adapted them
- **Generated, reviewed** – AI produced it; I checked, understood and typed or adapted it
- **Generated** – AI produced it; I used it largely as it was

## Overview

| Date | Sprint | Step | AI share |
|---|---|---|---|
| 2026-10-28 | 1 | Review of to-be BPMN model | Proposed |
| 2026-10-28 | 1 | Reworked to-be BPMN (v2) | Generated, reviewed |
| 2026-10-28 | 2 | Understanding the assignment and lecture slides | Explained |
| 2026-10-28 | 2 | Tool choice and project setup (Git, venv) | Proposed |
| 2026-10-28 | 2 | Return status model and allowed transitions | Proposed |
| 2026-10-28 | 2 | Mock data (returns and orders) | Generated, reviewed |

## Entries

### 2026-10-28 – Sprint 1: Review of to-be BPMN model
- **Task:** Check my to-be model for errors; add the marketplace pool and the email
  channel (professor's feedback).
- **AI:** Listed BPMN errors (message events inside one pool, implicit parallel splits,
  wrong timer event) and content gaps (no borderline-case path, no timeouts, no refund payout).
- **Me:** Brought the model and the professor's feedback; reviewed the findings.
- **Learned:** Message flows only connect different pools; sequence flows with more than one
  outgoing path need an explicit gateway.

### 2026-10-28 – Sprint 1: Reworked to-be BPMN (v2)
- **Task:** Apply the fixes and extensions.
- **AI:** Generated the new BPMN file (Sprint_1_Soll_v2.bpmn) and explained every change.
- **Me:** Reviewed the result, checked it against the case, accepted the assumptions
  (14-day timeout, 300 EUR approval limit, 15-min polling).
- **Learned:** How marketplaces are integrated via API polling; why condition checks need a
  three-way decision (ACCEPT / REJECT / MANUAL_REVIEW).

### 2026-10-28 – Sprint 2: Understanding the assignment and lecture slides
- **Task:** Understand what Sprint 2 requires and what the lectures (04_1 Integration,
  04_2 EDA) contribute.
- **AI:** Summarised the assignment and slides; explained client/server, HTTP, REST, gRPC
  and messaging in plain terms.
- **Me:** Asked follow-up questions until I could explain each concept myself.
- **Learned:** Synchronous vs. asynchronous communication; loose vs. tight coupling;
  why each of the three components uses a different integration style.

### 2026-10-28 – Sprint 2: Tool choice and project setup
- **Task:** Choose language and tools; set up the repository.
- **AI:** Proposed Python with FastAPI, gRPC and RabbitMQ; explained Git (add, commit, push)
  and virtual environments.
- **Me:** Decided on Python; created the GitHub repository, cloned it, set up the venv
  and folder structure myself.
- **Learned:** Git's working folder / staging area / repository; why a venv isolates
  project libraries; requirements.txt for reproducibility.

### 2026-10-28 – Sprint 2: Return status model
- **Task:** Define the statuses a return can have and which changes are allowed.
- **AI:** Proposed 13 statuses with business situations and a transition table.
- **Me:** Reviewed each status against my BPMN model and approved the list.
- **Learned:** Difference between HTTP status codes and business statuses; why forbidden
  transitions should be rejected (409 Conflict).

### 2026-10-28 – Sprint 2: Mock data
- **Task:** Create example returns and orders for the REST API.
- **AI:** Explained the data structure field by field and provided six example returns
  and orders.
- **Me:** Typed the first return and order myself to learn the structure; added the rest;
  validated the file with `python3 -m json.tool`.
- **Learned:** JSON syntax rules; difference between a return and an order.