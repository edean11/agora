---
name: ask
description: >
  Ask a direct question to an Agora persona. The persona responds in character,
  drawing on their psychological profile and memories from past discussions.
disable-model-invocation: true
allowed-tools: Read, Write, Edit, Glob, Bash, Agent, SendMessage, AskUserQuestion
argument-hint: <persona-id> "question"
---

# Agora Ask

**AGORA_HOME:** !`echo ${AGORA_HOME:-$HOME/.agora}`

Use this absolute path for ALL file operations. Never use relative paths.

If AGORA_HOME does not exist, tell the user: "Agora is not set up yet. Run /agora:discuss to initialize."

Arguments: `$ARGUMENTS`

Parse the arguments: the first word is the persona ID, everything after is the question.

## Steps

1. **Read the persona file**: Read `{AGORA_HOME}/agents/{persona_id}.md`. If it doesn't exist, list available personas with Glob `{AGORA_HOME}/agents/*.md` and suggest alternatives.

2. **Read memories**: If `{AGORA_HOME}/memory/{persona_id}/stream.md` exists, read the last 10 entries. Format as timestamped lines.

3. **Spawn persona subagent**: Use the Agent tool with:
   - `subagent_type`: `agora-persona`
   - `description`: `{Persona Name} answers a question`
   - `prompt`:
     ```
     ## Your Persona
     {full persona file contents}

     ## Your Memories from Previous Discussions
     {formatted last 10 memory entries, or "No prior memories."}

     ## Question
     A user has asked you directly: {question}

     ## Your Task
     Answer this question thoughtfully and in character. Draw on your persona's values,
     knowledge, and experiences. Be authentic to who you are. 1-3 paragraphs.
     ```

4. **Display the response**:
   ```
   [{Persona Name}]
   {response}
   ```

5. **Record in memory**: Ensure directory exists (`mkdir -p {AGORA_HOME}/memory/{persona_id}`), then append to `{AGORA_HOME}/memory/{persona_id}/stream.md`:
   ```

   ---
   id: {8-char-hex via python3 -c "import secrets; print(secrets.token_hex(4))"}
   timestamp: {ISO 8601 via date -u +%Y-%m-%dT%H:%M:%S}
   type: user_interaction
   discussion_id: direct_question
   importance: 5
   last_accessed: {same timestamp}
   evidence: []
   ---

   User: {question}
   Answer: {response}
   ```
