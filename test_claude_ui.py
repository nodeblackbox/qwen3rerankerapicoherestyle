"""
Complete UI Element Reranking Test for Claude Interface
Uses the actual UI elements from Claude's web interface.
"""

import requests
import json
from typing import List, Dict, Any


# The actual UI elements from Claude
CLAUDE_UI_ELEMENTS = [
    {"type": "EditControl", "name": "Write your prompt to Claude", "bounds": {"left": 480, "top": 454, "right": 962, "bottom": 472}, "depth": 14},
    {"type": "EditControl", "name": "Address and search bar", "bounds": {"left": 395, "top": 179, "right": 517, "bottom": 203}, "depth": 9},
    {"type": "ButtonControl", "name": "Send message", "bounds": {"left": 937, "top": 501, "right": 962, "bottom": 526}, "depth": 14},
    {"type": "ButtonControl", "name": "Open attachments menu", "bounds": {"left": 480, "top": 501, "right": 507, "bottom": 526}, "depth": 16},
    {"type": "ButtonControl", "name": "Open tools menu", "bounds": {"left": 512, "top": 501, "right": 538, "bottom": 526}, "depth": 16},
    {"type": "ButtonControl", "name": "Research", "bounds": {"left": 543, "top": 501, "right": 612, "bottom": 526}, "depth": 15},
    {"type": "ButtonControl", "name": "Sonnet 4.5", "bounds": {"left": 845, "top": 501, "right": 931, "bottom": 526}, "depth": 14},
    {"type": "HyperlinkControl", "name": "New chat", "bounds": {"left": 244, "top": 263, "right": 268, "bottom": 290}, "depth": 13},
    {"type": "HyperlinkControl", "name": "Chats", "bounds": {"left": 244, "top": 293, "right": 268, "bottom": 321}, "depth": 13},
    {"type": "HyperlinkControl", "name": "Projects", "bounds": {"left": 244, "top": 321, "right": 268, "bottom": 349}, "depth": 13},
    {"type": "HyperlinkControl", "name": "Artifacts", "bounds": {"left": 244, "top": 349, "right": 268, "bottom": 377}, "depth": 13},
    {"type": "ButtonControl", "name": "Sidebar", "bounds": {"left": 244, "top": 221, "right": 268, "bottom": 245}, "depth": 11},
    {"type": "ButtonControl", "name": "ED Evil Daddy Pro plan", "bounds": {"left": 242, "top": 728, "right": 270, "bottom": 758}, "depth": 13},
    {"type": "ButtonControl", "name": "Close", "bounds": {"left": 480, "top": 134, "right": 508, "bottom": 162}, "depth": 10},
    {"type": "ButtonControl", "name": "Minimise", "bounds": {"left": 1031, "top": 129, "right": 1076, "bottom": 168}, "depth": 5},
    {"type": "ButtonControl", "name": "Maximise", "bounds": {"left": 1076, "top": 129, "right": 1122, "bottom": 168}, "depth": 5},
    {"type": "ButtonControl", "name": "Close", "bounds": {"left": 1122, "top": 129, "right": 1168, "bottom": 168}, "depth": 5},
    {"type": "ButtonControl", "name": "Search tabs", "bounds": {"left": 244, "top": 128, "right": 272, "bottom": 169}, "depth": 8},
    {"type": "ButtonControl", "name": "New tab", "bounds": {"left": 516, "top": 128, "right": 544, "bottom": 169}, "depth": 7},
    {"type": "ButtonControl", "name": "Back", "bounds": {"left": 243, "top": 174, "right": 277, "bottom": 208}, "depth": 8},
    {"type": "ButtonControl", "name": "Forward", "bounds": {"left": 279, "top": 174, "right": 313, "bottom": 208}, "depth": 8},
    {"type": "ButtonControl", "name": "Reload", "bounds": {"left": 315, "top": 174, "right": 349, "bottom": 208}, "depth": 8},
    {"type": "ButtonControl", "name": "View site information", "bounds": {"left": 363, "top": 179, "right": 387, "bottom": 203}, "depth": 9},
    {"type": "ButtonControl", "name": "Daddy", "bounds": {"left": 1012, "top": 174, "right": 1046, "bottom": 208}, "depth": 8},
    {"type": "ButtonControl", "name": "Finish update", "bounds": {"left": 1051, "top": 174, "right": 1162, "bottom": 208}, "depth": 8},
    {"type": "ButtonControl", "name": "Managed bookmarks", "bounds": {"left": 244, "top": 214, "right": 276, "bottom": 242}, "depth": 7},
    {"type": "ButtonControl", "name": " stripe group – Closed", "bounds": {"left": 244, "top": 218, "right": 287, "bottom": 238}, "depth": 8},
    {"type": "ButtonControl", "name": "Tab groups", "bounds": {"left": 295, "top": 214, "right": 323, "bottom": 242}, "depth": 8},
    {"type": "ButtonControl", "name": "conda-cheatsheet.pdf", "bounds": {"left": 341, "top": 214, "right": 491, "bottom": 242}, "depth": 7},
    {"type": "ButtonControl", "name": "Shodan Search Engine", "bounds": {"left": 495, "top": 214, "right": 645, "bottom": 242}, "depth": 7},
    {"type": "ButtonControl", "name": "All Bookmarks", "bounds": {"left": 1046, "top": 214, "right": 1160, "bottom": 242}, "depth": 7},
    {"type": "TabItemControl", "name": "Claude", "bounds": {"left": 266, "top": 128, "right": 522, "bottom": 169}, "depth": 9},
    {"type": "TabItemControl", "name": "Write", "bounds": {"left": 532, "top": 548, "right": 595, "bottom": 573}, "depth": 13},
    {"type": "TabItemControl", "name": "Learn", "bounds": {"left": 600, "top": 548, "right": 664, "bottom": 573}, "depth": 13},
    {"type": "TabItemControl", "name": "Code", "bounds": {"left": 669, "top": 548, "right": 732, "bottom": 573}, "depth": 13},
    {"type": "TabItemControl", "name": "Life stuff", "bounds": {"left": 737, "top": 548, "right": 819, "bottom": 573}, "depth": 13},
    {"type": "TabItemControl", "name": "From Drive", "bounds": {"left": 824, "top": 548, "right": 911, "bottom": 573}, "depth": 13},
]


def create_element_description(element: Dict[str, Any]) -> str:
    """Convert a UI element into a natural language description."""
    elem_type = element.get('type', '').replace('Control', '')
    name = element.get('name', '').strip()
    bounds = element.get('bounds', {})
    
    # Build description focusing on semantics
    if elem_type == 'Edit':
        if 'prompt' in name.lower() or 'write' in name.lower():
            return f"Text input field for writing messages: '{name}'"
        elif 'address' in name.lower() or 'search' in name.lower():
            return f"Browser address bar: '{name}'"
        else:
            return f"Input field: '{name}'"
    
    elif elem_type == 'Button':
        return f"Button '{name}' - clickable action element"
    
    elif elem_type == 'Hyperlink':
        return f"Navigation link to '{name}' section"
    
    elif elem_type == 'TabItem':
        return f"Tab '{name}' for switching content categories"
    
    else:
        return f"{elem_type}: '{name}'"


def rerank_ui_elements(task: str, elements: List[Dict[str, Any]], top_n: int = 10):
    """Rerank UI elements for a given task."""
    # Create descriptions
    descriptions = [create_element_description(elem) for elem in elements]
    
    # Call API
    response = requests.post(
        "http://localhost:8888/v2/rerank",
        json={
            "model": "rerank-v3.5",
            "query": f"User task: {task}. Which UI element should the user interact with?",
            "documents": descriptions,
            "top_n": top_n
        }
    )
    
    if response.status_code != 200:
        raise Exception(f"API error: {response.text}")
    
    result = response.json()
    
    # Map back to elements
    ranked = []
    for item in result['results']:
        idx = item['index']
        ranked.append({
            'element': elements[idx],
            'description': descriptions[idx],
            'score': item['relevance_score']
        })
    
    return ranked


def print_ranking(task: str, ranked_elements: List[Dict]):
    """Pretty print ranking results."""
    print("\n" + "="*90)
    print(f"TASK: {task}")
    print("="*90)
    
    for i, item in enumerate(ranked_elements, 1):
        elem = item['element']
        score = item['score']
        
        print(f"\n{i}. [Relevance: {score:.4f}]")
        print(f"   Type: {elem['type']}")
        print(f"   Name: \"{elem['name']}\"")
        print(f"   Location: ({elem['bounds']['left']}, {elem['bounds']['top']})")
        print(f"   Reasoning: {item['description']}")


def main():
    """Run comprehensive UI reranking tests."""
    
    print("╔════════════════════════════════════════════════════════════════════╗")
    print("║        Claude UI Element Reranking Test Suite                     ║")
    print("║        Testing Agent's Ability to Predict Next Interaction        ║")
    print("╚════════════════════════════════════════════════════════════════════╝")
    
    # Define test scenarios
    test_scenarios = [
        {
            "task": "Type a message asking Claude about Python programming",
            "expected": "Write your prompt to Claude"
        },
        {
            "task": "Send the message I just typed to Claude",
            "expected": "Send message"
        },
        {
            "task": "Attach a PDF document to my conversation",
            "expected": "Open attachments menu"
        },
        {
            "task": "Start a brand new conversation",
            "expected": "New chat"
        },
        {
            "task": "Navigate to my saved Projects",
            "expected": "Projects"
        },
        {
            "task": "Enable extended research capabilities for this query",
            "expected": "Research"
        },
        {
            "task": "Switch to a different AI model",
            "expected": "Sonnet 4.5"
        },
        {
            "task": "View my previous conversations",
            "expected": "Chats"
        },
        {
            "task": "Close the browser tab",
            "expected": "Close"
        },
        {
            "task": "Go back to the previous page",
            "expected": "Back"
        }
    ]
    
    total_tests = len(test_scenarios)
    correct_predictions = 0
    
    for i, scenario in enumerate(test_scenarios, 1):
        print(f"\n{'='*90}")
        print(f"Test {i}/{total_tests}")
        print(f"{'='*90}")
        
        try:
            # Get rankings
            ranked = rerank_ui_elements(
                task=scenario['task'],
                elements=CLAUDE_UI_ELEMENTS,
                top_n=5
            )
            
            # Print results
            print_ranking(scenario['task'], ranked)
            
            # Check if top element matches expected
            top_element = ranked[0]['element']['name']
            expected = scenario['expected']
            
            if expected.lower() in top_element.lower():
                print(f"\n✅ CORRECT! Top prediction matches expected: '{expected}'")
                correct_predictions += 1
            else:
                print(f"\n❌ INCORRECT! Expected '{expected}', got '{top_element}'")
        
        except Exception as e:
            print(f"\n❌ ERROR: {e}")
    
    # Summary
    print("\n" + "="*90)
    print("SUMMARY")
    print("="*90)
    print(f"Total Tests: {total_tests}")
    print(f"Correct Predictions: {correct_predictions}")
    print(f"Accuracy: {(correct_predictions/total_tests)*100:.1f}%")
    print("="*90)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⏹️  Test interrupted by user")
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Cannot connect to reranking API at http://localhost:8888")
        print("   Make sure the API is running: python qwen_rerank_api.py")
    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR: {e}")
