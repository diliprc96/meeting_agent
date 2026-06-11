import requests
import argparse
import os
import Prompts
import json

parser = argparse.ArgumentParser(description="meeting notes processor")
parser.add_argument("file", help="Path to meeting notes file (.txt)")

args = parser.parse_args()

if not os.path.exists(args.file):
    print("File not found.")
    exit(1)

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

def actions_extract(chunk, Prompt):
    response = requests.post("http://localhost:11434/api/generate", json={"model": "mistral-repairgenie", "prompt":Prompt, "stream":False })
    return response.json()["response"]


def evaluate_output(output):
    prompt = Prompts.evaluation_prompt(output)

    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "mistral-repairgenie",
            "prompt": prompt,
            "stream": False
        }
    )
    return response.json()["response"]


def improve_output(output):
    prompt = Prompts.improvement_prompt(output)

    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "mistral-repairgenie",
            "prompt": prompt,
            "stream": False
        }
    )

    return response.json()["response"]

with open(args.file, 'r', encoding="utf-8") as f:
    meeting_notes = f.read()

num_tokens = estimate_tokens(meeting_notes)
print(f"token count: {num_tokens}")

Chunks = chunk_by_paragraph(meeting_notes)
print('Total chunks = ', len(Chunks))
final_output = {"action_items": [], "risks": [], "open_questions":[]}


for i, chunk in enumerate(Chunks):
    Prompt = Prompts.actions_extraction_prompt(chunk)
    response = actions_extract(chunk, Prompt)

    try:
        parsed = json.loads(response)

        final_output["action_items"].extend(parsed.get("action_items", []))
        final_output["risks"].extend(parsed.get("risks", []))
        final_output["open_questions"].extend(parsed.get("open_questions", []))

    except json.JSONDecodeError:
        print(f" JSON failed on chunk {i}")

# print(final_output)

evaluate_result = evaluate_output(final_output)

# print(evaluate_result)

if "Yes" in evaluate_result:
    print("Improving Output")
    improved = improve_output(json.dumps(final_output))

    try:
        final_output = json.loads(improved)
        print(final_output)
    except:
        print("Improvement parsing failed, attempting JSON repair")
        
        fix_prompt = Prompts.json_fix_prompt(improved)

        fixed = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "mistral-repairgenie",
                "prompt": fix_prompt,
                "stream": False
            }
        ).json()["response"]

        try:
            final_output = json.loads(fixed)
            print("✅ JSON repaired successfully")
            print(final_output)
        except:
            print("❌ JSON repair failed, keeping original output")

        
elif "No" in evaluate_result:
    print("No improvement needed")
    print(evaluate_result)

else:
    "evaluate result not in expected format"
    print(evaluate_result)
