import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog
import pandas as pd
from prompt_llm import define_prompt, fetch_llama_response


def select_file():
    return filedialog.askopenfilename(
        filetypes=[("CSV Files", "*.csv")],
        title="Select a CSV File"
    )


def generate_gui():
    app = tk.Tk()
    app.title("Book Recommendation Engine")

    #file select
    ttk.Label(app, text="Select your Goodreads dataset:").grid(row=0, column=0, padx=5, pady=5)
    file_path_label = ttk.Label(app, text="No file selected")
    file_path_label.grid(row=1, column=0, columnspan=2, padx=5, pady=5)

    def on_file_select():
        file_path = select_file()
        if file_path:
            file_path_label.config(text=file_path)

    select_button = ttk.Button(app, text="Browse", command=on_file_select)
    select_button.grid(row=0, column=1, padx=5, pady=5)

    status_label = ttk.Label(app, text="")
    status_label.grid(row=2, column=0, columnspan=2, padx=5, pady=5)

    #recommendations text box
    ttk.Label(app, text="Recommendations:").grid(row=4, column=0, columnspan=2, padx=5, pady=5)
    output_text = scrolledtext.ScrolledText(app, wrap=tk.WORD, width=60, height=15)
    output_text.grid(row=5, column=0, columnspan=2, padx=5, pady=5)

    def on_generate():
        if file_path_label.cget("text") == "No file selected":
            status_label.config(text="Please select your Goodreads dataset file before proceeding.")
            return

        #load dataset
        try:
            data = pd.read_csv(file_path_label.cget("text"))
            books_data = data.to_dict(orient='records')
            prompt = define_prompt(books_data)

            #fetch response from llm
            output = fetch_llama_response(prompt)
            output_text.delete('1.0', tk.END)  # Clear the text box
            output_text.insert(tk.END, output)  # Insert the fetched recommendations

            status_label.config(text="Recommendations generated successfully!")
        except Exception as e:
            status_label.config(text=f"Error loading dataset: {str(e)}")

    #generate recommendations button
    generate_button = ttk.Button(app, text="Generate Recommendations", command=on_generate)
    generate_button.grid(row=3, column=0, columnspan=2, pady=10)

    app.mainloop()


if __name__ == '__main__':
    generate_gui()
