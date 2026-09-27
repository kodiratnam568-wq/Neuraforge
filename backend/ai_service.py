import os
import json
from groq import AsyncGroq
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
MODEL = "qwen/qwen3.8-27b"

SYSTEM_PROMPT = """You are NeuraForge, an expert AI assistant that helps developers understand new codebases.
Your job is to analyse repository data and produce a structured, beginner-friendly onboarding guide.
You MUST respond with valid JSON only — no markdown fences, no extra text.
"""

ANALYSIS_SCHEMA = """
Respond with this exact JSON structure:
{
  "project_overview": "2-3 sentence plain-English description of what this project does",
  "tech_stack": {
    "languages": ["list of programming languages"],
    "frameworks": ["list of frameworks/libraries"],
    "databases": ["list of databases if any"],
    "tools": ["build tools, CI, Docker, etc."]
  },
  "important_files": [
    {
      "path": "relative/file/path",
      "role": "one sentence: what this file does"
    }
  ],
  "architecture": {
    "description": "2-3 sentence explanation of how the system is structured",
    "layers": ["layer1 description", "layer2 description", "..."]
  },
  "setup_guide": [
    "Step 1: ...",
    "Step 2: ...",
    "Step 3: ...",
    "Step 4: ..."
  ],
  "starter_tasks": [
    {
      "title": "Task title",
      "description": "What a beginner should do / explore",
      "file_hint": "which file to look at (optional)"
    }
  ]
}
"""


async def analyze_repository(repo_data: dict) -> dict:
    """Send repo data to Groq LLM and return structured analysis."""
    client = AsyncGroq(api_key=GROQ_API_KEY)

    # Build a compact summary of the repo for the prompt
    prompt_parts = [
        f"Repository: {repo_data['owner']}/{repo_data['repo']}",
        f"Total files: {repo_data['stats']['total_files']}",
        f"Top-level directories: {', '.join(repo_data['top_dirs'][:15])}",
        "",
        "=== FILE TREE (sample) ===",
        "\n".join(repo_data["all_files"][:60]),
        "",
    ]

    if repo_data["readme"]:
        prompt_parts += ["=== README ===", repo_data["readme"][:2000], ""]

    for cfg_path, content in list(repo_data["config_files"].items())[:4]:
        prompt_parts += [f"=== {cfg_path} ===", content[:800], ""]

    for code_path, content in list(repo_data["code_files"].items())[:6]:
        prompt_parts += [f"=== {code_path} (first 60 lines) ===", content[:1200], ""]

    prompt_parts.append(ANALYSIS_SCHEMA)

    user_message = "\n".join(prompt_parts)

    response = await client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ],
        temperature=0.3,
        max_tokens=800,
    )

    raw = response.choices[0].message.content.strip()

    # Strip markdown fences if the model added them anyway
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]

    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        # Fallback: return raw text wrapped in error structure
        return {
            "error": "AI returned invalid JSON",
            "raw_response": raw[:500],
        }
