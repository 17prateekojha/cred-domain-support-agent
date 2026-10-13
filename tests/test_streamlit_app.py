from pathlib import Path

from streamlit.testing.v1 import AppTest


def test_streamlit_app_renders_without_errors():
    app_path = Path(__file__).resolve().parents[1] / "app.py"

    app = AppTest.from_file(str(app_path)).run()

    assert not app.exception
    assert any("Cred Domain Support Agent" in title.value for title in app.title)
    assert app.chat_input


def test_streamlit_chat_returns_agent_response():
    app_path = Path(__file__).resolve().parents[1] / "app.py"
    app = AppTest.from_file(str(app_path)).run()

    app.chat_input[0].set_value("What are the eligibility rules for home loans?").run()

    assert not app.exception
    assert len(app.session_state["chat_history"]) == 2
    assert app.session_state["chat_history"][-1]["role"] == "assistant"
