# Agents

## Who works in this repo

| Agent | Name | Owner | Role |
|---|---|---|---|
| CL1 | JP-ContentLoader1 | Jay | Content Loader — loads Jay's content |
| CL2 | CP-ContentLoader2 | Chetna | Content Loader — loads Chetna's content |

Each agent works on its own named branch and opens a PR for peer + human review before merging to `main`.

---

## AgentCom — Communication Hub

All inter-agent communication happens via the AgentCom repo:
**https://github.com/teamfinlit/AgentCom**

| Agent | Inbox | Memory |
|---|---|---|
| JP-ContentLoader1 | `agents/JP-ContentLoader1/inbox/` | `agents/JP-ContentLoader1/memory/` |
| CP-ContentLoader2 | `agents/CP-ContentLoader2/inbox/` | `agents/CP-ContentLoader2/memory/` |

---

## Starting a content loader session

Paste the contents of the relevant `init.md` from AgentCom as your first prompt:

**Jay (JP-ContentLoader1):**
```
# Paste contents of: agents/JP-ContentLoader1/init.md
```

**Chetna (CP-ContentLoader2):**
```
# Paste contents of: agents/CP-ContentLoader2/init.md
```

---

## How content gets into this repo

```
1. Owner (Jay or Chetna) provides raw content
   → Any format: Excel, Word, plain text, etc.

2. Agent discusses with owner
   → Clarifies structure, tone, target audience, format requirements

3. Agent generates output artifacts
   → Markdown files (.md)
   → Mobile-hostable slides (Reveal.js / HTML / JSON — not PowerPoint)
   → HTML content pages
   → Images (free tools, agent's choice)

4. Agent pushes to its own branch
   → JP-ContentLoader1 → branch: JP-ContentLoader1
   → CP-ContentLoader2 → branch: CP-ContentLoader2

5. Agent opens a PR into main
   → PR description: what was loaded, formats generated, decisions made

6. Two approvals required before merge
   → Peer content loader agent reviews and approves
   → Human owner (Jay or Chetna) reviews and approves on GitHub
```

---

## Branch convention

| Branch | Owned by |
|---|---|
| `main` | Merged, approved content only |
| `JP-ContentLoader1` | Jay's agent working branch |
| `CP-ContentLoader2` | Chetna's agent working branch |

---

## Content structure (evolving)

This repo will eventually host and serve content directly to the FinKids mobile app. Current structure is being established as content is loaded. All content must be in mobile-hostable formats.

---

## Collaboration between CL1 and CL2

Both agents can work on the same or different content simultaneously. When working on the same content:
- Coordinate via AgentCom before starting — agree on file/scope split
- Each agent takes ownership of specific files to avoid branch conflicts
- Reference each other's `message_id` in coordination messages

---

## Related repos

| Repo | URL | Agent(s) |
|---|---|---|
| AgentCom | https://github.com/teamfinlit/AgentCom | Communication hub for all agents |
| finlit-ui | https://github.com/teamfinlit/finlit-ui | DP-UIDev |
| finlit-backend | https://github.com/teamfinlit/finlit-backend | TP-BEDev |
