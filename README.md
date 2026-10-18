# finlit-contentplatform

Content repository for **FinKids** — financial literacy gaming app for Indian families.

This repo stores all learning content for the app: markdown lessons, mobile-hostable slides, HTML pages, and images. It will later evolve into the full content hosting and caching platform serving content directly to the FinKids mobile app.

## Content types

| Format | Purpose |
|---|---|
| Markdown (`.md`) | Structured lessons, quizzes, habit prompts |
| HTML / Reveal.js slides | Mobile-hostable slide decks |
| HTML pages | Rich styled content pages |
| Images | Illustrations and supporting visuals (free tools) |

All content must be hostable in a mobile app — no PowerPoint or Google Slides.

## Agents

See [AGENTS.md](./AGENTS.md) — JP-ContentLoader1 (Jay) and CP-ContentLoader2 (Chetna) are the agents for this repo, coordinated via [AgentCom](https://github.com/teamfinlit/AgentCom).

## Branch model

| Branch | Purpose |
|---|---|
| `main` | Approved, merged content |
| `JP-ContentLoader1` | Jay's agent working branch |
| `CP-ContentLoader2` | Chetna's agent working branch |

PRs require approval from both the peer content loader agent and the human owner before merging to `main`.
