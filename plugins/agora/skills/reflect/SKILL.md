---
description: >
  Trigger reflection for an Agora persona. Reads recent memories, generates
  reflection questions, and synthesizes insights. Use when you want an agent
  to consolidate what they've learned across discussions.
disable-model-invocation: true
allowed-tools: Read, Write, Glob, Bash, Agent
argument-hint: <persona-id>
---

# Agora Reflection

**AGORA_HOME:** !`echo $HOME/.agora`

Use this absolute path for ALL file operations. Never use relative paths.

If AGORA_HOME does not exist, tell the user: "Agora is not set up yet. Run /agora:discuss to initialize."

Arguments: `$ARGUMENTS` (a persona ID, e.g., `socrates`)

## Steps

1. **Read persona**: Read `{AGORA_HOME}/agents/{persona_id}.md`. If not found, show available personas via Glob `{AGORA_HOME}/agents/*.md`.

2. **Read memories**: Read `{AGORA_HOME}/memory/{persona_id}/stream.md`. Extract the **last 50 entries** (delimited by `---` with YAML frontmatter). If fewer than 5 entries exist, tell the user there aren't enough memories to reflect on yet.

3. **Generate reflection questions**: Spawn a general-purpose Agent with this prompt:

   ```
   You are analyzing recent experiences and observations to identify salient themes.

   Here are recent memories from {Persona Name}:

   {formatted last 50 memory entries, showing timestamp and content}

   Generate exactly 3 high-level questions or themes that capture the most important
   patterns, tensions, or insights in these memories. Questions should be:
   - Broad and thought-provoking, not narrow or specific
   - Identify patterns across multiple memories
   - Focus on underlying values, motivations, or conflicts

   Output a numbered list (1. 2. 3.) with one question per line. Nothing else.
   ```

   Parse the 3 questions from the response.

4. **Synthesize insights**: For each of the 3 questions, spawn the `agora-persona` subagent:

   ```
   ## Your Persona
   {full persona file contents}

   ## Reflection Task
   You are reflecting on your recent experiences and discussions. Based on the
   following memories, answer this reflection question with a thoughtful,
   introspective paragraph.

   ## Question
   {question}

   ## Your Recent Memories
   {formatted last 50 memory entries}

   ## Your Task
   Write a single reflective paragraph answering this question. Be introspective
   and analytical. Connect multiple memories. Identify deeper patterns. Write in
   first person as yourself reflecting privately.
   ```

5. **Persist reflections**: For each question/insight pair:

   a. Ensure directory exists: `mkdir -p {AGORA_HOME}/memory/{persona_id}`

   b. Append to `{AGORA_HOME}/memory/{persona_id}/reflections.md`:
   ```
   ---
   ## Reflection: {ISO 8601 timestamp}

   **Question:** {question}
   **Evidence:** {comma-separated IDs of last 8 memory entries}

   {insight paragraph}

   ```

   c. Append a reflection-type memory to `{AGORA_HOME}/memory/{persona_id}/stream.md`:
   ```

   ---
   id: {8-char-hex via python3 -c "import secrets; print(secrets.token_hex(4))"}
   timestamp: {ISO 8601 via date -u +%Y-%m-%dT%H:%M:%S}
   type: reflection
   discussion_id:
   importance: 8
   last_accessed: {same timestamp}
   evidence: [{comma-separated IDs of last 8 memory entries}]
   ---

   {insight paragraph}
   ```

6. **Display results**:
   ```
   === Reflection: {Persona Name} ===

   Q1: {question}
   {insight}

   Q2: {question}
   {insight}

   Q3: {question}
   {insight}

   Reflections saved to: {AGORA_HOME}/memory/{persona_id}/reflections.md
   ```
