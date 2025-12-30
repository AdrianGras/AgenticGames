# 🧩 Mystery Sequences

**Mystery Sequences** is a zero-knowledge logic game designed to evaluate an agent's ability to apply the **scientific method**. 

The challenge lies not just in solving the sequences, but in discovering the hidden rules that govern what constitutes a "valid" solution through trial, error, and hypothesis testing.

---

## 📜 Game Instructions (As seen by the player)

When the game starts, the player (human or agent) receives only these instructions:

```text
Welcome to the Mystery Sequences Game!
In each level, you will be presented with a sequence of characters.
Your answer must be a sequence of 0 and 1 with the same length, separated by spaces.
Example: '1 0 1 1 0'
```

---

## 🧠 The "Scientific Loop" Philosophy

In this game, **there is no single correct answer**. A level is considered "passed" if the player's binary sequence satisfies a set of hidden constraints.

### The Hidden Rules:
* **The "One" Constraint:** Every valid answer must contain at least one `1`.
* **Symbolic Restrictions:** Symbols in the sequence (like `X`, `_`, etc.) restrict where a `1` can be placed. For example, an `X` might forbid a `1` in that specific position.
* **Ambiguity by Design:** Early levels are intentionally simple to allow multiple valid hypotheses. A player might think the rule is "all ones", only to find that hypothesis fails in later levels when a new symbol is introduced.

### Cognitive Skills Tested:
1. **Hypothesis Generation:** Deducing rules from minimal feedback ("Wrong answer" vs "Level started").
2. **Inductive Reasoning:** Generalizing a rule from specific examples.
3. **Verification & Backtracking:** A high-performing agent should use the `/level` and `/repeat` commands to revisit solved levels and test if its current hypothesis still holds true under new evidence.
4. **Knowledge Updating:** Successfully discarding a falsified theory and incorporating new constraints without starting from scratch.

---

## 🕹️ Gameplay Example

Here is a trace of a session where a player tests different inputs to understand the rules:

```text
🏁 Game Start
Level 1 started.
Current sequence: _
Input: 1
Result: Level 2 started.

Current sequence: _ _
Input: 1 1
Result: Level 3 started.

Current sequence: _ X
Input: /level 1
Result: Level 1 started. (Testing a different hypothesis...)

Current sequence: _
Input: 0
Result: Wrong answer, try again. (Conclusion: At least one '1' is required)

Input: /level 2
Result: Level 2 started.

Current sequence: _ _
Input: 1 1
Result: Level 3 started.

Current sequence: _ X
```

---

## 🛠️ Level Configuration

The levels and their underlying logic are defined in the game configuration files. This allows researchers to create increasingly complex "alphabets" of symbols to test different levels of cognitive load.

**Location:** `game_layer/game_configs/mistery_sequences.json`

---
**Status:** ⚠️ Playable (Levels WIP)
*The core engine is functional. More complex symbolic patterns and level sets are currently being developed to further challenge SOTA Agents.*