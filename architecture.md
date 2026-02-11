# Refined Cover Letter Agent Architecture - Concise Plan

## Flow Diagram

```
Input (Job URL) 
    ↓
[1] Classify → Gemini Flash 2.0 ($0.0001)
    ↓
    ✋ HUMAN: Verify category? [Y/N/Override]
    ↓
[2] Load Biography Files
    - Finance: Info_CL_Fin_GPT.md, Info_CL_Fin_Claude.md  
    - Engineering: Info_CL_Eng_GPT.md, Info_CL_Eng_Claude.md
    ↓
[3] Parallel Generation (2 models only)
    - Generator A: GPT-4o ($0.02)
    - Generator B: Claude Sonnet 4.5 ($0.03)
    ↓
[4] Critic Analysis → Claude Opus 4.5 ($0.05)
    - Reviews BOTH versions
    - Identifies: What's good in A, what's good in B
    - Identifies: What's bad in A, what's bad in B
    - Creates: FUSION version (best parts combined)
    ↓
    ✋ HUMAN: Review fusion version
        Input:
        - Quality score (1-10)
        - What you like
        - What you DON'T like
        - Save preferences → local preferences.json
    ↓
    Decision: Approve? 
        YES → [8] Save & Done
        NO ↓
    ↓
[5] ✋ HUMAN: Choose editor model
    [ ] Fine model: Claude Opus 4.5 ($0.05)
    [ ] Balanced model: GPT-4o ($0.02)
    ↓
[6] Editor implements your feedback
    - Uses your preferences.json
    - Your specific comments this round
    ↓
[7] ✋ HUMAN: Review edited version
    - Like it? Save
    - Don't like? → Choose model + feedback → Loop to [6]
    ↓
[8] APPROVED → Save final version
```

---

## Detailed Node Breakdown

### Node 1: Classification (Gemini Flash 2.0)
**Input:** Job description  
**Output:** "engineering" or "finance" + confidence  
**Cost:** ~$0.0001

```
HUMAN CHECKPOINT:
┌─────────────────────────────┐
│ Category: ENGINEERING       │
│ Confidence: 94%             │
│                             │
│ [✓ Correct] [X Change]      │
└─────────────────────────────┘
```

---

### Node 2: Load Biography Files
**Logic:**
```python
if category == "finance":
    load ["Info_CL_Fin_GPT.md", "Info_CL_Fin_Claude.md"]
elif category == "engineering":
    load ["Info_CL_Eng_GPT.md", "Info_CL_Eng_Claude.md"]
```

**Note:** Same content, different generation models
- GPT file will inform GPT-4o generator
- Claude file will inform Sonnet 4.5 generator

---

### Node 3: Parallel Generation

**Generator A: GPT-4o**
- Input: Job description + Info_CL_[category]_GPT.md
- Prompt: Professional cover letter, 300-400 words
- Cost: ~$0.02

**Generator B: Claude Sonnet 4.5**
- Input: Job description + Info_CL_[category]_Claude.md  
- Prompt: Professional cover letter, 300-400 words
- Cost: ~$0.03

---

### Node 4: Critic + Fusion (Claude Opus 4.5)

**Task:** Analyze both versions and create best hybrid

**Prompt Structure:**
```
You are an expert cover letter critic.

VERSION A (GPT-4o):
[letter A]

VERSION B (Claude Sonnet 4.5):
[letter B]

ANALYZE:
1. What's GOOD in Version A (strengths)
2. What's BAD in Version A (weaknesses)
3. What's GOOD in Version B (strengths)
4. What's BAD in Version B (weaknesses)

CREATE FUSION VERSION:
- Take best elements from both
- Fix weaknesses from both
- Create superior combined version

OUTPUT JSON:
{
  "version_a_good": [...],
  "version_a_bad": [...],
  "version_b_good": [...],
  "version_b_bad": [...],
  "fusion_letter": "...",
  "fusion_reasoning": "why this fusion is better"
}
```

**Cost:** ~$0.05

---

### Node 5: Human Review + Preference Learning

**Interface:**
```
┌──────────────────────────────────────────────────────────┐
│ FUSION COVER LETTER                                      │
├──────────────────────────────────────────────────────────┤
│ [Fusion letter text displayed]                           │
└──────────────────────────────────────────────────────────┘

CRITIC'S ANALYSIS:
✓ Version A strengths: [list]
✗ Version A weaknesses: [list]
✓ Version B strengths: [list]
✗ Version B weaknesses: [list]

YOUR EVALUATION:
Quality Score (1-10): [____]

What you LIKE:
┌────────────────────────────────────────────────────────┐
│                                                        │
└────────────────────────────────────────────────────────┘

What you DON'T LIKE / Changes needed:
┌────────────────────────────────────────────────────────┐
│                                                        │
└────────────────────────────────────────────────────────┘

[✓ APPROVE & SAVE]  [↻ EDIT WITH FEEDBACK]
```

**Preference Storage (preferences.json):**
```json
{
  "tone_preferences": [
    "less academic, more industry-focused",
    "confident but not arrogant"
  ],
  "content_preferences": [
    "always mention HPC/GPU experience",
    "connect research to practical outcomes"
  ],
  "structure_preferences": [
    "strong opening with achievement",
    "3-paragraph format"
  ],
  "avoid": [
    "overly technical jargon in finance roles",
    "generic phrases like 'team player'"
  ],
  "history": [
    {"date": "2025-01-21", "job": "ML Engineer @ Company X", "feedback": "..."}
  ]
}
```

---

### Node 6: Human Selects Editor Model

**Interface:**
```
SELECT EDITOR MODEL:

( ) Fine Model: Claude Opus 4.5
    - Best quality
    - Best at nuanced changes
    - Cost: $0.05
    
( ) Balanced Model: GPT-4o
    - Good quality  
    - Faster iterations
    - Cost: $0.02

[Proceed with Edits]
```

---

### Node 7: Editor Implements Feedback

**Editor Prompt (regardless of model chosen):**
```
You are editing a cover letter based on user feedback.

CURRENT VERSION:
{fusion_letter}

USER'S SAVED PREFERENCES (apply always):
{preferences.json content}

USER'S SPECIFIC FEEDBACK THIS ROUND:
{user_feedback}

TASK:
- Implement ALL requested changes
- Apply user's saved preferences
- Maintain professional quality
- Keep 300-400 words

OUTPUT:
Only the edited letter, no commentary.
```

**Models:**
- Opus 4.5: $0.05 per edit
- GPT-4o: $0.02 per edit

---

### Node 8: Review Edited Version (Loop)

**Interface:**
```
┌──────────────────────────────────────────────────────────┐
│ EDITED VERSION (Round N)                                 │
│ Edited by: [Claude Opus 4.5 / GPT-4o]                   │
├──────────────────────────────────────────────────────────┤
│ [Edited letter text]                                     │
└──────────────────────────────────────────────────────────┘

YOUR DECISION:

[✓ APPROVE - Save this version]

OR provide more feedback:

Additional changes needed:
┌────────────────────────────────────────────────────────┐
│                                                        │
└────────────────────────────────────────────────────────┘

Which model should fix it?
( ) Claude Opus 4.5 (fine)
( ) GPT-4o (balanced)

[Submit for Another Round]
```

**Loop continues until APPROVE**

---

## Complete Cost Breakdown

### Minimum (Approved after fusion):
- Classification: $0.0001
- Generation (2 models): $0.05
- Critic + Fusion: $0.05
- **Total: $0.10**

### Standard (1 edit round with GPT-4o):
- Classification: $0.0001
- Generation: $0.05
- Critic + Fusion: $0.05
- Edit (GPT-4o): $0.02
- **Total: $0.12**

### High Quality (2 edit rounds with Opus):
- Classification: $0.0001
- Generation: $0.05
- Critic + Fusion: $0.05
- Edit 1 (Opus): $0.05
- Edit 2 (Opus): $0.05
- **Total: $0.20**

---

## Model Assignments Summary

| Node | Model | Cost | Why |
|------|-------|------|-----|
| Classifier | Gemini Flash 2.0 | $0.0001 | Ultra-cheap, accurate enough |
| Generator A | GPT-4o | $0.02 | Uses GPT-written bio |
| Generator B | Claude Sonnet 4.5 | $0.03 | Uses Claude-written bio |
| Critic/Fusion | Claude Opus 4.5 | $0.05 | Best analysis + synthesis |
| Editor | User choice | $0.02-0.05 | Flexibility per situation |

---

## Preferences Learning System

**preferences.json** stores:

1. **General patterns** (learned over time)
   - Tone preferences
   - Content focus
   - Structural choices

2. **Specific feedback** (per application)
   - Date
   - Job/company
   - What you said
   - Which model was used

3. **Usage:**
   - Fed to ALL models in subsequent generations
   - Critic considers them in fusion
   - Editor MUST apply them in every edit

**Update frequency:**
- After every feedback round
- Accumulates over time
- Can be manually edited

---

## Example Session Flow

```
1. Input: LinkedIn URL for "Quant Researcher @ Trading Firm"

2. Gemini: "finance" (96% confidence)
   YOU: ✓ Correct

3. Load: Info_CL_Fin_GPT.md, Info_CL_Fin_Claude.md

4. Generate:
   - GPT-4o: Version A
   - Sonnet 4.5: Version B

5. Opus creates fusion + analysis
   YOU: Score 7/10
        Like: Strong opening, good technical depth
        Don't like: Too academic in para 2, missing quant-specific skills
        
6. YOU: Choose GPT-4o for editing

7. GPT-4o edits based on feedback + preferences.json
   YOU: Score 8/10
        Still needs: More emphasis on autonomous research
        Choose: Opus 4.5 for final polish

8. Opus refines
   YOU: Score 9/10 - APPROVED ✓
   
9. Saved! (and preferences updated)
```

**Total cost:** $0.17  
**Total time:** 15 minutes  
**Edit rounds:** 2

---

## Implementation Priority

### Phase 1: Core Pipeline
- [ ] Gemini classification
- [ ] Load biography files
- [ ] GPT + Sonnet generation
- [ ] Opus fusion
- [ ] Human review interface
- [ ] Approve/reject

### Phase 2: Preferences System
- [ ] preferences.json schema
- [ ] Save feedback after each review
- [ ] Load preferences in prompts
- [ ] Manual preference editing

### Phase 3: Edit Loop
- [ ] Model selection UI
- [ ] Editor integration
- [ ] Multi-round support
- [ ] Track edit history

### Phase 4: Polish
- [ ] Better UI/UX
- [ ] Analytics (approval rate, avg rounds)
- [ ] Cost tracking
- [ ] Quality trends over time

---

## Key Advantages

✅ **Lightweight classification** - Gemini Flash saves money  
✅ **No overwhelming choice** - Just 2 versions, then fusion  
✅ **Smart critic** - Identifies strengths/weaknesses automatically  
✅ **Learning system** - Your preferences improve future generations  
✅ **Flexible editing** - Choose quality vs speed per situation  
✅ **Iterative until perfect** - As many rounds as you need  
✅ **Budget conscious** - $0.10-0.20 per letter depending on rounds

---

## Questions?

1. Should preferences.json have categories (finance vs engineering)?
2. How many past feedbacks to show you during review?
3. Want ability to merge manual edits with AI edits?
4. Should system suggest which editor model based on feedback type?

---

**This architecture gives you full control while learning your style over time.**