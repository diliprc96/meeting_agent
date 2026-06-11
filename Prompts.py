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