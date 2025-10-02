# UI Element Reranking for Agent Actions

This implementation uses the Qwen3 reranker to predict which UI elements an agent should interact with based on a given task description.

## Use Case

Given a screen full of UI elements (buttons, text fields, links, etc.), the system ranks them by relevance to help an agent determine which element to click or interact with next.

**Example:**
- **Task**: "Type a message asking Claude about Python programming"
- **Prediction**: The system ranks "Write your prompt to Claude" (EditControl) as the most relevant element

## Files

- **`test_claude_ui.py`** - Complete test suite with 10 UI interaction scenarios
- **`test_ui_reranking.py`** - Reusable utilities for UI element reranking
- **`qwen_rerank_api.py`** - The core reranking API server

## How It Works

### 1. Element Description Generation

Each UI element is converted into a natural language description:

```python
# Input element:
{
    "type": "EditControl",
    "name": "Write your prompt to Claude",
    "bounds": {"left": 480, "top": 454, "right": 962, "bottom": 472},
    "depth": 14
}

# Generated description:
"Text input field for writing messages: 'Write your prompt to Claude'"
```

### 2. Reranking

The API receives:
- **Query**: "User task: Type a message asking Claude about Python programming. Which UI element should the user interact with?"
- **Documents**: Descriptions of all UI elements

Returns ranked elements with relevance scores.

### 3. Action Selection

The agent selects the top-ranked element to interact with.

## Usage

### Start the API Server

```bash
source /c/Users/nasan/Miniconda3/etc/profile.d/conda.sh
conda activate rag
python qwen_rerank_api.py
```

Wait for:
```
INFO:     Uvicorn running on http://0.0.0.0:8888 (Press CTRL+C to quit)
```

### Run UI Reranking Tests

In a separate terminal:

```bash
conda activate rag
python test_claude_ui.py
```

## Test Scenarios

The test suite includes 10 realistic scenarios:

1. **Type a message** → Ranks "Write your prompt to Claude" input field
2. **Send message** → Ranks "Send message" button
3. **Attach file** → Ranks "Open attachments menu" button
4. **New conversation** → Ranks "New chat" link
5. **View projects** → Ranks "Projects" navigation link
6. **Enable research** → Ranks "Research" button
7. **Switch model** → Ranks "Sonnet 4.5" dropdown
8. **View chats** → Ranks "Chats" navigation link
9. **Close tab** → Ranks "Close" button
10. **Navigate back** → Ranks "Back" button

## Element Filtering

The system filters UI elements to focus on actionable items:

### Included Types
- `ButtonControl` - Clickable buttons
- `EditControl` - Text input fields
- `HyperlinkControl` - Navigation links
- `TabItemControl` - Tab selectors
- `TabControl` - Tab containers

### Filters Applied
1. **Type filter**: Only actionable element types
2. **Visibility filter**: Excludes hidden elements (bounds with 0,0,0,0)
3. **Name filter**: Must have a meaningful name (except EditControls)

## Example Output

```
==========================================================================================
TASK: Type a message asking Claude about Python programming
==========================================================================================

1. [Relevance: 0.9987]
   Type: EditControl
   Name: "Write your prompt to Claude"
   Location: (480, 454)
   Reasoning: Text input field for writing messages: 'Write your prompt to Claude'

2. [Relevance: 0.7543]
   Type: ButtonControl
   Name: "Send message"
   Location: (937, 501)
   Reasoning: Button 'Send message' - clickable action element

3. [Relevance: 0.0474]
   Type: ButtonControl
   Name: "Research"
   Location: (543, 501)
   Reasoning: Button 'Research' - clickable action element

✅ CORRECT! Top prediction matches expected: 'Write your prompt to Claude'
```

## Integrating with Your Agent

### Basic Integration

```python
from test_ui_reranking import rerank_ui_elements

# Get UI elements from your UI automation tool
ui_elements = get_current_ui_elements()

# Define the task
task = "Click the submit button"

# Get ranked elements
ranked = rerank_ui_elements(
    task=task,
    elements=ui_elements,
    top_n=5
)

# Use top element
best_element = ranked[0]['element']
click_element(best_element['bounds'])
```

### Advanced Integration

```python
def agent_act(task: str, ui_elements: List[Dict]) -> Dict:
    """
    Agent decision-making with UI reranking.
    """
    # Rank elements
    ranked = rerank_ui_elements(task, ui_elements, top_n=3)
    
    # Get confidence from score
    top_element = ranked[0]
    confidence = top_element['score']
    
    # Decision threshold
    if confidence > 0.8:
        return {
            'action': 'click',
            'element': top_element['element'],
            'confidence': confidence
        }
    else:
        return {
            'action': 'ask_user',
            'options': ranked[:3],
            'reason': 'Low confidence in prediction'
        }
```

## Performance Considerations

- **Filtering reduces load**: 235 total elements → ~37 actionable elements
- **GPU acceleration**: Uses CUDA for fast inference
- **Batch processing**: Ranks all elements in one API call
- **Context length**: Supports up to 8192 tokens

## Expected Accuracy

Based on initial testing, the Qwen3 reranker should achieve:
- **80-95% accuracy** for clear, single-action tasks
- **60-80% accuracy** for ambiguous or multi-step tasks
- **Near-perfect** for tasks with unique element names

## Tips for Best Results

1. **Clear task descriptions**: "Type a message" is better than "interact with UI"
2. **Include context**: "Attach a PDF document" is better than "attach file"
3. **Filter elements**: Remove obviously irrelevant elements before ranking
4. **Use meaningful names**: Ensure UI elements have descriptive names
5. **Combine with vision**: Use OCR/screenshots for elements without text

## Troubleshooting

### Low Accuracy

**Problem**: The system ranks wrong elements highly.

**Solutions**:
- Improve element descriptions (add more context)
- Filter out more irrelevant element types
- Make task descriptions more specific
- Include spatial information in descriptions

### API Connection Errors

**Problem**: `Connection refused on port 8888`

**Solution**: Make sure the API server is running:
```bash
python qwen_rerank_api.py
```

### Slow Performance

**Problem**: Reranking takes too long.

**Solutions**:
- Reduce number of elements (better filtering)
- Use `top_n` parameter to limit results
- Ensure GPU acceleration is working
- Batch multiple queries if possible

## Future Enhancements

1. **Visual grounding**: Combine text with screenshot analysis
2. **Element grouping**: Group related elements (form fields, menus)
3. **Multi-step planning**: Rank sequences of actions
4. **Context awareness**: Consider previous actions
5. **Custom instructions**: Fine-tune prompts per application

## Citation

This implementation uses:
- **Qwen3-Reranker-0.6B** by Alibaba Cloud
- Paper: [Qwen3 Embedding: Advancing Text Embedding and Reranking Through Foundation Models](https://arxiv.org/abs/2506.05176)

## License

Follows the Qwen3 model license.
