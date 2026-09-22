from app.rag.prompts import (
    build_compare_messages,
    build_map_messages,
    build_qa_messages,
    build_qa_messages_with_history,
    build_reduce_messages,
    build_related_work_messages,
)


def _sample_chunks():
    return [
        {"text": "Attention is all you need.", "page_number": 3, "paper_id": "p1"},
        {"text": "Transformers use self-attention.", "page_number": 5, "paper_id": "p1"},
    ]


def test_build_qa_messages_includes_context_and_question():
    messages = build_qa_messages("What is attention?", _sample_chunks())
    assert messages[0]["role"] == "system"
    assert messages[-1]["role"] == "user"
    assert "What is attention?" in messages[-1]["content"]
    assert "Attention is all you need." in messages[-1]["content"]
    assert "[Source 1]" in messages[-1]["content"]
    assert "[Source 2]" in messages[-1]["content"]


def test_build_qa_messages_has_injection_guard_in_system_prompt():
    messages = build_qa_messages("q", _sample_chunks())
    system_content = messages[0]["content"].lower()
    assert "untrusted" in system_content
    assert "ignore" in system_content


def test_build_qa_messages_with_history_preserves_turn_order():
    history = [{"question": "first question", "answer": "first answer"}]
    messages = build_qa_messages_with_history("second question", _sample_chunks(), history)

    roles = [m["role"] for m in messages]
    assert roles == ["system", "user", "assistant", "user"]
    assert messages[1]["content"] == "first question"
    assert messages[2]["content"] == "first answer"
    assert "second question" in messages[3]["content"]


def test_build_map_and_reduce_messages():
    map_msgs = build_map_messages("some excerpt text")
    assert map_msgs[1]["content"] == "some excerpt text"

    reduce_msgs = build_reduce_messages(["summary one", "summary two"])
    assert "summary one" in reduce_msgs[1]["content"]
    assert "summary two" in reduce_msgs[1]["content"]


def test_build_compare_messages_includes_both_papers():
    messages = build_compare_messages("paper-a", "summary A text", "paper-b", "summary B text")
    content = messages[-1]["content"]
    assert "paper-a" in content
    assert "paper-b" in content
    assert "summary A text" in content
    assert "summary B text" in content


def test_build_related_work_messages_cites_paper_ids():
    excerpts = [{"text": "Excerpt text", "paper_id": "p42", "page_number": 7}]
    messages = build_related_work_messages("attention mechanisms", excerpts)
    assert "p42" in messages[-1]["content"]
    assert "attention mechanisms" in messages[-1]["content"]
