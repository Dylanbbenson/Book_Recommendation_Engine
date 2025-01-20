import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog
import pandas as pd
import requests
import json


def define_prompt(data):
    # Define the prompt
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


def prompt_llama(prompt, output_text, status_label):
    # Update status to show the user that processing has started
    status_label.config(text="Processing recommendations, please wait...")
    status_label.update_idletasks()  # Force an immediate GUI update

    # Send request to LLM
    try:
        response = requests.post(
            url="http://localhost:11434/api/generate",
            json={
                "model": "llama3",
                "prompt": prompt,
                "stream": True,
            },
            stream=True
        )

        # Clear the output text area
        output_text.delete(1.0, tk.END)

        if response.status_code == 200:
            full_response = ""
            for chunk in response.iter_lines():
                if chunk:
                    try:
                        chunk_data = json.loads(chunk)
                        full_response += chunk_data.get("response", "")
                    except json.JSONDecodeError:
                        pass
            # Display the full response
            output_text.insert(tk.END, full_response.strip())
            status_label.config(text="Recommendations generated successfully!")
        else:
            status_label.config(text=f"Error {response.status_code}: Unable to generate recommendations.")
    except Exception as e:
        status_label.config(text=f"Error: {str(e)}")


def select_file():
    # Open a file dialog to select the CSV file
    file_path = filedialog.askopenfilename(
        filetypes=[("CSV Files", "*.csv")],
        title="Select a CSV File"
    )
    return file_path


def generate_gui():
    # Initialize the Tkinter app
    app = tk.Tk()
    app.title("Book Recommendation Engine")

    # File selection button
    ttk.Label(app, text="Select your dataset:").grid(row=0, column=0, padx=5, pady=5)
    file_path_label = ttk.Label(app, text="No file selected")
    file_path_label.grid(row=1, column=0, columnspan=2, padx=5, pady=5)

    def on_file_select():
        file_path = select_file()
        if file_path:
            file_path_label.config(text=file_path)

    select_button = ttk.Button(app, text="Browse", command=on_file_select)
    select_button.grid(row=0, column=1, padx=5, pady=5)

    # Status label
    status_label = ttk.Label(app, text="")
    status_label.grid(row=2, column=0, columnspan=2, padx=5, pady=5)

    # Button to generate recommendations
    def on_generate():
        if file_path_label.cget("text") == "No file selected":
            status_label.config(text="Please select a dataset file before proceeding.")
            return

        # Load the dataset
        try:
            data = pd.read_csv(file_path_label.cget("text"))
            print(data.head())
            books_data = data.to_dict(orient='records')
            prompt = define_prompt(books_data)
            prompt_llama(prompt, output_text, status_label)
        except Exception as e:
            status_label.config(text=f"Error loading dataset: {str(e)}")

    generate_button = ttk.Button(app, text="Generate Recommendations", command=on_generate)
    generate_button.grid(row=3, column=0, columnspan=2, pady=10)

    # Output area
    ttk.Label(app, text="Recommendations:").grid(row=4, column=0, columnspan=2, padx=5, pady=5)
    output_text = scrolledtext.ScrolledText(app, wrap=tk.WORD, width=60, height=15)
    output_text.grid(row=5, column=0, columnspan=2, padx=5, pady=5)

    # Run the application
    app.mainloop()


if __name__ == '__main__':
    generate_gui()
