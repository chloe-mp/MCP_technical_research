## MCP_technical_research
MCP server linked to ArXiv, GitHub and HuggingFace

# Overview
This project exposes, through the Model Context Protocol (MCP), four tools that query the main sources of the NLP/AI ecosystem. Any MCP-compatible assistant (Claude Desktop, Cursor, etc.) can call them in natural language; a Gradio interface also allows manual use.
The goal isn't to read everything, but to detect signals of change: which methods are rising, which ones enter mainstream libraries, which recent papers move a subfield.
The four tools
ToolSourceWhat it returnsget_trending_hfHugging Face Hubtrending models (trendingScore)search_recent_papersarXivrecent papers filtered by category, keywords and time windowsearch_trending_reposGitHub Searchpopular repos in a domain, recently createdget_release_notesGitHub Releasesrelease notes of a library (TRL, vLLM, etc.)
Architecture and design choices
Logic / exposure separation. Tool logic lives in doc_mcp_server.py (built with FastMCP). The interface and web exposure are in app.py (Gradio with mcp_server=True). The same set of tools can therefore be served either locally via stdio (Claude Desktop) or online via HTTP (this Space). The logic doesn't change; only the exposure layer differs.
A notion of "trending" rebuilt per source. None of the three sources exposes the same mechanism:

Hugging Face provides a native trendingScore (used directly).
GitHub has no "trending" API: it's approximated via the Search API (topic: + created:>date, sorted by stars).
arXiv can't filter by date: results are sorted by submission date, then the since_days window is cut on the Python side.

Input robustness. get_release_notes validates the owner/repo format before any network call (rejecting empty fields or pasted URLs), making the tool safe when an LLM — not a human — provides the arguments. arXiv keywords are normalized (list or comma-separated string) to work both from an MCP call and from the Gradio interface.
Secrets. The GitHub token is read from an environment variable (GITHUB_TOKEN), never hard-coded. On this Space it's stored in Secrets; locally, in the client configuration.
Usage
Via the Gradio interface: open the App tab, pick a tool tab, fill the fields, click Search.
Via an MCP client: add the Space's MCP URL to your client config (Claude Desktop, Cursor…). The endpoint follows the format https://huggingface.co/spaces/Chloemp/mcp-veille-nlp .

# Known limitations

The GitHub tool relies on the topic label, which is noisy: catch-all projects tag themselves llm without real relevance. Quality signal comes mainly from HuggingFace and arXiv.
GitHub "trending" is an approximation (stars + date), not the proprietary Trending-page algorithm.
Without a GitHub token, the rate limit is 60 requests/hour.

# Future directions

A benchmark comparison tool (set aside for lack of a stable, free source).
Signal consolidation (heuristic: library integration > Hub adoption > paper volume).
Generating tool-calling traces from server usage, as training data for an agentic model.


Built with FastMCP + Gradio · Sources: Hugging Face Hub, arXiv, GitHub
