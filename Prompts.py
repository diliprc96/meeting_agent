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
You are analyzing/reviewing extracted meeting insights from the transcript.

Identify issues in the data:

Categories:
1. duplicate_items
2. missing_owner
3. vague_tasks
4. redundant_risks
5. no_issuess

Return ONLY JSON:
{{
  "issues":["duplicate_items, "missing_owner"]
}}

If no issues:
{{
  "issues:["no_issues"]
}}

Data:
{output_json}
'''

def deduplicate_prompt(data):
    return f'''
Remove duplicate or overlapping action items.
Merge similar ones.

Return ONLY JSON.

Data:
{data}
'''


def owner_fix_prompt(data):
    return f'''
Some action items have missing or unclear owners.

Infer or assign appropriate owners if possible.

Return ONLY JSON.

Data:
{data}
'''

def clarity_prompt(data):
    return f'''
Some tasks are vague.

Rewrite them to be clear and actionable.

Return ONLY JSON.

Data:
{data}
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
