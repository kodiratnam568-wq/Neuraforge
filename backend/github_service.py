import httpx
import base64
import os
from typing import Optional

GITHUB_API = "https://api.github.com"
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")

HEADERS = {
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": "2022-11-28",
}
if GITHUB_TOKEN:
    HEADERS["Authorization"] = f"Bearer {GITHUB_TOKEN}"

# Files we care about for analysis
IMPORTANT_EXTENSIONS = {
    ".py", ".js", ".jsx", ".ts", ".tsx", ".java", ".go", ".rs",
    ".rb", ".php", ".cs", ".cpp", ".c", ".swift", ".kt",
}
CONFIG_FILES = {
    "package.json", "requirements.txt", "pyproject.toml", "Cargo.toml",
    "go.mod", "pom.xml", "build.gradle", "Gemfile", "composer.json",
    "Dockerfile", "docker-compose.yml", "docker-compose.yaml",
    ".env.example", "setup.py", "setup.cfg",
}
DOC_FILES = {"README.md", "README.rst", "README.txt", "CONTRIBUTING.md"}
MAX_FILE_SIZE = 30_000  # bytes – skip very large files


def parse_github_url(url: str) -> tuple[str, str]:
    """Return (owner, repo) from a GitHub URL."""
    url = url.strip().rstrip("/")
    # handle https://github.com/owner/repo and git@github.com:owner/repo
    if "github.com" not in url:
        raise ValueError("Not a GitHub URL")
    if url.startswith("git@"):
        path = url.split("github.com:")[-1]
    else:
        path = url.split("github.com/")[-1]
    parts = path.replace(".git", "").split("/")
    if len(parts) < 2:
        raise ValueError("Cannot parse owner/repo from URL")
    return parts[0], parts[1]


async def fetch_repo_tree(owner: str, repo: str) -> list[dict]:
    """Fetch the full file tree of the default branch."""
    async with httpx.AsyncClient(timeout=30) as client:
        # Get default branch
        repo_resp = await client.get(f"{GITHUB_API}/repos/{owner}/{repo}", headers=HEADERS)
        repo_resp.raise_for_status()
        default_branch = repo_resp.json().get("default_branch", "main")

        tree_resp = await client.get(
            f"{GITHUB_API}/repos/{owner}/{repo}/git/trees/{default_branch}?recursive=1",
            headers=HEADERS,
        )
        tree_resp.raise_for_status()
        return tree_resp.json().get("tree", [])


async def fetch_file_content(owner: str, repo: str, path: str) -> Optional[str]:
    """Fetch raw text content of a single file (returns None if too large or binary)."""
    async with httpx.AsyncClient(timeout=20) as client:
        resp = await client.get(
            f"{GITHUB_API}/repos/{owner}/{repo}/contents/{path}",
            headers=HEADERS,
        )
        if resp.status_code != 200:
            return None
        data = resp.json()
        size = data.get("size", 0)
        if size > MAX_FILE_SIZE:
            return None
        encoded = data.get("content", "")
        if not encoded:
            return None
        try:
            return base64.b64decode(encoded).decode("utf-8", errors="replace")
        except Exception:
            return None


def classify_file(path: str) -> Optional[str]:
    """Return the category of a file path, or None if we should ignore it."""
    filename = os.path.basename(path)
    ext = os.path.splitext(filename)[1].lower()

    if filename in DOC_FILES:
        return "docs"
    if filename in CONFIG_FILES:
        return "config"
    if ext in IMPORTANT_EXTENSIONS:
        return "code"
    return None


async def scan_repository(github_url: str) -> dict:
    """
    Main entry point: scan a GitHub repo and return structured data.
    Returns a dict with keys: owner, repo, tree_summary, file_contents, readme
    """
    owner, repo = parse_github_url(github_url)
    tree = await fetch_repo_tree(owner, repo)

    # Categorise everything
    classified: dict[str, list[str]] = {"docs": [], "config": [], "code": []}
    for item in tree:
        if item.get("type") != "blob":
            continue
        path = item["path"]
        cat = classify_file(path)
        if cat:
            classified[cat].append(path)

    # Directories (unique top-level dirs)
    dirs = sorted({p.split("/")[0] for p in (item["path"] for item in tree if item.get("type") == "blob")})

    # Fetch README first
    readme_content = ""
    for doc_path in classified["docs"][:3]:
        content = await fetch_file_content(owner, repo, doc_path)
        if content:
            readme_content = content[:3000]  # cap at 3k chars
            break

    # Fetch config files (package.json, requirements.txt, etc.)
    config_contents: dict[str, str] = {}
    for cfg_path in classified["config"][:8]:
        content = await fetch_file_content(owner, repo, cfg_path)
        if content:
            config_contents[cfg_path] = content[:2000]

    # Fetch a sample of code files (up to 10 files, prioritise root/main files)
    priority_keywords = {"main", "app", "index", "server", "api", "routes", "models", "db", "config"}
    def priority_score(p: str) -> int:
        name = os.path.basename(p).lower().replace(".", "_")
        return sum(1 for kw in priority_keywords if kw in name)

    code_paths = sorted(classified["code"], key=priority_score, reverse=True)[:12]
    code_contents: dict[str, str] = {}
    for cp in code_paths:
        content = await fetch_file_content(owner, repo, cp)
        if content:
            code_contents[cp] = content[:2500]

    return {
        "owner": owner,
        "repo": repo,
        "top_dirs": dirs[:20],
        "all_files": [item["path"] for item in tree if item.get("type") == "blob"][:100],
        "readme": readme_content,
        "config_files": config_contents,
        "code_files": code_contents,
        "stats": {
            "total_files": sum(1 for i in tree if i.get("type") == "blob"),
            "code_files_count": len(classified["code"]),
            "config_files_count": len(classified["config"]),
            "doc_files_count": len(classified["docs"]),
        },
    }
