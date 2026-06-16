from doc_mcp_server import get_trending_hf, get_release_notes, search_recent_papers, search_trending_repos
import gradio as gr

with gr.Blocks(title="Veille technique") as demo:
    gr.Markdown("# Outils pour la veille technique")
    gr.Markdown("Outils allant chercher les derniers articles et modèles sur les LLM/NLP.")

    with gr.Tab("HuggingFace Extraction"):
        hf_repo_type = gr.Textbox(label="Type de dépôt", value="model")
        hf_limit = gr.Number(label="Nombre de résultats", value=10, precision=0)
        hf_output = gr.JSON(label="Résultats")
        gr.Button("Rechercher", size="lg").click(
            get_trending_hf,
            inputs=[hf_repo_type, hf_limit],
            outputs=hf_output,
        )

    with gr.Tab("Recherche notes de version"):
        rn_repo = gr.Textbox(label="Dépôt (format owner/repo)", placeholder="huggingface/trl")
        rn_limit = gr.Number(label="Nombre de releases", value=5, precision=0)
        rn_output = gr.JSON(label="Résultats")
        gr.Button("Rechercher", size="lg").click(
            get_release_notes,
            inputs=[rn_repo, rn_limit],
            outputs=rn_output,
        )

    with gr.Tab("Recherche ArXiv"):
        ax_cat = gr.Textbox(label="Catégorie arXiv", value="cs.CL")
        ax_keyword = gr.Textbox(
            label="Mots-clés (séparés par des virgules)",
            placeholder="LLM, distillation, RAG",
        )
        ax_since = gr.Number(label="Fenêtre (jours)", value=90, precision=0)
        ax_limit = gr.Number(label="Nombre de résultats", value=10, precision=0)
        ax_output = gr.JSON(label="Résultats")
        gr.Button("Rechercher", size="lg").click(
            search_recent_papers,
            inputs=[ax_cat, ax_keyword, ax_since, ax_limit],
            outputs=ax_output,
        )

    with gr.Tab("Recherche GitHub"):
        gh_topic = gr.Textbox(label="Sujet GitHub", value="llm")
        gh_since = gr.Number(label="Fenêtre (jours)", value=30, precision=0)
        gh_limit = gr.Number(label="Nombre de résultats", value=10, precision=0)
        gh_output = gr.JSON(label="Résultats")
        gr.Button("Rechercher", size="lg").click(
            search_trending_repos,
            inputs=[gh_topic, gh_since, gh_limit],
            outputs=gh_output,
        )

if __name__ == "__main__":
    demo.launch(mcp_server=True)