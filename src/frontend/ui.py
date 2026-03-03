import gradio as gr
from src.frontend.callbacks import (
    ui_bootstrap,
    on_switch_notebook,
    on_create_notebook,
    on_rename_notebook,
    on_delete_notebook,
    on_ingest_files,
    on_ingest_url,
    on_chat,
    on_report,
    on_quiz,
    on_podcast,
    on_download,
)
from src.backend.auth import require_login


CUSTOM_CSS = """
.gradio-container {
  max-width: 1320px !important;
  margin: 0 auto !important;
  padding-top: 18px !important;
}

.hero {
  border: 1px solid rgba(255,255,255,.08);
  border-radius: 16px;
  padding: 16px 18px;
  background: linear-gradient(145deg, rgba(50,87,255,.16), rgba(145,92,255,.12));
  backdrop-filter: blur(6px);
}

.hero h1 {
  margin: 0;
  font-size: 1.5rem;
  letter-spacing: .2px;
}

.hero p {
  margin: 6px 0 0;
  opacity: .88;
}

.panel {
  border: 1px solid rgba(255,255,255,.08);
  border-radius: 14px;
  background: linear-gradient(180deg, rgba(255,255,255,.04), rgba(255,255,255,.02));
  padding: 10px;
}

.chat-panel {
  border: 1px solid rgba(255,255,255,.08);
  border-radius: 14px;
  padding: 10px;
  background: linear-gradient(180deg, rgba(255,255,255,.04), rgba(255,255,255,.02));
}

.chat-panel .message-wrap {
  border-radius: 12px;
}

.chat-input textarea {
  min-height: 92px !important;
}

.primary-btn button {
  border-radius: 10px !important;
}
"""


def build_app():
    theme = gr.themes.Soft(
        primary_hue="blue",
        secondary_hue="indigo",
        neutral_hue="slate",
        spacing_size="md",
        radius_size="lg",
    )

    with gr.Blocks(title="NotebookLM Clone", theme=theme, css=CUSTOM_CSS) as demo:
        gr.Markdown(
            """
<div class='hero'>
  <h1>📓 NotebookLM Clone</h1>
  <p>Organize notebooks, ingest sources, and chat with RAG-backed citations.</p>
</div>
            """
        )

        login = gr.LoginButton()
        login.activate()

        username_state = gr.State("")

        def on_load(request: gr.Request):
            username = require_login(request)
            dd, chat, arts = ui_bootstrap(username)
            return username, dd, chat, arts

        with gr.Row(equal_height=True):
            with gr.Column(scale=1, min_width=360, elem_classes=["panel"]):
                user_box = gr.Textbox(label="User", interactive=False)

                with gr.Accordion("Notebook", open=True):
                    notebook_dd = gr.Dropdown(
                        label="Notebooks",
                        choices=[],
                        interactive=True,
                    )
                    nb_new = gr.Textbox(label="Create notebook", placeholder="Name")
                    btn_create = gr.Button("Create", elem_classes=["primary-btn"])
                    nb_rename = gr.Textbox(label="Rename notebook", placeholder="New name")
                    btn_rename = gr.Button("Rename")
                    btn_delete = gr.Button("Delete current", variant="stop")

                with gr.Accordion("Ingest", open=True):
                    file_up = gr.File(label="Upload PDF / PPTX / TXT", file_count="multiple")
                    btn_ingest_files = gr.Button("Ingest Files", elem_classes=["primary-btn"])
                    ingest_status = gr.Textbox(label="File ingest status", interactive=False)
                    url_in = gr.Textbox(label="URL", placeholder="https://...")
                    btn_ingest_url = gr.Button("Ingest URL")
                    url_status = gr.Textbox(label="URL ingest status", interactive=False)

                with gr.Accordion("Artifacts", open=False):
                    topic = gr.Textbox(label="Topic / prompt")
                    extra = gr.Textbox(label="Extra prompt (optional)")
                    with gr.Row():
                        btn_report = gr.Button("Generate Report")
                        btn_quiz = gr.Button("Generate Quiz")
                        btn_podcast = gr.Button("Generate Podcast")
                    artifact_status = gr.Textbox(label="Artifact status", interactive=False)
                    artifacts_list = gr.Dropdown(label="Artifacts", choices=[], interactive=True)
                    download_btn = gr.Button("Download selected")
                    download_file = gr.File(label="Download", interactive=False)
                    podcast_audio = gr.Audio(label="Podcast Audio", interactive=False)

            with gr.Column(scale=2, min_width=560, elem_classes=["chat-panel"]):
                chatbot = gr.Chatbot(
                    height=520,
                    label="Chat (RAG + citations)",
                    bubble_full_width=False,
                )

                with gr.Row():
                    msg = gr.Textbox(
                        label="Message",
                        placeholder="Ask about your uploaded sources...",
                        elem_classes=["chat-input"],
                        scale=5,
                    )
                    send = gr.Button(
                        "Send",
                        variant="primary",
                        scale=1,
                        elem_classes=["primary-btn"],
                    )

        demo.load(
            on_load,
            inputs=None,
            outputs=[username_state, notebook_dd, chatbot, artifacts_list],
            queue=False,
            api_name=False,
        )

        username_state.change(
            lambda u: u,
            inputs=username_state,
            outputs=user_box,
            queue=False,
            api_name=False,
        )

        notebook_dd.change(
            on_switch_notebook,
            inputs=[username_state, notebook_dd],
            outputs=[chatbot, artifacts_list],
            queue=False,
            api_name=False,
        )

        btn_create.click(
            on_create_notebook,
            inputs=[username_state, nb_new],
            outputs=[notebook_dd, chatbot, artifacts_list],
            queue=False,
            api_name=False,
        )

        btn_rename.click(
            on_rename_notebook,
            inputs=[username_state, notebook_dd, nb_rename],
            outputs=[notebook_dd],
            queue=False,
            api_name=False,
        )

        btn_delete.click(
            on_delete_notebook,
            inputs=[username_state, notebook_dd],
            outputs=[notebook_dd, chatbot, artifacts_list],
            queue=False,
            api_name=False,
        )

        btn_ingest_files.click(
            on_ingest_files,
            inputs=[username_state, notebook_dd, file_up],
            outputs=[ingest_status],
            queue=True,
            api_name=False,
        )

        btn_ingest_url.click(
            on_ingest_url,
            inputs=[username_state, notebook_dd, url_in],
            outputs=[url_status],
            queue=True,
            api_name=False,
        )

        send.click(
            on_chat,
            inputs=[username_state, notebook_dd, chatbot, msg],
            outputs=[chatbot, msg],
            queue=True,
            api_name=False,
        )

        btn_report.click(
            on_report,
            inputs=[username_state, notebook_dd, topic, extra],
            outputs=[artifact_status, artifacts_list, download_file],
            queue=True,
            api_name=False,
        )

        btn_quiz.click(
            on_quiz,
            inputs=[username_state, notebook_dd, topic, extra],
            outputs=[artifact_status, artifacts_list, download_file],
            queue=True,
            api_name=False,
        )

        btn_podcast.click(
            on_podcast,
            inputs=[username_state, notebook_dd, topic, extra],
            outputs=[artifact_status, artifacts_list, download_file, podcast_audio],
            queue=True,
            api_name=False,
        )

        download_btn.click(
            on_download,
            inputs=[username_state, notebook_dd, artifacts_list],
            outputs=[download_file],
            queue=False,
            api_name=False,
        )

    return demo
