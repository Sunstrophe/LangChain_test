import tkinter as tk
import main
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage


def handle_response(response):
    responses = []

    for res in response:
        # print(res)
        # print(type(res))
        if isinstance(res, HumanMessage):
            responses.append({
                "type": "Human",
                "message": res.content
            })

        elif isinstance(res, ToolMessage):
            responses.append({
                "type": "Tool",
                "message": res.content
            })
        elif isinstance(res, AIMessage):
            # print(res)
            if res.content:
                message = res.content
            elif res.tool_calls:
                # print(res.tool_calls[0])
                # print(type(res.tool_calls[0]))
                message = f"Use tool: {res.tool_calls[0]['name']}\nWith query: '{res.tool_calls[0]['args']['query']}'"
            else:
                message = "Couldn't find the message"
            responses.append({
                "type": "AI",
                "message": message
            })
        else:
            raise ValueError
    return responses


def submit_message():
    message = input_window.get()
    response = main.ui_query(message)
    # print(type(response[-1]))
    # print(dir(response[-1]))
    # print(response)
    # print(type(response))
    responses = handle_response(response)

    text_window1.config(state="normal")
    # text_window1.delete(1.0, tk.END)
    # start_idx = text_window1.index(tk.END)
    text_window1.insert(tk.END, "--Human Message--\n\n")
    # end_idx = text_window1.index(tk.END)
    # text_window1.tag_add("bold_large", start_idx, end_idx)
    text_window1.insert(tk.END, message + '\n\n')
    # start_idx = text_window1.index(tk.END)
    text_window1.insert(tk.END, "--AI Message--\n\n")
    # end_idx = text_window1.index(tk.END)
    # text_window1.tag_add("bold_large", start_idx, end_idx)
    text_window1.insert(tk.END, response[-1].content + '\n\n')
    text_window1.config(state="disabled")

    text_window2.config(state="normal")
    text_window2.delete(1.0, tk.END)
    for res in responses:
        # start_idx = text_window1.index(tk.END)
        text_window2.insert(tk.END, f"--{res['type']} Message--\n\n")
        # end_idx = text_window1.index(tk.END)
        # text_window2.tag_add("bold_large", start_idx, end_idx)
        text_window2.insert(tk.END, res["message"] + "\n\n")
    text_window2.config(state="disabled")


# Create the main application window
app = tk.Tk()
app.title("AI librarian")

app.geometry("1600x900")

app.config(bg="gray")

# Configure the grid layout
app.rowconfigure([0, 1, 2, 3], weight=1)
app.columnconfigure([0, 1], weight=1)

# Title stretching over column 0 and 1
title_label = tk.Label(app, text="Title", bg="lightblue", font=("Arial", 16))
title_label.grid(row=0, column=0, columnspan=2, sticky="nsew")

# Text display window in column 0, row 1
text_window1 = tk.Text(app, bg="lightgray", height=40, width=30, state="disabled", font=("Arial", 8), wrap="word", padx=5, pady=5)
text_window1.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
# text_window1.tag_configure("bold_large", font=("Arial", 12, "bold"))

text_window2 = tk.Text(app, bg="lightgray", height=40, width=30, state="disabled", font=("Arial", 8), wrap="word", padx=5, pady=5)
text_window2.grid(row=1, column=1, sticky="nsew", padx=5, pady=5)
# text_window2.tag_configure("bold_large", font=("Arial", 12, "bold"))

# Input window in column 0, row 2
input_window = tk.Entry(app, font=("Arial", 12))
input_window.grid(row=2, column=0, sticky="nsew", padx=5, pady=5, ipady=10)

# Submit button in column 1, row 2
submit_button = tk.Button(app, text="Submit", command=submit_message, font=("Arial", 20))
submit_button.grid(row=2, column=1, sticky="nsew", padx=5, pady=5, ipady=10)

# Close button at row 3, stretching over column 0 and 1
close_button = tk.Button(app, text="Close Application",
                         command=app.quit, bg="red", fg="white")
close_button.grid(row=3, column=0, columnspan=2, sticky="nsew", padx=5, pady=5)

# Run the application
app.mainloop()
