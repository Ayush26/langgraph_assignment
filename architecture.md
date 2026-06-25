# Presentation Planner -- Architecture

## How It Works

```
User provides a topic and audience
        |
        v
  [understand_user_requirement] -- identifies the user' topic and target audience
        |
        +---> [define_key_messages]   \
        |                                |
        +---> [build_slide_structure] +--> run in PARALLEL
        |                                |
        +---> [suggest_visuals_and_data] /
        |
        v
  [decide_deck_style] -- chooses quick pitch vs detailed presentation
        |
        +-- QUICK --> [quick_pitch_deck] --> concise slide plan
        |
        +-- DETAILED --> [detailed_presentation_plan] --> expanded deck plan
        |
        v
  Final presentation plan printed to user
```

## Graph Structure (Detailed)

```
                    +-------+
                    | START |
                    +---+---+
                        |
                        v
            +-----------+-----------+
            |   understand_user_    |
            |   requirement         |
            |                       |
            | Finds the topic and   |
            | audience              |
            +-----------+-----------+
                        |
           PARALLEL FAN-OUT (3 edges from one node)
          /             |              \
         v              v               v
+----------------+ +----------------------+ +--------------------+
| define_        | | build_            | | suggest_visuals_      |
| key_           | | slide_            | | and_data              |
| messages       | | structure         | | (alternate path)      |
+----------------+ +----------------------+ +--------------------+
         \              |               /
          FAN-IN (all specialist nodes finish)
                        |
                        v
          +-------------+-------------+
          |      decide_deck_style    |
          |                           |
          | Chooses quick vs detailed |
          +-------------+-------------+
                        |
               CONDITIONAL EDGE
                   /         \
      quick pitch /           \ detailed talk
                v               v
    +----------------+   +--------------------------+
    | quick_pitch_   |   | detailed_presentation_ |
    | deck           |   | plan                    |
    +----------------+   +--------------------------+
                \               /
                 \             /
                  v           v
                  +----+----+
                  |   END   |
                  +---------+
```

## State Fields

```
PresentationState
|
|-- topic                     <-- set by user input
|-- audience                  <-- set by user input
|-- key_messages              <-- written by define_key_messages
|-- slide_structure           <-- written by build_slide_structure
|-- visuals_and_data         <-- written by suggest_visuals_and_data
|-- deck_style                <-- written by decide_deck_style
|-- final_plan                <-- written by quick_pitch_deck OR detailed_presentation_plan
|-- messages                  <-- appended by ALL nodes (operator.add)
```

## LangGraph Concepts Used

| Concept | Where in Code | What It Does |
|---------|--------------|--------------|
| State (Pydantic) | `PresentationState` class | Typed data that flows through every node |
| Nodes | `define_key_messages`, `build_slide_structure`, `suggest_visuals_and_data`, `decide_deck_style`, `quick_pitch_deck`, `detailed_presentation_plan` | Functions that read state, do one job, and return updates |
| Parallel Execution | 3 edges from the first planning node | LangGraph runs the specialist nodes simultaneously |
| Fan-In | Multiple edges into the decision node | Waits for the parallel planning nodes to finish |
| Conditional Edge | Routing logic in the decision node | Sends the graph to a quick or detailed final path |
| Graph Compilation | `graph.compile()` | Turns the graph definition into a runnable `app` |
| Invocation | `app.invoke({...})` | Runs the graph with initial state |
| Message Accumulation | `Annotated[list, operator.add]` | Parallel nodes append without overwriting |

## Tech Stack

| Component | Purpose |
|-----------|---------|
| LangGraph | Graph orchestration -- nodes, edges, parallel, conditional |
| LangChain | OpenAI LLM wrapper (ChatOpenAI) |
| OpenAI | gpt-4o-mini -- cheap, fast, good enough for demo |
| Pydantic | State validation and type safety |
| python-dotenv | Load OPENAI_API_KEY from .env |

## File Structure

```
LangGraph_AgentFramework/
|-- presentation_builder_graph.py   Main code (graph + interactive loop)
|-- architecture.md                 This file
|-- architecture.drawio             Visual diagram (open with draw.io extension)
|-- requirements.txt                Python dependencies
|-- .env                            OPENAI_API_KEY (not committed)
|-- .env.example                    Template for .env
|-- .gitignore                      Ignores .env, venv, __pycache__
```
