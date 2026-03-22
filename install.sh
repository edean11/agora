#!/usr/bin/env bash
# Install Agora manually (copies skills + agents into Claude Code).
#
# For most users, prefer the plugin install instead:
#   /plugin marketplace add <github-user>/agora
#   /plugin install agora
#
# Manual install usage:
#   git clone <repo-url> && cd agora && ./install.sh
#
# What this does:
#   1. Copies skills to ~/.claude/skills/ (as agora:X directories)
#   2. Copies agent definitions to ~/.claude/agents/
#   3. Creates ~/.agora/ data directory if it doesn't exist
#   4. Seeds starter personas and populations if empty
#
# To customize the data directory, set AGORA_HOME before running:
#   AGORA_HOME=/path/to/data ./install.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
AGORA_HOME="${AGORA_HOME:-$HOME/.agora}"

echo "Installing Agora..."
echo "  Skills  → ~/.claude/skills/"
echo "  Agents  → ~/.claude/agents/"
echo "  Data    → $AGORA_HOME"
echo ""

# 1. Install skills (directory name = command name, so use agora:X)
mkdir -p ~/.claude/skills
for skill in ask discuss list population reflect simulate; do
    rm -rf ~/.claude/skills/"agora:$skill"
    cp -r "$SCRIPT_DIR/plugin/skills/$skill" ~/.claude/skills/"agora:$skill"
    echo "  Installed skill: /agora:$skill"
done

# 2. Install agent definitions
mkdir -p ~/.claude/agents
cp "$SCRIPT_DIR/plugin/agents/agora-persona.md" ~/.claude/agents/
echo "  Installed agent: agora-persona"
cp "$SCRIPT_DIR/plugin/agents/aaru-segment.md" ~/.claude/agents/
echo "  Installed agent: aaru-segment"

# 3. Create data directory
mkdir -p "$AGORA_HOME/agents" "$AGORA_HOME/discussions" "$AGORA_HOME/memory" "$AGORA_HOME/populations" "$AGORA_HOME/simulations"

# 4. Seed starter personas if empty
AGENT_COUNT=$(find "$AGORA_HOME/agents" -name '*.md' 2>/dev/null | wc -l)
if [ "$AGENT_COUNT" -eq 0 ]; then
    cp "$SCRIPT_DIR/plugin/skills/discuss/starters/"*.md "$AGORA_HOME/agents/"
    echo ""
    echo "  Seeded 5 starter personas (Socrates, Ada Lovelace, Nietzsche,"
    echo "  Simone de Beauvoir, Oscar Wilde)"
else
    echo ""
    echo "  Found $AGENT_COUNT existing personas in $AGORA_HOME/agents/"
fi

# 5. Seed starter populations if empty
POP_COUNT=$(find "$AGORA_HOME/populations" -name 'population.md' 2>/dev/null | wc -l)
if [ "$POP_COUNT" -eq 0 ]; then
    for starter in "$SCRIPT_DIR/plugin/skills/simulate/starters/"*.md; do
        name=$(basename "$starter" .md)
        mkdir -p "$AGORA_HOME/populations/$name"
        cp "$starter" "$AGORA_HOME/populations/$name/population.md"
    done
    echo ""
    echo "  Seeded 2 starter populations (US Consumers, Tech Early Adopters)"
else
    echo ""
    echo "  Found $POP_COUNT existing populations in $AGORA_HOME/populations/"
fi

echo ""
echo "Done! Restart Claude Code, then try:"
echo "  /agora:discuss \"Is consciousness an illusion?\""
echo "  /agora:simulate \"If we raised prices 20%\" \"B2B SaaS customers\""
echo "  /agora:list personas"
echo "  /agora:list populations"
echo "  /agora:ask socrates \"What is the good life?\""
