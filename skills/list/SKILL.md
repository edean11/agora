---
name: list
description: >
  List available Agora personas, past discussions, saved populations, or
  past simulations. Use when the user wants to browse Agora resources.
disable-model-invocation: true
allowed-tools: Read, Glob, Bash
argument-hint: personas | discussions | populations | simulations
---

# Agora List

**AGORA_HOME:** !`echo ${AGORA_HOME:-$HOME/.agora}`

Use this absolute path for ALL file operations. Never use relative paths.

If AGORA_HOME does not exist, tell the user: "Agora is not set up yet. Run /agora:discuss to initialize."

Arguments: `$ARGUMENTS`

## If arguments contain "personas" (or no arguments):

1. Use Glob to find all `{AGORA_HOME}/agents/*.md` files
2. For each file, read just the first 6 lines to extract the Name and Background fields
3. Display as a formatted list:
   ```
   Available Personas ({count}):

   - socrates — Socrates (ancient Greek philosopher, Socratic method)
   - ada-lovelace — Ada Lovelace (mathematician, first computer programmer)
   ...
   ```
   Format: `{filename-without-md} — {Name} ({brief background excerpt, max 60 chars})`
4. Sort alphabetically by persona ID

## If arguments contain "discussions":

1. Use Glob to find all `{AGORA_HOME}/discussions/*/meta.md` files
2. For each meta.md, read it and extract Topic, ID, Created, Participants, and Status
3. Display as a formatted list sorted by creation date (newest first):
   ```
   Past Discussions ({count}):

   - [active]    "What makes a life worth living?" (2026-02-15)
                  ID: what-makes-a-life-worth-living-397e7a51
                  Participants: Socrates, Nietzsche, Confucius, Simone de Beauvoir, Oscar Wilde

   - [completed] "Should we colonize Mars?" (2026-02-13)
                  ID: should-we-colonize-mars-803bae03
                  Participants: Ada, Dante, Sophia
   ...
   ```

## If arguments contain "populations":

1. Use Glob to find all `{AGORA_HOME}/populations/*/population.md` files
2. For each file, read just the first 8 lines to extract the Description, Segment Count, and Created date
3. Display as a formatted list sorted alphabetically by ID:
   ```
   Saved Populations ({count}):

   - us-consumers — US General Consumers (6 segments, 2026-03-22)
   - tech-early-adopters — Technology Product Early Adopter Segments (5 segments, 2026-03-22)
   ...
   ```
   Format: `{directory-name} — {Description} ({segment count} segments, {date})`

If no populations found, tell the user: "No saved populations. Create one with: /agora:population create \"description\" or run /agora:simulate to auto-generate one."

## If arguments contain "simulations":

1. Use Glob to find all `{AGORA_HOME}/simulations/*/meta.md` files
2. For each meta.md, read it and extract Scenario, ID, Created, Population Description, Segments, Status, Weighted Likelihood, and Weighted Sentiment
3. Display as a formatted list sorted by creation date (newest first):
   ```
   Past Simulations ({count}):

   - [completed] "If we raised prices 20%..." (2026-03-22)
                  ID: if-we-raised-prices-20-a1b2c3d4
                  Population: B2B SaaS customers (6 segments)
                  Likelihood: 35% | Sentiment: -1.2

   - [completed] "Would voters support a carbon tax?" (2026-03-21)
                  ID: would-voters-support-a-carbon-tax-e5f6a7b8
                  Population: US registered voters (7 segments)
                  Likelihood: 48% | Sentiment: 0.3
   ...
   ```

If no simulations found, tell the user: "No simulations yet. Run one with: /agora:simulate \"scenario\" \"population description\""
