import requests
import json
import sys
import io

# Fix encoding for Windows console
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# API endpoint
API_URL = "http://localhost:8889/ui/rerank"

# UI elements data
ui_elements = {
    "window": {
        "title": "Create form - Tally - Google Chrome",
        "process": "chrome.exe",
        "pid": 119148
    },
    "total_elements": 246,
    "elements": [
        {"type": "WindowControl", "name": "Create form - Tally - Google Chrome", "bounds": {"left": -8, "top": -8, "right": 1408, "bottom": 836}, "depth": 0},
        {"type": "PaneControl", "name": "", "bounds": {"left": 0, "top": 0, "right": 1400, "bottom": 828}, "depth": 1},
        {"type": "PaneControl", "name": "Create form - Tally - Google Chrome – PitchDeck", "bounds": {"left": 0, "top": 0, "right": 1400, "bottom": 828}, "depth": 1},
        {"type": "ButtonControl", "name": "Minimise", "bounds": {"left": 1263, "top": 0, "right": 1308, "bottom": 40}, "depth": 5},
        {"type": "ButtonControl", "name": "Maximise", "bounds": {"left": 1308, "top": 0, "right": 1354, "bottom": 40}, "depth": 5},
        {"type": "ButtonControl", "name": "Restore", "bounds": {"left": 1308, "top": 0, "right": 1354, "bottom": 40}, "depth": 5},
        {"type": "ButtonControl", "name": "Close", "bounds": {"left": 1354, "top": 0, "right": 1400, "bottom": 40}, "depth": 5},
        {"type": "TabControl", "name": "", "bounds": {"left": 0, "top": 0, "right": 1263, "bottom": 41}, "depth": 6},
        {"type": "ButtonControl", "name": "Search tabs", "bounds": {"left": 6, "top": 0, "right": 34, "bottom": 41}, "depth": 8},
        {"type": "ButtonControl", "name": "Group related tabs", "bounds": {"left": 0, "top": 0, "right": 0, "bottom": 0}, "depth": 8},
        {"type": "TextControl", "name": "Organise tabs?", "bounds": {"left": 0, "top": 0, "right": 0, "bottom": 0}, "depth": 9},
        {"type": "ButtonControl", "name": "Dismiss suggestion", "bounds": {"left": 0, "top": 0, "right": 0, "bottom": 0}, "depth": 9},
        {"type": "TabItemControl", "name": "Data Science Tool: Orange Overview - Grok", "bounds": {"left": 28, "top": 0, "right": 110, "bottom": 41}, "depth": 9},
        {"type": "ButtonControl", "name": "Mute tab", "bounds": {"left": 224, "top": 12, "right": 240, "bottom": 28}, "depth": 10},
        {"type": "ButtonControl", "name": "Close", "bounds": {"left": 132, "top": 6, "right": 160, "bottom": 34}, "depth": 10},
        {"type": "ButtonControl", "name": "New tab", "bounds": {"left": 1181, "top": 0, "right": 1209, "bottom": 41}, "depth": 7},
        {"type": "ButtonControl", "name": "Back", "bounds": {"left": 0, "top": 46, "right": 39, "bottom": 80}, "depth": 8},
        {"type": "ButtonControl", "name": "Forward", "bounds": {"left": 41, "top": 46, "right": 75, "bottom": 80}, "depth": 8},
        {"type": "ButtonControl", "name": "Reload", "bounds": {"left": 77, "top": 46, "right": 111, "bottom": 80}, "depth": 8},
        {"type": "ButtonControl", "name": "Home", "bounds": {"left": 0, "top": 0, "right": 0, "bottom": 0}, "depth": 8},
        {"type": "GroupControl", "name": "", "bounds": {"left": 120, "top": 46, "right": 857, "bottom": 80}, "depth": 8},
        {"type": "ButtonControl", "name": "This page is accessing your microphone.", "bounds": {"left": 125, "top": 51, "right": 149, "bottom": 75}, "depth": 9},
        {"type": "ButtonControl", "name": "View site information", "bounds": {"left": 125, "top": 51, "right": 149, "bottom": 75}, "depth": 9},
        {"type": "EditControl", "name": "Address and search bar", "bounds": {"left": 157, "top": 51, "right": 813, "bottom": 75}, "depth": 9},
        {"type": "ButtonControl", "name": "Open in app", "bounds": {"left": 0, "top": 0, "right": 0, "bottom": 0}, "depth": 9},
        {"type": "ButtonControl", "name": "Customize", "bounds": {"left": 1048, "top": 97, "right": 1141, "bottom": 125}, "depth": 13},
        {"type": "ButtonControl", "name": "Sign up", "bounds": {"left": 1144, "top": 97, "right": 1215, "bottom": 125}, "depth": 13},
        {"type": "ButtonControl", "name": "Preview", "bounds": {"left": 1218, "top": 97, "right": 1293, "bottom": 125}, "depth": 13},
        {"type": "ButtonControl", "name": "Publish", "bounds": {"left": 1301, "top": 97, "right": 1371, "bottom": 125}, "depth": 14},
        {"type": "TextControl", "name": "Form title", "bounds": {"left": 342, "top": 283, "right": 530, "bottom": 332}, "depth": 14},
        {"type": "ButtonControl", "name": "Press Enter to start from scratch", "bounds": {"left": 334, "top": 381, "right": 595, "bottom": 409}, "depth": 12},
        {"type": "ButtonControl", "name": "Use a template", "bounds": {"left": 334, "top": 419, "right": 477, "bottom": 447}, "depth": 12},
        {"type": "HyperlinkControl", "name": "Get started with templates", "bounds": {"left": 334, "top": 645, "right": 555, "bottom": 674}, "depth": 13},
        {"type": "HyperlinkControl", "name": "Embed your form", "bounds": {"left": 334, "top": 683, "right": 493, "bottom": 712}, "depth": 13},
        {"type": "HyperlinkControl", "name": "Help center", "bounds": {"left": 334, "top": 721, "right": 455, "bottom": 750}, "depth": 13},
        {"type": "HyperlinkControl", "name": "Learn about Tally Pro", "bounds": {"left": 334, "top": 759, "right": 519, "bottom": 788}, "depth": 13},
        {"type": "TextControl", "name": "How-to guides", "bounds": {"left": 692, "top": 577, "right": 794, "bottom": 594}, "depth": 12},
        {"type": "HyperlinkControl", "name": "Untitled", "bounds": {"left": 44, "top": 97, "right": 112, "bottom": 125}, "depth": 13},
        {"type": "TextControl", "name": "Untitled", "bounds": {"left": 51, "top": 102, "right": 105, "bottom": 119}, "depth": 14},
        {"type": "ButtonControl", "name": "Choose files: No file chosen", "bounds": {"left": 0, "top": 135, "right": 1, "bottom": 136}, "depth": 11},
        {"type": "TextControl", "name": "Get started", "bounds": {"left": 342, "top": 577, "right": 420, "bottom": 594}, "depth": 12},
        {"type": "HyperlinkControl", "name": "Create your first form", "bounds": {"left": 334, "top": 607, "right": 522, "bottom": 636}, "depth": 13},
        {"type": "TextControl", "name": "Create your first form", "bounds": {"left": 366, "top": 612, "right": 512, "bottom": 630}, "depth": 14},
    ]
}

# Test scenarios
test_scenarios = [
    {
        "task": "click on sign up button",
        "description": "Finding the sign up button to register"
    },
    {
        "task": "publish the form",
        "description": "Finding the publish button to make the form live"
    },
    {
        "task": "create a new form from scratch",
        "description": "Finding the option to start creating a form from scratch"
    },
    {
        "task": "use a template",
        "description": "Finding the button to use a pre-made template"
    },
    {
        "task": "preview the form",
        "description": "Finding the preview button to see how the form looks"
    },
    {
        "task": "customize the form",
        "description": "Finding the customize button to change form settings"
    },
    {
        "task": "edit form title",
        "description": "Finding the form title field to change the name"
    },
    {
        "task": "get help and documentation",
        "description": "Finding help resources and documentation"
    }
]




def test_reranking(task, elements, top_k=10):
    """Test the reranking API with a specific task"""
    
    # Prepare request payload matching the API schema
    payload = {
        "task": task,
        "elements": elements,
        "top_n": top_k
    }
    
    print(f"\n{'='*80}")
    print(f"Task: {task}")
    print(f"Total elements: {len(elements)}")
    print(f"Requesting top {top_k} results...")
    print(f"{'='*80}\n")
    
    try:
        # Send request to API
        response = requests.post(API_URL, json=payload, timeout=30)
        response.raise_for_status()
        
        result = response.json()
        
        # Display results
        print(f"[OK] Request successful!")
        print(f"Processing time: {result.get('inference_time_ms', 'N/A')} ms\n")
        
        print(f"Top {len(result['results'])} ranked elements:")
        print("-" * 80)
        
        for i, item in enumerate(result['results'], 1):
            idx = item['index']
            score = item['relevance_score']
            element = item['element']
            
            print(f"\n#{i} - Score: {score:.4f}")
            print(f"   Type: {element.get('type', 'N/A')}")
            print(f"   Name: {element.get('name', '(empty)')}")  
            if element.get('bounds'):
                bounds = element['bounds']
                print(f"   Bounds: ({bounds['left']}, {bounds['top']}, {bounds['right']}, {bounds['bottom']})")
            print(f"   Depth: {element.get('depth', 'N/A')}")
        
        print("\n" + "-" * 80)
        
        return result
        
    except requests.exceptions.RequestException as e:
        print(f"[FAIL] Request failed: {e}")
        return None
    except Exception as e:
        print(f"[ERROR] Error: {e}")
        return None


def main():
    print("=" * 80)
    print("UI ELEMENT RERANKING API TEST")
    print("=" * 80)
    print(f"\nAPI Endpoint: {API_URL}")
    print(f"Total UI Elements: {len(ui_elements['elements'])}")
    print(f"Window: {ui_elements['window']['title']}")
    
    # Test each scenario
    for i, scenario in enumerate(test_scenarios, 1):
        print(f"\n\n{'#' * 80}")
        print(f"TEST SCENARIO {i}/{len(test_scenarios)}")
        print(f"{'#' * 80}")
        print(f"Description: {scenario['description']}")
        
        result = test_reranking(
            task=scenario['task'],
            elements=ui_elements['elements'],
            top_k=5  # Get top 5 results for each task
        )
        
        if result:
            print(f"\n[OK] Test scenario {i} completed successfully")
        else:
            print(f"\n[FAIL] Test scenario {i} failed")
        
        # Small delay between tests
        import time
        time.sleep(0.5)
    
    print(f"\n\n{'=' * 80}")
    print("ALL TESTS COMPLETED")
    print(f"{'=' * 80}\n")


if __name__ == "__main__":
    main()
