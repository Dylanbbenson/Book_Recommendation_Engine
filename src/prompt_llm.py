import requests
import json

def define_prompt(data):
    prompt = f"""
    You are an assistant that generates book recommendations. Here's a dataset of books that a user has read:
    {data}

    Recommend 5 books similar to the books listed in this dataset. 
    Consider:
    - Genre similarity
    - Matching or complementary authors
    - A close page count range
    - Publish date proximity
    - Whether it's part of a series or not
    - User rating and Average Rating

    Explain your reasoning for each recommendation.
    """
    return prompt


def fetch_llama_response(input_text):
    try:
        response = requests.post(
            url="http://localhost:11434/api/generate",
            json={
                "model": "llama3",
                "prompt": input_text,
                "stream": True,
            },
            stream=True
        )
        response.raise_for_status()

        full_response = ""
        for chunk in response.iter_lines(decode_unicode=True):
            if chunk:
                try:
                    data = json.loads(chunk)
                    if "response" in data:
                        full_response += data["response"]
                except json.JSONDecodeError as e:
                    print(f"Error decoding chunk: {chunk}. Error: {e}")
                    continue

        return full_response.strip() if full_response else "No response from the Llama model."
    except requests.RequestException as e:
        return f"Error: {e}"

