---
name: population
description: >
  Create, list, and view population segment profiles for Agora simulations.
  Auto-generates diverse representative demographic segments from a description.
  Use to pre-build reusable populations for later use with /agora:simulate.
disable-model-invocation: true
allowed-tools: Read, Write, Edit, Glob, Bash, Agent, AskUserQuestion
argument-hint: create "description" | list | view <id>
---

# Agora Population Manager

You manage population segment profiles for Agora simulations. Populations are collections of diverse demographic segments that represent a target group. They can be created once and reused across multiple simulations.

## Configuration

**AGORA_HOME:** !`echo ${AGORA_HOME:-$HOME/.agora}`

Use this absolute path for ALL file operations. NEVER use relative paths — this skill can be invoked from any working directory.

If AGORA_HOME does not exist, tell the user: "Agora is not set up yet. Run /agora:discuss or /agora:simulate to initialize."

Arguments: `$ARGUMENTS`

## If arguments start with "create":

### Step 1: Parse Description

Extract the population description from the arguments (everything after "create"). The description should be a quoted string or the remaining text.

If no description is provided, use AskUserQuestion to ask: "Describe the population you want to simulate (e.g., 'US smartphone buyers', 'voters in swing states', 'enterprise SaaS customers')."

### Step 2: Generate Population ID

- Slugify the description: lowercase, replace spaces with hyphens, remove special characters, truncate to 40 chars
- Append a random 8-character hex suffix: `python3 -c "import secrets; print(secrets.token_hex(4))"`
- Result: `{slug}-{hex}`

### Step 3: Determine Segment Count

Default: 6 segments. Adjust based on population complexity:
- Narrow/specific populations (single age bracket, single city): 4-5
- Broad/general populations (all US adults, global consumers): 7-8

### Step 4: Generate Segments

Analyze the population description and generate diverse representative segments. Follow these rules:

**Diversity is mandatory.** Segments MUST span the full spectrum along multiple axes: socioeconomic status, age/generation, geography (urban/suburban/rural), ideology/values, and lifestyle.

**Include extremes.** At least one segment likely to be strongly positive toward most scenarios, at least one strongly negative, and at least one ambivalent/conflicted.

**Internal coherence.** Each segment's demographics, psychographics, behaviors, and attitudes must tell a consistent, believable story about real people.

**No stereotypes.** Avoid lazy generalizations. Each segment should feel like a real cohort with nuanced attributes.

**Sizes must sum to 100%.** Assign realistic proportions — not all segments are equal.

Generate each segment using this EXACT structure:

```markdown
# {Descriptive Segment Label}

## Demographics
- **Label:** {segment label, e.g., "Urban Young Professionals"}
- **Size:** {percentage of total population, e.g., "18%"}
- **Age Range:** {e.g., "25-34"}
- **Income Bracket:** {e.g., "Upper-middle ($75K-$120K)"}
- **Education:** {e.g., "Bachelor's degree or higher"}
- **Location Type:** {e.g., "Urban metro areas"}
- **Household:** {e.g., "Single or cohabiting, no children"}

## Psychographics
- **Values:** {1-3 core values}
- **Identity:** {how they see themselves}
- **Aspirations:** {what they want}
- **Anxieties:** {what worries them}

## Behavioral Profile
- **Media Diet:** {media consumption patterns}
- **Spending Priorities:** {where their money goes}
- **Brand Orientation:** {how they relate to brands}
- **Decision Style:** {how they make purchasing/adoption decisions}

## Attitudinal Anchors
- **Trust in Institutions:** {Low/Medium/High}
- **Price Sensitivity:** {Low/Medium/High}
- **Risk Tolerance:** {Low/Medium/High}
- **Change Openness:** {Low/Medium/High}
- **Tech Comfort:** {Low/Medium/High}

## Constraints & Context
- **Budget Constraints:** {financial situation and limitations}
- **Time Constraints:** {time availability and pressures}
- **Access Constraints:** {physical, digital, or social access limitations}
```

### Step 5: Save Population

Create the directory via Bash: `mkdir -p {AGORA_HOME}/populations/{pop-id}`

Write `{AGORA_HOME}/populations/{pop-id}/population.md`:

```markdown
# {Population Description}

- **ID:** {population-id}
- **Created:** {ISO 8601 timestamp via `date -u +%Y-%m-%dT%H:%M:%S`}
- **Segment Count:** {N}
- **Description:** {original population description}

---

{Segment 1 full profile}

---

{Segment 2 full profile}

---

{... all segments separated by ---}
```

### Step 6: Display Result

```
=== Population Created ===
Description: {description}
ID: {pop-id}
Segments: {N}

  - {Segment 1 Label} ({size}%)
  - {Segment 2 Label} ({size}%)
  - ...

Saved to: {AGORA_HOME}/populations/{pop-id}/population.md
Use with: /agora:simulate "scenario" --population {pop-id}
```

## If arguments contain "list" (or no arguments):

1. Use Glob to find all `{AGORA_HOME}/populations/*/population.md` files
2. For each file, read just the first 8 lines to extract the description, segment count, and creation date
3. Display as a formatted list:
   ```
   Saved Populations ({count}):

   - us-consumers — US General Consumers (6 segments, 2026-03-22)
   - tech-early-adopters — Technology Product Early Adopter Segments (5 segments, 2026-03-22)
   ...
   ```
   Format: `{id} — {Description} ({segment count} segments, {date})`
4. Sort alphabetically by ID

If no populations found, tell the user: "No saved populations. Create one with: /agora:population create \"description\""

## If arguments start with "view":

1. Extract the population ID from arguments (everything after "view")
2. Read `{AGORA_HOME}/populations/{id}/population.md`
3. If file not found, list available populations and suggest alternatives
4. Display each segment with its key attributes:
   ```
   === {Population Description} ===
   ID: {id}
   Created: {date}
   Segments: {N}

   1. {Segment Label} ({size}%)
      Age: {range} | Income: {bracket} | Location: {type}
      Values: {values}
      Key anchors: Trust {level}, Price Sensitivity {level}, Change Openness {level}

   2. {Segment Label} ({size}%)
      ...
   ```

## Important Notes

- **Use absolute paths for EVERYTHING.** AGORA_HOME is the base for all file operations.
- **Create directories before writing files.** Always `mkdir -p` before any Write.
- **Verify sizes sum to 100%.** If generated segments don't sum correctly, adjust the largest segment.
