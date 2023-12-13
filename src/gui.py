import tkinter as tk


def show_modal_window(categories):
    root = tk.Tk()
    root.title("Выбор аккаунтов")

    selected_categories = []

    def on_checkbox_clicked(category, value):
        if value.get():
            selected_categories.append(category)
        else:
            selected_categories.remove(category)

    for i, category in enumerate(categories):
        var = tk.BooleanVar()
        checkbox = tk.Checkbutton(
            root,
            text=category,
            variable=var,
            command=lambda c=category, v=var: on_checkbox_clicked(c, v),
        )
        checkbox.pack()

    ok_button = tk.Button(root, text="OK", command=root.destroy)
    ok_button.pack()

    root.mainloop()

    return selected_categories
