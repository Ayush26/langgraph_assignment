# =============================================================================
# Presentation Builder -- A LangGraph Project
# =============================================================================
#
# WHAT THIS DOES:
# A user provides a topic and audience. The system runs 3 planning specialists
# in PARALLEL (key messages, slide structure, visuals/data), then a decision
# node chooses whether the result should be a QUICK pitch or a DETAILED talk.
#
# GRAPH STRUCTURE:
#
#   START
#     |
#   understand_user_requirement
#     |
#     +---> define_key_messages --------+
#     |                                 |
#     +---> build_slide_structure -----+---> decide_deck_style
#     |                                 |         |
#     +---> suggest_visuals_and_data -+    (conditional)
#                                           /          \
#                                      quick?        detailed?
#                                         |               |
#                                quick_pitch_deck   detailed_presentation_plan
#                                         |               |
#                                        END             END
#
# HOW TO RUN:
#   python presentation_builder_graph.py
#
# DEPENDENCIES (same as requirements.txt):
#   langgraph, langchain-openai, python-dotenv, pydantic
#
# =============================================================================

import sys
import operator
from typing import Annotated

from dotenv import load_dotenv
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END

sys.stdout.reconfigure(encoding="utf-8")
load_dotenv()


class PresentationRequirement(BaseModel):
    topic: str = ""
    audience: str = ""
    key_messages: list[str] = Field(default_factory=list)
    slide_structure: list[str] = Field(default_factory=list)
    visuals_and_data: list[str] = Field(default_factory=list)
    needs_quick_pitch: bool = False
    deck_style: str = "detailed"
    final_deck: list[str] = Field(default_factory=list)
    messages: Annotated[list[str], operator.add] = Field(default_factory=list)


llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)


def _invoke_text(prompt: str) -> str:
    """Invoke the model and return a clean text response."""
    response = llm.invoke(prompt)
    content = getattr(response, "content", "") or ""
    if isinstance(content, list):
        return "\n".join(str(item).strip() for item in content if str(item).strip())
    return str(content).strip()


def _to_list(text: str, fallback: list[str] | None = None) -> list[str]:
    """Convert a model response into a non-empty list of strings."""
    if not text:
        return fallback or []

    lines = [line.strip() for line in text.splitlines() if line.strip()]
    if lines:
        return lines

    return fallback or []


def understand_user_requirement(requirement: PresentationRequirement) -> dict:
    """Understand the user's requirement for the presentation."""
    prompt = (
        f"User has provided the following requirement: Topic - {requirement.topic}, Audience - {requirement.audience}. "
        f"Please confirm and provide any additional insights or clarifications needed."
    )
    response_text = _invoke_text(prompt)
    print(f"Understanding user requirement: Topic - {requirement.topic}, Audience - {requirement.audience}")
    return {
        "messages": [f"[understand_user_requirement] {response_text}"]
    }


def define_key_messages(requirement: PresentationRequirement) -> dict:
    """Define the key messages for the presentation based on the topic and audience."""
    prompt = (
        f"You are a Specialist in creating effective presentations. "
        f"Based on the topic '{requirement.topic}' and audience '{requirement.audience}' given by the user, "
        f"Identify 3-5 concise key messages that should be conveyed in the presentation. "
        f"Return only short bullet points, one per line, with no extra commentary."
    )
    response_text = _invoke_text(prompt)
    key_messages = _to_list(
        response_text,
        fallback=[f"Explain why {requirement.topic} matters for {requirement.audience}."]
    )
    print(f"Defined key messages: {response_text}")
    return {
        "key_messages": key_messages,
        "messages": [f"[define_key_messages] {response_text}"],
    }


def build_slide_structure(requirement: PresentationRequirement) -> dict:
    """Build the slide-by-slide structure for the presentation based on the user requirement."""
    prompt = (
        f"You are a Specialist in creating effective presentations. "
        f"Based on the topic '{requirement.topic}', audience '{requirement.audience}' provided by the user\n"
        f"Please suggest a slide-by-slide structure for the presentation."
        f"Put each slide title on a new line, and do not include any extra commentary."
    )
    response_text = _invoke_text(prompt)
    slide_structure = _to_list(
        response_text,
        fallback=["Title slide", "Introduction", "Main content slide 1", "Main content slide 2", "Conclusion"]
    )
    print(f"Built slide structure: {response_text}")
    return {
        "slide_structure": slide_structure,
        "messages": [f"[build_slide_structure] {response_text}"],
    }


def suggest_visuals_and_data(requirement: PresentationRequirement) -> dict:
    """Suggest visuals and data to support the key messages in the presentation."""
    prompt = (
        f"You are a Specialist in creating effective presentations. "
        f"Based on the topic '{requirement.topic}', audience '{requirement.audience}' provided by the user\n"
        f"Please suggest relevant charts, images and data that can be included in the presentation."
    )
    response_text = _invoke_text(prompt)
    visuals_and_data = _to_list(
        response_text,
        fallback=["Use one supporting chart", "Add one relevant image", "Include 2-3 concise data points"]
    )
    print(f"Suggested visuals and data: {response_text}")
    return {
        "visuals_and_data": visuals_and_data,
        "messages": [f"[suggest_visuals_and_data] {response_text}"],
    }


def deck_style_decision(requirement: PresentationRequirement) -> dict:
    """Decide whether the presentation should be a quick pitch or a detailed talk."""
    prompt = (
        f"You are a presentation style decision system. The user privided the presentation topic '{requirement.topic}' and audience '{requirement.audience}'. "
        f"Here are three suggestions from Presentation specialists:\n\n"
        f"KEY MESSAGES:\n{requirement.key_messages}\n\n"
        f"SLIDE STRUCTURE:\n{requirement.slide_structure}\n\n"
        f"VISUALS AND DATA:\n{requirement.visuals_and_data}\n\n"
        f"Decide: does this presentation should be a quick pitch or a detailed talk?\n\n"
        f"Reply STRICTLY in this JSON format (no other text):\n"
        f'{{"needs_quick_pitch": true/false, "reason": "one sentence explanation"}}'
    )
    response_text = _invoke_text(prompt)
    decision = response_text.lower()
    needs_quick = "quick" in decision
    print(f"Decided deck style: {'quick' if needs_quick else 'detailed'}")
    return {
        "needs_quick_pitch": needs_quick,
        "deck_style": "quick" if needs_quick else "detailed",
        "messages": [f"[deck_style_decision] {response_text}"],
    }


def quick_pitch_deck(requirement: PresentationRequirement) -> dict:
    """Generate a quick pitch deck based on the key messages, slide structure, and visuals/data."""
    prompt = (
        f"You are a quick pitch deck generator. "
        f"Based on the key messages:\n{requirement.key_messages}\n"
        f"slide structure '{requirement.slide_structure}', and visuals/data '{requirement.visuals_and_data}', "
        f"please generate a concise quick pitch deck."
        f"Return the deck as a list of bullet points, one per line, with no extra commentary."
    )
    response_text = _invoke_text(prompt)
    print(f"Generated quick pitch deck: {response_text}")
    return {
        "final_deck": _to_list(response_text, fallback=["Quick pitch summary"]),
        "messages": [f"[quick_pitch_deck] {response_text}"],
    }


def detailed_presentation_plan(requirement: PresentationRequirement) -> dict:
    """Generate a detailed presentation plan based on the key messages, slide structure, and visuals/data."""
    formatted_key_messages = _format_key_messages(requirement)
    prompt = (
        f"You are a detailed presentation plan generator. "
        f"Based on the key messages:\n{requirement.key_messages}\n"
        f"slide structure '{requirement.slide_structure}', and visuals/data '{requirement.visuals_and_data}', "
        f"Please generate a detailed presentation plan."
        f"Return the plan as a slide-by-slide outline, with each slide's content and suggested visuals/data, one slide per line, with no extra commentary."
    )
    response_text = _invoke_text(prompt)
    print(f"Generated detailed presentation plan: {response_text}")
    return {
        "final_deck": _to_list(response_text, fallback=["Detailed presentation plan"]),
        "messages": [f"[detailed_presentation_plan] {response_text}"],
    }


def route_to_final_deck(requirement: PresentationRequirement) -> str:
    """Route to the final deck generation based on the decision made."""
    return "quick" if requirement.needs_quick_pitch else "detailed"


graph = StateGraph(PresentationRequirement)

graph.add_node("understand_user_requirement", understand_user_requirement)
graph.add_node("define_key_messages", define_key_messages)
graph.add_node("build_slide_structure", build_slide_structure)
graph.add_node("suggest_visuals_and_data", suggest_visuals_and_data)
graph.add_node("deck_style_decision", deck_style_decision)
graph.add_node("quick_pitch_deck", quick_pitch_deck)
graph.add_node("detailed_presentation_plan", detailed_presentation_plan)

graph.add_edge(START, "understand_user_requirement")
graph.add_edge("understand_user_requirement", "define_key_messages")
graph.add_edge("understand_user_requirement", "build_slide_structure")
graph.add_edge("understand_user_requirement", "suggest_visuals_and_data")

graph.add_edge("build_slide_structure", "deck_style_decision")
graph.add_edge("suggest_visuals_and_data", "deck_style_decision")

graph.add_conditional_edges(
    "deck_style_decision", 
    route_to_final_deck,
    {
        "quick": "quick_pitch_deck", 
        "detailed": "detailed_presentation_plan"
    }
)

graph.add_edge("quick_pitch_deck", END)
graph.add_edge("detailed_presentation_plan", END)

app= graph.compile()

def run_presentation_builder(topic: str, audience: str):
    print("="*50)
    print(" Presntation Builder Graph Execution ")
    print(f"You Mentioned- Topic: {topic}, Audience: {audience}")
    print("="*50)

    result = app.invoke(
        { "topic": topic, "audience": audience, "messages": [] }
    )

    print("\n"+"="*50)
    print(" Your personalized presentation is ready! ")
    print("="*50)

    print(f"\n{result['final_deck']}")

    print("\n"+"="*50)
    print(" Messages from each step of the process ")
    print("="*50)
    for message in result["messages"]:
        print(f"- {message}")  

    return result


if __name__ == "__main__":
    print("\n" + "=" * 55)
    print("  PRESENTATION BUILDER  ")
    print("=" * 55)  
    print("\n  Tell me the topic and audience for your presentation.")
    print("  I'll help you create a personalized presentation.")
    print("  Type 'quit' to exit.\n")

    while True:
        topic = input("  What is the topic of your presentation? > ").strip()
        audience = input("  Who is your audience? > ").strip()

        if topic.lower() in ("quit", "exit", "q") or audience.lower() in ("quit", "exit", "q"):
            print("\n  Take care of yourself. Goodbye!\n")
            break

        if not topic or not audience:
            continue

        run_presentation_builder(topic, audience)
        print("\n")