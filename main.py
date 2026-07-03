import requests
import argparse
import os
import Prompts
import json
from datetime import datetime

parser = argparse.ArgumentParser(description="meeting notes processor")
parser.add_argument("file", help="Path to meeting notes file (.txt)")

args = parser.parse_args()

if not os.path.exists(args.file):
    print("File not found.")
    exit(1)


def save_output_to_file(data):
    os.makedirs("outputs", exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = os.path.join("outputs", f"meeting_output_{timestamp}.json")

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"Saved output to: {output_file}")

def estimate_tokens(text):
    return len(text) // 4

def chunk_by_paragraph(text, max_characters=6000):
    paragraph = text.split('\n')
    current_chunk = ""
    Chunks = []

    for p in paragraph:
        if len(current_chunk) + len(p) < max_characters:
            current_chunk += p + '\n'
        else:
            Chunks.append(current_chunk)
            current_chunk = p+'\n'

    if current_chunk:
        Chunks.append(current_chunk)

    return Chunks


def call_llm(function, output):
    prompt_map = {"extract_actions": Prompts.actions_extraction_prompt(output),
                  "evaluate_output": Prompts.evaluation_prompt(output),
                  "deduplicate_prompt": Prompts.deduplicate_prompt(output),
                  "owner_fix_prompt": Prompts.owner_fix_prompt(output),
                  "clarity_prompt" : Prompts.clarity_prompt(output),
                  "Json_repair": Prompts.json_fix_prompt(output)
                }
    Prompt = prompt_map[f"{function}"]
    response = requests.post("http://localhost:11434/api/generate", json={"model": "mistral-repairgenie", "prompt":Prompt, "stream":False })
    return response.json()["response"]


with open(args.file, 'r', encoding="utf-8") as f:
    meeting_notes = f.read()

num_tokens = estimate_tokens(meeting_notes)
print(f"token count: {num_tokens}")

Chunks = chunk_by_paragraph(meeting_notes)
print('Total chunks = ', len(Chunks))
final_output = {"action_items": [], "risks": [], "open_questions":[]}


for i, chunk in enumerate(Chunks):
    # Prompt = Prompts.actions_extraction_prompt(chunk)
    response = call_llm("extract_actions", chunk)

    try:
        parsed = json.loads(response)

        final_output["action_items"].extend(parsed.get("action_items", []))
        final_output["risks"].extend(parsed.get("risks", []))
        final_output["open_questions"].extend(parsed.get("open_questions", []))

    except json.JSONDecodeError:
        print(f" JSON failed on chunk {i}")



issues = call_llm("evaluate_output", final_output)
print(issues)

data_str = json.dumps(final_output)

if "duplicate_items" in issues:
    print("🔧 Fixing duplicates...")
    data_str = call_llm("deduplicate_prompt", data_str)

if "missing_owner" in issues:
    print("🔧 Fixing missing owners...")
    data_str = call_llm("owner_fix_prompt", data_str)

if "vague_tasks" in issues:
    print("🔧 Improving clarity...")
    data_str = call_llm("clarity_prompt", data_str)

# final parse
try:
    final_output = json.loads(data_str)
    print(final_output)
    save_output_to_file(final_output)
except:
    print("⚠️ Final parsing failed, repairing Json")
    fixed_output = call_llm("Json_repair", final_output)
    final_output = json.loads(fixed_output)
    print("✅ JSON repaired successfully")
    print(final_output)
    save_output_to_file(final_output)