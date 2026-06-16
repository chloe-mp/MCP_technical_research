from mcp.server.fastmcp import FastMCP
from huggingface_hub import list_models
from datetime import datetime, timedelta, timezone
from typing import Optional
import os
import requests
import arxiv

mcp = FastMCP("documentation")

@mcp.tool()
def get_trending_hf(repo_type: str = "model", limit: int = 10) -> list[dict]:
    """Récupère les modèles les plus populaires récemment sur le Hugging Face Hub.

    Args:
        repo_type: type de dépôt, "model".
        limit: nombre de résultats à renvoyer.
    """
    models = list_models(sort="trendingScore", limit=limit)
    return [
        {"id": m.id, "downloads": m.downloads, "likes": m.likes}
        for m in models
    ]

@mcp.tool()
def search_trending_repos(topic: str = "llm", since_days: int = 30, limit: int = 10) -> list[dict]:
    """Recherche les dépôts GitHub populaires d'un domaine, créés récemment.

    Args:
        topic: étiquette de sujet GitHub, par exemple "nlp", "llm", "large-language-models".
        since_days: fenêtre en jours pour ne garder que les dépôts récents.
        limit: nombre de résultats, triés par nombre d'étoiles décroissant.
    """
    since_date = (datetime.now() - timedelta(days=since_days)).strftime("%Y-%m-%d")
    query = f"topic:{topic} created:>{since_date}"

    headers = {}
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"

    response = requests.get(
        "https://api.github.com/search/repositories",
        params={"q": query, "sort": "stars", "order": "desc", "per_page": limit},
        headers=headers,
    )
    response.raise_for_status()
    items = response.json()["items"]

    return [
        {
            "full_name": r["full_name"],
            "stars": r["stargazers_count"],
            "forks": r["forks_count"],
            "url": r["html_url"],
        }
        for r in items
    ]

@mcp.tool()
def search_recent_papers(cat: str = "cs.CL", keyword: Optional[list[str]] = None, since_days: int = 7, limit: int = 10) -> list[dict]:
    """Recherche les papiers ArXiv les plus récents.
       Args:
            cat: domaine de recherche (cs.CL = Computation and Language)
            keyword: liste des sous domaines de recherche (LLM, SLM, VLM, quantization, RAG, distillation)
            since_days: fenêtre de jours pour ne garder que les papiers les plus récents
            limit: nombre de résultats.
    """
    if keyword is None:
        keyword = ["LLM", "SLM", "VLM", "quantization", "RAG", "distillation"]
    if isinstance(keyword, str):
        keyword = [k.strip() for k in keyword.split(",")]

    keyword_part = " OR ".join(f"abs:{k}" for k in keyword)
    query = f"cat:{cat} AND ({keyword_part})"

    client = arxiv.Client()
    search = arxiv.Search(
        query=query,
        max_results=limit,
        sort_by=arxiv.SortCriterion.SubmittedDate,
    )
    results = client.results(search)
    cutoff = datetime.now(timezone.utc) - timedelta(days=since_days)

    return [                          # <-- return ajouté
        {
            "title": r.title,
            "published": r.published.isoformat(),
            "authors": [a.name for a in r.authors],
            "url": r.entry_id,
        }
        for r in results
        if r.published >= cutoff
    ]


@mcp.tool()
def get_release_notes(repo: str, limit: int = 5) -> list[dict]:
    """Récupère les dernières notes de version (releases) d'un dépôt GitHub.

    Args:
        repo: dépôt au format "owner/repo", par exemple "huggingface/trl".
        limit: nombre de releases récentes à renvoyer (les plus récentes d'abord).
    """
    if not repo or "/" not in repo or repo.startswith("http"):
        return [{"error": "Le paramètre 'repo' doit être au format 'owner/repo', par exemple 'huggingface/trl'."}]

    headers = {}
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    

    response = requests.get(
        f"https://api.github.com/repos/{repo}/releases",
        params={"per_page": limit},
        headers=headers,
    )
    response.raise_for_status()
    releases = response.json()          # <-- pas de ["items"] : c'est déjà une liste

    return [
        {
            "tag_name": r["tag_name"],
            "name": r["name"],
            "published_at": r["published_at"],   # <-- vrai nom du champ
            "body": (r["body"] or "")[:500],     # <-- garde-fou contre None
            "url": r["html_url"],
        }
        for r in releases
    ]
    

if __name__ == "__main__":
    mcp.run()