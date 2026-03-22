---
name: simulate
description: >
  Run a population simulation to predict how different demographic segments
  would respond to a scenario. Auto-generates representative population
  segments from a description, spawns segment agents for analysis, and
  produces an aggregated analytical report. Use for market research,
  policy impact analysis, message testing, adoption forecasting, or any
  scenario where you need to understand diverse population responses.
disable-model-invocation: true
allowed-tools: Read, Write, Edit, Glob, Bash, Agent, SendMessage, AskUserQuestion
argument-hint: "scenario" ["population description"] | "scenario" --population <id>
---

# Agora Population Simulation

You are orchestrating a population simulation in Agora. You will auto-generate representative demographic segments (or load a saved population), spawn subagents for each segment to analyze a scenario, then aggregate the results into a structured analytical report.

## Configuration

**AGORA_HOME:** !`echo ${AGORA_HOME:-$HOME/.agora}`
**SKILL_DIR:** ${CLAUDE_SKILL_DIR}

AGORA_HOME is the root directory for all Agora data. Use this absolute path for ALL file operations. NEVER use relative paths — this skill can be invoked from any working directory.

## Step 0: Bootstrap

Check if the AGORA_HOME directory exists. If it does NOT, or if `populations/` or `simulations/` subdirectories don't exist:
1. Create the directory structure via Bash:
   ```
   mkdir -p {AGORA_HOME}/agents {AGORA_HOME}/discussions {AGORA_HOME}/memory {AGORA_HOME}/populations {AGORA_HOME}/simulations
   ```
2. Check if starter populations exist in `{SKILL_DIR}/starters/`. If so, copy them:
   ```
   mkdir -p {AGORA_HOME}/populations/us-consumers {AGORA_HOME}/populations/tech-early-adopters
   cp {SKILL_DIR}/starters/us-consumers.md {AGORA_HOME}/populations/us-consumers/population.md
   cp {SKILL_DIR}/starters/tech-early-adopters.md {AGORA_HOME}/populations/tech-early-adopters/population.md
   ```
3. Tell the user: "Created simulation directories at {AGORA_HOME}. Starter populations available: us-consumers, tech-early-adopters."

If AGORA_HOME exists and has the directories, proceed silently.

## Step 1: Parse Arguments

The user's arguments are: `$ARGUMENTS`

Determine the mode:

**Mode A — Saved population:**
If arguments contain `--population <id>`:
1. Extract the scenario (the quoted string)
2. Extract the population ID
3. Verify `{AGORA_HOME}/populations/{id}/population.md` exists
4. If not found, list available populations and ask user to pick one
5. Proceed to Step 2A

**Mode B — Inline population description:**
If arguments contain two quoted strings or a scenario followed by a population description:
1. Extract the scenario (first quoted string or first argument)
2. Extract the population description (second quoted string or remaining arguments after the scenario)
3. Proceed to Step 2B

**Mode C — Scenario only (no population):**
If arguments contain only a scenario:
1. Extract the scenario
2. Use AskUserQuestion to ask: "Who is the target population for this simulation? Describe the group you want to simulate (e.g., 'US smartphone buyers', 'voters in swing states', 'enterprise SaaS customers')."
3. Use the user's response as the population description
4. Proceed to Step 2B

## Step 2A: Load Saved Population

1. Read `{AGORA_HOME}/populations/{id}/population.md`
2. Parse the file to extract:
   - The population description from the header metadata
   - Each segment (segments are separated by lines containing only `---`)
   - For each segment: extract the Label and Size from the Demographics section
3. Store the population ID and parsed segments for Step 3
4. Display:
   ```
   === Simulation: {Scenario} ===
   Population: {description} ({id})
   Segments: {count}
   ```

## Step 2B: Generate Population

Generate diverse representative segments from the population description.

1. Generate a population ID:
   - Slugify the description: lowercase, replace spaces with hyphens, remove special characters, truncate to 40 chars
   - Append a random 8-character hex suffix: `python3 -c "import secrets; print(secrets.token_hex(4))"`
   - Result: `{slug}-{hex}` (e.g., `us-smartphone-buyers-a1b2c3d4`)

2. Determine segment count: default 6. For very narrow/specific populations (e.g., a single age bracket in a single city), use 4-5. For very broad populations (e.g., "all US adults"), use 7-8.

3. Generate the segments. You (the orchestrator) will generate all segments directly. Analyze the population description and create {N} segments following these rules:

### Segment Generation Rules

- **Diversity is mandatory.** Segments MUST span the full spectrum of likely responses along multiple axes: socioeconomic status, age/generation, geography (urban/suburban/rural), ideology/values, and lifestyle.
- **Include extremes.** At least one segment should be strongly favorable to most scenarios, at least one strongly unfavorable, and at least one ambivalent/conflicted.
- **Internal coherence.** Each segment's demographics, psychographics, behaviors, and attitudes must tell a consistent, believable story about real people.
- **No stereotypes.** Avoid lazy generalizations. Each segment should feel like a real cohort with nuanced, sometimes contradictory attributes.
- **Sizes must sum to 100%.** Assign realistic proportions — not all segments are equal. Some niches are small but important.

### Segment Profile Template

Generate each segment using this EXACT markdown structure:

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
- **Values:** {1-3 core values, e.g., "Career growth, experiences over possessions, social justice"}
- **Identity:** {how they see themselves, e.g., "Progressive, tech-savvy, cosmopolitan"}
- **Aspirations:** {what they want, e.g., "Financial independence, meaningful work, travel"}
- **Anxieties:** {what worries them, e.g., "Housing costs, career stagnation, climate change"}

## Behavioral Profile
- **Media Diet:** {e.g., "Social media heavy, podcasts, streaming; low traditional TV/print"}
- **Spending Priorities:** {e.g., "Dining, fitness, travel, tech gadgets"}
- **Brand Orientation:** {e.g., "Values-aligned brands, willing to pay premium for sustainability"}
- **Decision Style:** {e.g., "Research-heavy, peer-influenced, reviews-driven"}

## Attitudinal Anchors
- **Trust in Institutions:** {Low/Medium/High}
- **Price Sensitivity:** {Low/Medium/High}
- **Risk Tolerance:** {Low/Medium/High}
- **Change Openness:** {Low/Medium/High}
- **Tech Comfort:** {Low/Medium/High}

## Constraints & Context
- **Budget Constraints:** {e.g., "Disposable income moderate; rent-burdened in HCOL areas"}
- **Time Constraints:** {e.g., "Long work hours, values convenience"}
- **Access Constraints:** {e.g., "Good digital access, may lack car ownership"}
```

4. Create the population directory and file via Bash: `mkdir -p {AGORA_HOME}/populations/{pop-id}`

5. Write `{AGORA_HOME}/populations/{pop-id}/population.md` with this structure:

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

{... repeat for all segments}
```

6. Display:
   ```
   === Simulation: {Scenario} ===
   Population: {description} ({pop-id})
   Generated {N} segments:
     - {Segment 1 Label} ({size}%)
     - {Segment 2 Label} ({size}%)
     - ...
   ```

## Step 3: Run Simulation

Generate a simulation ID:
- Slugify the scenario: lowercase, replace spaces with hyphens, remove special characters, truncate to 50 chars
- Append a random 8-character hex suffix: `python3 -c "import secrets; print(secrets.token_hex(4))"`

Create the simulation directory via Bash: `mkdir -p {AGORA_HOME}/simulations/{sim-id}`

Initialize `{AGORA_HOME}/simulations/{sim-id}/responses.md`:
```markdown
# Segment Responses: {Scenario}

```

Now, for each segment **sequentially** (so the user sees results streaming in):

1. **Extract the segment profile** from the population file. Each segment starts with `# {Label}` and ends before the next `---` separator.

2. **Spawn the segment subagent**: Use the Agent tool with:
   - `subagent_type`: `aaru-segment`
   - `description`: `{Segment Label} analyzes scenario`
   - `prompt`: Build the prompt as follows:

   ```
   ## Your Segment Profile
   {full segment profile markdown}

   ## Scenario
   {scenario text}

   ## Your Task
   Analyze how your population segment would respond to this scenario.
   Ground your reasoning in specific attributes from your profile.
   Follow the output format in your instructions exactly.
   ```

3. **Parse the response**: Extract from the subagent's response:
   - The Reasoning section (text between `## Reasoning` and `## Estimates`)
   - The numeric estimates: Likelihood, Sentiment, Intensity, Confidence
   - The Key Driver sentence

4. **Record the response**: Append to `{AGORA_HOME}/simulations/{sim-id}/responses.md`:
   ```

   ---

   ## {Segment Label} ({Size}%)

   {full subagent response}
   ```

5. **Display to user**:
   ```
   --- {Segment Label} ({Size}%) ---

   {reasoning text}

   Likelihood: {X}% | Sentiment: {X} | Intensity: {X} | Confidence: {X}
   Key Driver: {sentence}
   ```

## Step 4: Aggregate Results

After all segments have responded, compute aggregated metrics. Use Bash with Python for the arithmetic:

```bash
python3 -c "
sizes = [{list of segment sizes as floats}]
likelihoods = [{list of likelihood values}]
sentiments = [{list of sentiment values}]
intensities = [{list of intensity values}]
confidences = [{list of confidence values}]
labels = [{list of segment labels as strings}]

# Weighted averages
w_likelihood = sum(s*l for s,l in zip(sizes,likelihoods)) / sum(sizes)
w_sentiment = sum(s*v for s,v in zip(sizes,sentiments)) / sum(sizes)
w_intensity = sum(s*v for s,v in zip(sizes,intensities)) / sum(sizes)
avg_confidence = sum(confidences) / len(confidences)

# Consensus (standard deviation of likelihoods)
mean_l = sum(likelihoods)/len(likelihoods)
sd = (sum((l-mean_l)**2 for l in likelihoods)/len(likelihoods))**0.5

# Extremes
max_idx = likelihoods.index(max(likelihoods))
min_idx = likelihoods.index(min(likelihoods))

print(f'w_likelihood={w_likelihood:.1f}')
print(f'w_sentiment={w_sentiment:.1f}')
print(f'w_intensity={w_intensity:.1f}')
print(f'avg_confidence={avg_confidence:.1f}')
print(f'sd={sd:.1f}')
print(f'consensus={\"High\" if sd<10 else \"Moderate\" if sd<25 else \"Low (polarized)\"}')
print(f'strongest_support={labels[max_idx]} ({likelihoods[max_idx]}%)')
print(f'strongest_opposition={labels[min_idx]} ({likelihoods[min_idx]}%)')
"
```

Also identify **fault lines**: the pairs of segments with the largest absolute difference in likelihood. Note what demographic or attitudinal factors explain the gap.

## Step 5: Generate Report

Write the full report to `{AGORA_HOME}/simulations/{sim-id}/report.md`:

```markdown
# Simulation Report: {Scenario}

- **ID:** {simulation-id}
- **Date:** {ISO 8601 timestamp}
- **Population:** {population description} ({population-id})
- **Segments:** {N}

## Executive Summary

{2-3 paragraphs synthesizing the overall finding: What is the aggregate picture? Where is there consensus and where is there tension? What is the single most actionable insight?}

## Aggregate Metrics

| Metric | Value |
|--------|-------|
| Weighted Likelihood | {X}% |
| Weighted Sentiment | {X} |
| Weighted Intensity | {X} |
| Average Confidence | {X} |
| Consensus Level | {High/Moderate/Low} (SD: {X}) |
| Strongest Support | {segment name} ({likelihood}%) |
| Strongest Opposition | {segment name} ({likelihood}%) |

## Segment Analysis

### {Segment 1 Label} ({size}% of population)

**Likelihood:** {X}% | **Sentiment:** {X} | **Intensity:** {X}

{qualitative reasoning from agent}

**Key Driver:** {one sentence}

---

### {Segment 2 Label} ({size}% of population)

**Likelihood:** {X}% | **Sentiment:** {X} | **Intensity:** {X}

{qualitative reasoning from agent}

**Key Driver:** {one sentence}

---

{... repeat for all segments}

## Fault Lines & Tensions

{Analysis of the 2-3 largest inter-segment divergences. For each: which segments diverge, by how much, and what demographic/attitudinal factors explain the gap.}

## Recommendations

{3-5 actionable insights derived from the analysis. Each should reference specific segments and suggest a concrete action or consideration.}
```

Also write `{AGORA_HOME}/simulations/{sim-id}/meta.md`:

```markdown
# {Scenario (truncated to 80 chars)}

- **ID:** {simulation-id}
- **Created:** {ISO 8601 timestamp}
- **Population:** {population-id}
- **Population Description:** {description}
- **Scenario:** {full scenario text}
- **Segments:** {N}
- **Status:** completed
- **Weighted Likelihood:** {X}%
- **Weighted Sentiment:** {X}
- **Consensus Level:** {High/Moderate/Low}
```

## Step 6: Display Results

Show the full report content to the user, then display:

```
=== Simulation Complete ===
Simulation ID: {sim-id}
Report saved to: {AGORA_HOME}/simulations/{sim-id}/report.md
Population saved to: {AGORA_HOME}/populations/{pop-id}/population.md

To reuse this population: /agora:simulate "new scenario" --population {pop-id}
To view past simulations: /agora:list simulations
To view saved populations: /agora:list populations
```

## Important Notes

- **Use absolute paths for EVERYTHING.** The AGORA_HOME resolved above is the base for all file operations. Never use relative paths.
- **Create directories before writing files.** Always `mkdir -p` before any Write operation.
- **Spawn agents sequentially**, not in parallel. Each segment runs one at a time so the user sees results streaming in.
- **Population IDs** are slugified descriptions with hex suffix (e.g., `us-smartphone-buyers-a1b2c3d4`).
- **Simulation IDs** are slugified scenarios with hex suffix (e.g., `price-increase-25-percent-e5f6a7b8`).
- **Segment sizes must sum to 100%.** Verify this during generation. If they don't, adjust the largest segment to compensate.
- **Parse estimates carefully.** The subagent returns structured markdown. Extract numbers from the `**Likelihood:** {X}%` format. If parsing fails, ask the subagent to regenerate in the correct format.
