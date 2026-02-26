import os
import sys

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from core.ai.factory import get_ai_provider

def test_ai_provider():
    print("Testing AI Provider...")
    
    # 1. Get Provider
    provider = get_ai_provider()
    if not provider:
        print("X No provider found (check API Key).")
        return

    print(f"Provider: {provider.__class__.__name__}")

    # 2. Test Text Generation
    print("\n--- Testing Text Generation ---")
    text_prompt = "Say hello in 1 sentence."
    response = provider.generate_text(text_prompt)
    print(f"Prompt: {text_prompt}")
    print(f"Response: {response}")

    if response:
        print("Text Generation Success")
    else:
        print("Text Generation Failed (Expected if no API Key)")

    # 3. Test JSON Generation
    print("\n--- Testing JSON Generation ---")
    json_prompt = "Generate a JSON object with fields 'name' and 'age'."
    json_response = provider.generate_json(json_prompt)
    print(f"Prompt: {json_prompt}")
    print(f"Response: {json_response}")

    if json_response:
        print("JSON Generation Success")
    else:
        print("JSON Generation Failed (Expected if no API Key)")

if __name__ == "__main__":
    test_ai_provider()
