def actions_extraction_prompt(Chunk):
    Prompt = f''' 
You are an engineering meeting assistant.

Extract:

1. Action items (task, owner, deadline if available)
2. Risks (description and impact)
3. Open technical questions

Return ONLY valid JSON:

{{
  "action_items": [
    {{"task": "", "owner": "", "deadline": ""}}
  ],
  "risks": [
    {{"risk": "", "impact": ""}}
  ],
  "open_questions": []
}}

Meeting Notes:
----------------
{Chunk}
----------------
'''
    return Prompt


def evaluation_prompt(output_json):
    return f'''
You are reviewing extracted meeting insights.

Check for the following issues:

1. Duplicate or overlapping action items
2. Missing or unclear owners
3. Vague or unclear tasks
4. Redundant risks or questions

If issues exist, describe them briefly.

If everything looks good, say: "No major issues".

Output format:
- issues_found: Yes/No
- comments: short explanation

Data:
{output_json}
'''

def improvement_prompt(output_json):
    return f'''
You are improving extracted meeting insights.

Tasks:
- Remove duplicate action items
- Merge similar entries
- Clarify vague tasks
- Improve consistency of names

Return ONLY valid JSON:

{{
  "action_items": [...],
  "risks": [...],
  "open_questions": []
}}

Data:
{output_json}
'''



def json_fix_prompt(broken_output):
    return f'''
You are a JSON repair tool.

Fix the following text so that it becomes valid JSON.

Rules:
- Return ONLY valid JSON
- Do NOT add explanations
- Do NOT change meaning
- Preserve all keys and values
- Ensure proper quotes, brackets, and commas

Expected format:
{{
  "action_items": [
    {{"task": "", "owner": "", "deadline": ""}}
  ],
  "risks": [
    {{"risk": "", "impact": ""}}
  ],
  "open_questions": []
}}

Text to fix:
----------------
{broken_output}
----------------
'''
