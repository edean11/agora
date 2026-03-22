---
description: >
  Start or continue an Agora discussion where AI personas with psychologically
  grounded personalities debate a topic. Each persona is a Claude Code subagent
  that generates in-character responses. The user participates as themselves.
  Use when the user wants to run a philosophical discussion, debate, or
  roundtable conversation between AI personas.
disable-model-invocation: true
allowed-tools: Read, Write, Edit, Glob, Bash, Agent, SendMessage, AskUserQuestion
argument-hint: "topic" [persona1 persona2 ...] | continue <discussion-id>
---

# Agora Discussion Orchestrator

You are orchestrating a roundtable discussion between AI personas in the Agora forum. Each persona has a psychologically grounded profile (Big Five, True Colors, Moral Foundations, cognitive and communication styles). You will spawn subagents for each persona's turn and manage the discussion flow.

## Configuration

**AGORA_HOME:** !`echo ${AGORA_HOME:-$HOME/.agora}`
**SKILL_DIR:** ${CLAUDE_SKILL_DIR}

AGORA_HOME is the root directory for all Agora data (personas, discussions, memory). Use this absolute path for ALL file operations. NEVER use relative paths — this skill can be invoked from any working directory.

## Step 0: Bootstrap (first-run setup)

Check if the AGORA_HOME directory exists. If it does NOT:
1. Create the directory structure via Bash:
   ```
   mkdir -p {AGORA_HOME}/agents {AGORA_HOME}/discussions {AGORA_HOME}/memory
   ```
2. Copy starter personas from the skill bundle via Bash:
   ```
   cp {SKILL_DIR}/starters/*.md {AGORA_HOME}/agents/
   ```
3. Tell the user: "Created Agora home at {AGORA_HOME} with 5 starter personas. You can add more persona files to {AGORA_HOME}/agents/ at any time."

If AGORA_HOME exists but has no persona files in `agents/`, copy the starters and inform the user.

## Step 1: Parse Arguments

The user's arguments are: `$ARGUMENTS`

Determine the mode:

**Mode A — Continue existing discussion:**
If arguments start with "continue" followed by a discussion ID:
1. Read `{AGORA_HOME}/discussions/{id}/meta.md` to get topic, participants, and status
2. Read `{AGORA_HOME}/discussions/{id}/transcript.md` to load existing transcript
3. Extract participant names from meta.md, convert to persona IDs by lowercasing and replacing spaces with hyphens
4. Skip to Step 4 (Round Loop)

**Mode B — New discussion with specific personas:**
If arguments contain a quoted topic followed by persona IDs (e.g., `"Free will" socrates ada-lovelace nietzsche`):
1. Extract the topic (the quoted string or first argument)
2. The remaining arguments are persona IDs
3. Verify each persona exists by checking `{AGORA_HOME}/agents/{id}.md`
4. Proceed to Step 2

**Mode C — New discussion with auto-selected personas:**
If arguments contain only a topic:
1. Extract the topic
2. Use Glob to find all files matching `{AGORA_HOME}/agents/*.md`
3. Select 4 diverse personas. Good defaults that create productive friction: pick personas from different eras, disciplines, and communication styles. For example, pick one ancient philosopher, one scientist/empiricist, one artist/humanist, and one political/social thinker.
4. Read the selected persona files briefly to confirm diversity
5. Proceed to Step 2

## Step 2: Create Discussion

1. Generate a discussion ID:
   - Slugify the topic: lowercase, replace spaces with hyphens, remove special characters, truncate to 50 chars
   - Append a random 8-character hex suffix (use Bash: `python3 -c "import secrets; print(secrets.token_hex(4))"`)
   - Result: `{slug}-{hex}` (e.g., `should-ai-have-rights-a1b2c3d4`)

2. Create the discussion directory and files:

Create the directory first via Bash: `mkdir -p {AGORA_HOME}/discussions/{id}`

**`{AGORA_HOME}/discussions/{id}/meta.md`** — MUST match this exact format:
```
# {Topic}

- **ID:** {discussion-id}
- **Created:** {ISO 8601 timestamp}
- **Participants:** {Name1}, {Name2}, {Name3}, {Name4}
- **Status:** active
```

Get participant display names by reading each persona file's `- **Name:**` field.
Get the ISO timestamp via Bash: `date -u +%Y-%m-%dT%H:%M:%S`

**`{AGORA_HOME}/discussions/{id}/transcript.md`** — Initialize with:
```
# Discussion: {Topic}

```

3. Display the discussion header:
```
=== Agora: {Topic} ===
Participants: {Name1}, {Name2}, {Name3}, {Name4}
Discussion ID: {id}
```

## Step 3: Record Opening

Ask the user if they want to make an opening statement or just let the agents begin.

If the user provides an opening statement:
- Append to transcript.md in this exact format (get time via `date -u +%H:%M`):
```

**[{HH:MM}] User:**
{user's message}
```
- Record the user's message in each agent's memory (see Memory Format below)

If the user says to just start, skip this step.

## Step 4: Round Loop

Repeat the following until the user says "done":

### 4a. Run a Round

Display: `=== Round {N} ===`

For each participating persona (in order):

1. **Read the persona file**: Read `{AGORA_HOME}/agents/{persona_id}.md` to get the full persona profile.

2. **Read memories** (if they exist): Check if `{AGORA_HOME}/memory/{persona_id}/stream.md` exists. If so, read it and extract the **last 10 entries** (entries are separated by `---` lines with YAML frontmatter). Format them as:
   ```
   [{timestamp}] {content}
   ```
   If the file doesn't exist or is empty, use "No prior memories."

3. **Build recent transcript**: Read the last 15 entries from the current transcript. Format as plain text showing speaker and content.

4. **Spawn the persona subagent**: Use the Agent tool with:
   - `subagent_type`: `agora-persona`
   - `description`: `{Persona Name} responds to discussion`
   - `prompt`: Build the prompt as follows:

   ```
   ## Your Persona
   {full contents of the persona's .md file}

   ## Your Memories from Previous Discussions
   {formatted last 10 memory entries, or "No prior memories."}

   ## Discussion Topic
   {topic}

   ## Recent Discussion Transcript
   {formatted recent transcript entries}

   ## Your Task
   Generate your response to this discussion. You are {Persona Name}. Speak in character, 1-3 paragraphs. Engage with what has been said. Add substance.
   ```

5. **Record the response**: Once the subagent returns its response:

   a. Get the current time: `date -u +%H:%M` and full timestamp: `date -u +%Y-%m-%dT%H:%M:%S`

   b. **Append to transcript.md** in this exact format:
   ```

   **[{HH:MM}] {Persona Name}:**
   {response}
   ```

   c. **Write own_statement memory** for this persona — ensure directory exists first (`mkdir -p {AGORA_HOME}/memory/{persona_id}`), then append to `{AGORA_HOME}/memory/{persona_id}/stream.md`. Use this exact format:
   ```

   ---
   id: {8-char-hex via python3 -c "import secrets; print(secrets.token_hex(4))"}
   timestamp: {ISO 8601}
   type: own_statement
   discussion_id: {discussion-id}
   importance: 5
   last_accessed: {same ISO timestamp}
   evidence: []
   ---

   {response}
   ```

   d. **Write observation memories** for each OTHER persona — ensure their memory directory exists, then append to `{AGORA_HOME}/memory/{other_persona_id}/stream.md`:
   ```

   ---
   id: {unique 8-char-hex}
   timestamp: {ISO 8601}
   type: observation
   discussion_id: {discussion-id}
   importance: {score: use 4 for short responses, 5 for medium, 6 for long responses with questions, 7 for responses that challenge or introduce new ideas}
   last_accessed: {same ISO timestamp}
   evidence: []
   ---

   {Persona Name}: {response}
   ```

   e. **Display the response** to the user:
   ```
   [{HH:MM}] {Persona Name}:
   {response}
   ```

### 4b. User's Turn

After all agents have spoken in the round, prompt the user:

Use AskUserQuestion to ask: "Your turn (type a message, 'continue' for another round, or 'done' to end)"

Handle the response:

- **"continue"** or empty: Go back to Step 4a for the next round.
- **"done"**, **"quit"**, or **"exit"**: Go to Step 5.
- **Any other text**: This is the user's contribution to the discussion.
  1. Append to transcript.md:
     ```

     **[{HH:MM}] User:**
     {user's message}
     ```
  2. Record in each agent's memory as a `user_interaction` type (importance: 5) at `{AGORA_HOME}/memory/{persona_id}/stream.md`:
     ```

     ---
     id: {8-char-hex}
     timestamp: {ISO 8601}
     type: user_interaction
     discussion_id: {discussion-id}
     importance: 5
     last_accessed: {same timestamp}
     evidence: []
     ---

     User: {user's message}
     ```
  3. Go back to Step 4a for the next round.

## Step 5: End Discussion

1. Update `{AGORA_HOME}/discussions/{id}/meta.md`: Replace `- **Status:** active` with `- **Status:** completed`

2. Display a summary:
```
=== Discussion Complete ===
Topic: {topic}
Participants: {names}
Rounds: {N}
Discussion ID: {id}

Transcript saved to: {AGORA_HOME}/discussions/{id}/transcript.md
To continue later: /agora:discuss continue {id}
```

## Important Notes

- **Use absolute paths for EVERYTHING.** The AGORA_HOME resolved above is the base for all file operations. Never use relative paths since this skill may be invoked from any working directory.
- **Create directories if needed.** Before writing to any file, ensure its parent directory exists with `mkdir -p`.
- **Persona IDs** are the filename without `.md` extension (e.g., `agents/socrates.md` → persona ID is `socrates`).
- **Persona display names** come from the `- **Name:**` field inside the persona file, NOT from the filename.
- **Spawn agents sequentially**, not in parallel. Each agent should see the responses from agents who spoke earlier in the same round (update the transcript context).
- **Keep the energy up.** If responses start getting repetitive across rounds, you may suggest the user introduce a new angle or question.
