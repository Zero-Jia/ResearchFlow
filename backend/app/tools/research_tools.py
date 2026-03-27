from langchain.tools import tool

from app.data.research_knowledge import RESEARCH_KNOWLEDGE


def _score_knowledge_item(query: str, item: dict) -> int:
    query_lower = query.lower()
    score = 0

    if item["topic"].lower() in query_lower:
        score += 3

    for keyword in item["keywords"]:
        if keyword.lower() in query_lower:
            score += 2

    content_words = item["content"].lower().split()
    for word in query_lower.split():
        if word in content_words:
            score += 1

    return score


@tool
def search_research_knowledge(query: str) -> str:
    """
    Search the local research knowledge base for topics related to LLM agents,
    LangChain, LangGraph, RAG, structured output, or middleware.
    Use this tool when the user asks a research-oriented or concept-explanation question.
    """
    scored_results = []

    for item in RESEARCH_KNOWLEDGE:
        score = _score_knowledge_item(query, item)
        if score > 0:
            scored_results.append((score, item))

    scored_results.sort(key=lambda x: x[0], reverse=True)
    top_results = scored_results[:3]

    if not top_results:
        return "No relevant research knowledge was found."

    lines = []
    for rank, (score, item) in enumerate(top_results, start=1):
        lines.append(
            f"{rank}. Topic: {item['topic']}\n"
            f"   Score: {score}\n"
            f"   Content: {item['content']}"
        )

    return "\n\n".join(lines)


def _split_sentences(text: str) -> list[str]:
    raw_parts = text.replace("\n", " ").split(". ")
    sentences = []
    for part in raw_parts:
        part = part.strip()
        if not part:
            continue
        if not part.endswith("."):
            part += "."
        sentences.append(part)
    return sentences


@tool
def summarize_research_content(content: str, focus: str = "general") -> str:
    """
    Summarize retrieved research content into a shorter, cleaner answer.
    Use this tool after search results are available and the user wants
    a concise explanation, study note, interview summary, or engineering-focused summary.
    """
    if not content or content.strip() == "":
        return "No content provided for summarization."

    sentences = _split_sentences(content)

    if not sentences:
        return "No meaningful content was found to summarize."

    selected = sentences[:3]
    summary = " ".join(selected).strip()

    if focus == "interview":
        return (
            "Interview-style summary:\n"
            f"{summary}\n"
            "Key takeaway: Focus on what the concept is, why it is useful, and when to use it."
        )

    if focus == "engineering":
        return (
            "Engineering-focused summary:\n"
            f"{summary}\n"
            "Key takeaway: Emphasize implementation value, system design role, and practical usage."
        )

    return f"Summary:\n{summary}"


@tool
def classify_research_task(question: str) -> str:
    """
    Classify a user question into one of the following task types:
    research, compare, summary, or general.
    Use this tool when you need to determine the user's intent before deciding which tool to use next.
    """
    q = question.lower()

    compare_keywords = [
        "difference", "compare", "vs", "versus", "区别", "对比", "比较"
    ]
    summary_keywords = [
        "summary", "summarize", "总结", "概括", "简洁总结", "study note", "面试总结"
    ]
    research_keywords = [
        "research", "介绍", "解释", "是什么", "作用", "原理", "how", "what is", "why"
    ]

    if any(keyword in q for keyword in compare_keywords):
        return "compare"

    if any(keyword in q for keyword in summary_keywords):
        return "summary"

    if any(keyword in q for keyword in research_keywords):
        return "research"

    return "general"


@tool
def compare_research_topics(topic_a: str, topic_b: str) -> str:
    """
    Compare two research topics and return a structured comparison.
    Use this tool when the user explicitly asks for differences, comparison,
    pros/cons, or learning order between two concepts.
    """
    def find_best_match(topic: str) -> dict | None:
        topic_lower = topic.lower()
        best_item = None
        best_score = -1

        for item in RESEARCH_KNOWLEDGE:
            score = 0

            if item["topic"].lower() in topic_lower:
                score += 3

            for keyword in item["keywords"]:
                if keyword.lower() in topic_lower:
                    score += 2

            if score > best_score:
                best_score = score
                best_item = item

        return best_item if best_score > 0 else None

    item_a = find_best_match(topic_a)
    item_b = find_best_match(topic_b)

    if not item_a or not item_b:
        return "Unable to find enough knowledge to compare the two topics."

    return (
        f"Comparison of {item_a['topic']} and {item_b['topic']}:\n\n"
        f"1. {item_a['topic']}:\n"
        f"{item_a['content']}\n\n"
        f"2. {item_b['topic']}:\n"
        f"{item_b['content']}\n\n"
        "Suggested comparison dimensions:\n"
        "- Definition\n"
        "- Main purpose\n"
        "- Typical usage scenario\n"
        "- Engineering value\n"
    )