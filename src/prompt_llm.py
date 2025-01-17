import requests
import json
import pandas as pd
import tkinter as tk
from tkinter import ttk, scrolledtext

def define_prompt(data):
    #define prompt
    prompt = f"""
    You are an assistant that generates book recommendations. Here's a dataset of books that a user has read:
    {data}
    
    Recommend 5 books similar to the books listed in this dataset. 
    Consider:
    - Genre similarity
    - Matching or complementary authors
    - A close page count range
    - Publish date proximity
    - Whether it's a part of a series or not
    
    Explain your reasoning for each recommendation.
    """
    return prompt

def prompt_llama(prompt):
    #send request to llama
    response = requests.post(
        url="http://localhost:11434/api/generate",
        json={
            "model": "llama3",  # Replace with the model you're using
            "stream": True,  # Ensure streaming is enabled
        },
        stream=True  # Enable streaming response
    )

    output_text.delete(1.0, tk.END) #clear text

    if response.status_code == 200:
        full_response = ""
        for chunk in response.iter_lines():
            if chunk:
                try:
                    # Parse each chunk as JSON and extract the "response" field
                    chunk_data = json.loads(chunk)
                    full_response += chunk_data.get("response", "")
                except json.JSONDecodeError:
                    pass
        # Display the response in the output text area
        output_text.insert(tk.END, full_response.strip())
    else:
        output_text.insert(tk.END, f"Error {response.status_code}: {response.text}")


def generate_gui():
    # Initialize the Tkinter app
    app = tk.Tk()
    app.title("Book Recommendation Engine")

    # Input fields
    ttk.Label(app, text="Book Title:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
    book_title = ttk.Entry(app, width=30)
    book_title.grid(row=0, column=1, padx=5, pady=5)

    ttk.Label(app, text="Book Author:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
    book_author = ttk.Entry(app, width=30)
    book_author.grid(row=1, column=1, padx=5, pady=5)

    ttk.Label(app, text="Genres (comma-separated):").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
    book_genres = ttk.Entry(app, width=30)
    book_genres.grid(row=2, column=1, padx=5, pady=5)

    ttk.Label(app, text="Page Count:").grid(row=3, column=0, padx=5, pady=5, sticky=tk.W)
    book_pages = ttk.Entry(app, width=30)
    book_pages.grid(row=3, column=1, padx=5, pady=5)

    ttk.Label(app, text="Publish Year:").grid(row=4, column=0, padx=5, pady=5, sticky=tk.W)
    book_year = ttk.Entry(app, width=30)
    book_year.grid(row=4, column=1, padx=5, pady=5)

    # Button to generate recommendations
    generate_button = ttk.Button(app, text="Generate Recommendations", command=prompt_llama)
    generate_button.grid(row=5, column=0, columnspan=2, pady=10)

    # Output area
    ttk.Label(app, text="Recommendations:").grid(row=6, column=0, columnspan=2, padx=5, pady=5)
    output_text = scrolledtext.ScrolledText(app, wrap=tk.WORD, width=60, height=15)
    output_text.grid(row=7, column=0, columnspan=2, padx=5, pady=5)

    # Run the application
    app.mainloop()

if __name__ == '__main__':
    # load dataset
    data = pd.read_csv('./data/cleaned_data.csv')
    data = data[data['have_read'] == True]  # filter by books read (optional)
    books_data = data.to_dict(orient='records')
    prompt = define_prompt(books_data)
    generate_gui()
    prompt_llama(prompt)
