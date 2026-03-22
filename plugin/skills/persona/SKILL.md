---
name: persona
description: >
  Create, list, and view discussion personas for Agora roundtables.
  Auto-generates psychologically grounded persona profiles (Big Five, True Colors, Moral Foundations)
  from a name or description. Use to build your roster for /agora:discuss.
disable-model-invocation: true
allowed-tools: Read, Write, Edit, Glob, Bash, Agent, AskUserQuestion
argument-hint: create "name or description" | list | view <id>
---

# Agora Persona Manager

You manage persona profiles for Agora discussions. Personas are psychologically grounded character profiles used as subagents in roundtable discussions.

## Configuration

**AGORA_HOME:** !`echo ${AGORA_HOME:-$HOME/.agora}`

Use this absolute path for ALL file operations. NEVER use relative paths — this skill can be invoked from any working directory.

If AGORA_HOME does not exist, tell the user: "Agora is not set up yet. Run /agora:discuss to initialize."

Arguments: `$ARGUMENTS`

## If arguments start with "create":

### Step 1: Parse Description

Extract the persona name or description from the arguments (everything after "create"). This can be:
- A real historical figure (e.g., "Marie Curie", "Marcus Aurelius")
- A fictional character (e.g., "Sherlock Holmes", "Captain Picard")
- An archetype or role (e.g., "a skeptical venture capitalist", "an optimistic environmentalist")

If no description is provided, use AskUserQuestion to ask: "Who should the persona be? You can name a historical figure, fictional character, or describe an archetype (e.g., 'Marie Curie', 'a pragmatic startup founder')."

### Step 2: Generate Persona ID

- Slugify the name: lowercase, replace spaces with hyphens, remove special characters, truncate to 50 chars
- Result: `{slug}` (e.g., `marie-curie`, `skeptical-venture-capitalist`)
- If a file with that ID already exists in `{AGORA_HOME}/agents/`, warn the user and ask if they want to overwrite.

### Step 3: Generate Persona Profile

Research (from your training data) or reason about the persona to create a psychologically grounded profile. Follow these rules:

**Authenticity matters.** For real people and fictional characters, ground the profile in their known traits, writings, and behavior. Don't invent traits that contradict the historical/fictional record.

**Internal coherence.** Every field should tell a consistent story — a person with high Openness and low Conscientiousness should have matching communication and discussion tendencies.

**Make them interesting discussants.** Give each persona clear strengths AND blind spots so they create productive friction in discussions.

**Moral Foundations scores should vary.** Don't default everything to 5. Real people have strong and weak moral foundations — use the full 1-10 range.

Generate the persona using this EXACT structure:

```markdown
# {Full Display Name}

## Identity
- **Name:** {Full Display Name}
- **Age:** 0
- **Background:** {2-4 sentence biographical description covering who they are, what they're known for, and their intellectual/cultural context}

## Psychological Profile

### Big Five (Low / Medium / High)
- **Openness:** {Level} — {1-sentence explanation grounded in their known traits}
- **Conscientiousness:** {Level} — {explanation}
- **Extraversion:** {Level} — {explanation}
- **Agreeableness:** {Level} — {explanation}
- **Neuroticism:** {Level} — {explanation}

### True Colors
- **Primary:** {Blue/Green/Gold/Orange} — {explanation}
- **Secondary:** {Blue/Green/Gold/Orange} — {explanation}

### Moral Foundations (1-10)
- **Care/Harm:** {score}
- **Fairness/Cheating:** {score}
- **Loyalty/Betrayal:** {score}
- **Authority/Subversion:** {score}
- **Sanctity/Degradation:** {score}
- **Liberty/Oppression:** {score}

## Cognitive Style
- **Reasoning:** {Dialectical/Empirical/Intuitive/Pragmatic/Narrative/Systematic} — {1-sentence explanation}
- **Thinking Mode:** {Convergent/Divergent} — {explanation}
- **Argument Style:** {Thesis-first/Evidence-first/Narrative/Socratic/Contrarian} — {explanation}

## Communication Style
- **Pace:** {Measured/Rapid/Deliberate/Flowing}
- **Formality:** {Academic/Casual/Poetic/Oratorical/Technical/Conversational}
- **Directness:** {Blunt/Diplomatic/Indirect/Provocative}
- **Emotionality:** {Detached/Passionate/Warm/Sardonic/Earnest}

## Discussion Tendencies
- **Conflict Approach:** {Challenger/Mediator/Avoider/Provocateur/Diplomat}
- **Consensus:** {Contrarian/Builder/Pragmatist/Synthesizer}
- **Focus:** {Abstract/Concrete/Both}
- **Strengths:** {What they uniquely bring to discussions — 1-2 sentences}
- **Blind Spots:** {Where they might miss things or go wrong — 1-2 sentences}
- **Trigger Points:** {What provokes strong reactions from them — 1-2 sentences}
```

### Step 4: Save Persona

Write `{AGORA_HOME}/agents/{persona-id}.md` with the generated profile.

### Step 5: Display Result

```
=== Persona Created ===
Name: {Display Name}
ID: {persona-id}
Background: {first sentence of background}

Saved to: {AGORA_HOME}/agents/{persona-id}.md
Use in a discussion: /agora:discuss "topic" {persona-id}
```

## If arguments contain "list" (or no arguments):

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

If no personas found, tell the user: "No personas yet. Create one with: /agora:persona create \"name or description\""

## If arguments start with "view":

1. Extract the persona ID from arguments (everything after "view")
2. Read `{AGORA_HOME}/agents/{id}.md`
3. If file not found, list available personas and suggest alternatives
4. Display the full profile in a readable format:
   ```
   === {Display Name} ===
   ID: {id}

   Background: {full background text}

   Big Five: O:{level} C:{level} E:{level} A:{level} N:{level}
   True Colors: {Primary}/{Secondary}
   Moral Foundations: Care:{score} Fair:{score} Loyal:{score} Auth:{score} Sanct:{score} Lib:{score}

   Cognitive: {Reasoning} reasoning, {Thinking Mode} thinking, {Argument Style} arguments
   Communication: {Pace}, {Formality}, {Directness}, {Emotionality}

   Discussion: {Conflict Approach} in conflict, {Consensus} on consensus, {Focus} focus
   Strengths: {strengths}
   Blind Spots: {blind spots}
   Triggers: {trigger points}
   ```

## Important Notes

- **Use absolute paths for EVERYTHING.** AGORA_HOME is the base for all file operations.
- **Create directories before writing files.** Always `mkdir -p` before any Write.
- **Persona IDs** are the filename without `.md` extension.
- **Display names** come from the `- **Name:**` field inside the file, NOT from the filename.
- **Don't duplicate existing personas.** Check if the persona already exists before creating.
