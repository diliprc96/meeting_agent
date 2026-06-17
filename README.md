# Meeting Agent

Lightweight CLI tool that analyzes meeting notes and extracts:

- Action items (task, owner, deadline)
- Risks (risk, impact)
- Open technical questions

The script is designed to process transcript-style text files (for example, exported Teams transcripts) by chunking content and calling a local LLM endpoint.

## Current Implementation

The main flow in `main.py` is:

1. Read a `.txt` meeting notes file from CLI argument.
2. Estimate token count (`len(text) // 4`) for quick sizing.
3. Split notes into paragraph-based chunks (default max 6000 chars/chunk).
4. For each chunk, call local LLM to extract JSON with:
	 - `action_items`
	 - `risks`
	 - `open_questions`
5. Merge all chunk outputs into one combined JSON object.
6. Run an evaluation pass and optional cleanup passes:
	 - deduplicate action items
	 - fill missing owners
	 - improve vague tasks
7. Attempt final JSON parse and run a JSON repair step if parse fails.

Prompt templates are defined in `Prompts.py`.

## Requirements

- Python 3.9+
- Local LLM server at `http://localhost:11434` (Ollama-compatible API)
- A model named `mistral-repairgenie` available in the local server
- Python package:
	- `requests`

Install dependencies:

```bash
pip install requests
```

## Usage

Run from project root:

```bash
python main.py transcript.txt
```

You can replace `transcript.txt` with any plain text meeting notes file.

## Output Format

Expected extracted structure:

```json
{
	"action_items": [
		{ "task": "", "owner": "", "deadline": "" }
	],
	"risks": [
		{ "risk": "", "impact": "" }
	],
	"open_questions": []
}
```

Current script prints progress and final JSON to stdout.

## Notes and Limitations

- Input is currently treated as plain text; non-text document formats are not parsed directly.
- The tool depends on local model quality and prompt adherence.
- Evaluation output handling is currently string-based, so behavior depends on model response text.
- No automated tests or packaging are included yet.
- The script currently prints results but does not persist them to a file.

## Repository Structure

- `main.py`: CLI workflow and LLM orchestration
- `Prompts.py`: all prompt templates used by the workflow
- `transcript.txt`: sample input transcript
- `LICENSE`: Apache 2.0 license

## License

Licensed under Apache License 2.0. See `LICENSE`.