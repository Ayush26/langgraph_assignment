# Presentation Planner - Learn LangGraph Step by Step

A beginner-friendly LangGraph project that plans a slide deck based on a
user-provided topic and audience.

The project demonstrates a clear LangGraph pattern:

```text
[Topic + Audience]
      |
      v
Understand Topic and Target Audience
      |
      +--> define_key_messages ----+
      +--> build_slide_structure --+--> decide_deck_style
      +--> suggest_visuals_and_data -----+          |
                                         conditional
                                      /              \
                              quick_pitch_deck     detailed_presentation_plan
                                      |              |
                                     END            END
---

## What This Project Does

A user provides a topic and audience such as:

- Topic- `AI for Healthcare` , Audience - Healthcare Professionals

The graph then:

1. Understand the Topic and AUdience.
2. Runs three specialist planning nodes in parallel:
   - `define_key_messages`
   - `build_slide_structure`
   - `suggest_visuals_and_data`
3. Uses a decision node to choose whether the deck should be:
   - a quick pitch, or
   - a detailed talk
4. Routes to the correct final node.
5. Produces a tailored presentation plan.

---

## Project Files

```text
presentation_builder_graph.py    Main LangGraph project
architecture.md                  Architecture explanation
architecture.drawio              Diagram source file
requirements.txt                 Python dependencies
.env.example                     Example environment file
.gitignore                       Ignored local files
```

---

## Setup

### 1. Create and activate a virtual environment

```powershell
python -m venv venv
venv\Scripts\activate
```

On macOS/Linux:

```bash
python -m venv venv
source venv/bin/activate
```

### 2. Install dependencies

```powershell
pip install -r requirements.txt
```

### 3. Configure your OpenAI API key

```powershell
copy .env.example .env
```

Edit `.env` and add your API key:

```text
OPENAI_API_KEY=sk-...
```

Never commit your real `.env` file.

### 4. Run the project

```powershell
python mental_wellness_graph.py
```

---

## Expected Flow

Example input:

```text
Topic: AI for Healthcare
Audience: Hospital executives
```

The graph will:

1. Identify the core messages that should be conveyed to the audience.
2. Draft a slide-by-slide structure for the presentation.
3. Suggest visuals, charts, or supporting data for each slide.
4. Decide whether the deck should be a quick pitch or a detailed talk.
5. Print the final presentation plan.
6. Print the message log showing which nodes executed.

---

## Code Walkthrough

| Step | What Happens | File |
|---|---|---|
| 1 | Define the presentation state | `presentation_builder_graph.py` |
| 2 | Initialize `ChatOpenAI` | `presentation_builder_graph.py` |
| 3 | Define the graph node functions | `presentation_builder_graph.py` |
| 4 | Define the routing logic for the decision node | `presentation_builder_graph.py` |
| 5 | Add nodes and edges to `StateGraph` | `presentation_builder_graph.py` |
| 6 | Compile the graph as `app` | `presentation_builder_graph.py` |
| 7 | Run the graph entry point | `presentation_builder_graph.py` |

---

## Important Note

This is a learning project for presentation planning. The output is meant to
help structure a deck and should be reviewed for clarity, accuracy, and audience fit.

---

## Key Takeaways

1. State carries the topic, audience, and planning output through the graph.
2. Nodes are normal Python functions that read state and return updates.
3. Parallel execution happens when one node connects to multiple next nodes.
4. Fan-in happens when multiple nodes connect into one later node.
5. Conditional edges let the graph choose the next path at runtime.
