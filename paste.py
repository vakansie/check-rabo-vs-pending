import tkinter as tk
from tkinter import simpledialog, messagebox
import pyautogui
from time import sleep
from typing import Callable
import sqlite3

phrases_db = 'phrases.db'

class UI:
    def __init__(self, phrases: dict):
        self.phrases = phrases
        self.window = tk.Tk()
        self.window.title("Pasty Paste")
        self.create_elements()
        self.add_button = tk.Button(self.window, text='Add Line', command= lambda: self.add_line())
        self.refresh_button = tk.Button(self.window, text='Refresh', command= lambda: self.refresh())
        self.add_button.grid(row=len(self.phrases), column=0)
        self.refresh_button.grid(row=len(self.phrases), column=1)

    def create_elements(self):
        for position, phrase in enumerate(self.phrases.keys()):
            label = tk.Label(self.window, text=phrase, font=('calibre',10, 'bold'))
            paste_button = tk.Button(self.window, text='Alt-Tab and Paste', command= paste_func_gen(phrase))
            delete_button = tk.Button(self.window, text='Delete', command= delete_func_gen(self, phrase))
            label.grid(row=position, column=0)
            paste_button.grid(row=position, column=1)
            delete_button.grid(row=position, column=2)

    def add_line(self):
        short_description, phrase = get_new_phrase()
        if not short_description or not phrase: return
        add_phrase_to_database(short_description, phrase)

    def refresh(self):
        self.window.destroy()
        main()

def get_new_phrase():
    sentence = ''
    def submit():
        nonlocal sentence
        sentence = text_entry.get("1.0", tk.END).strip()
        if sentence:
            messagebox.showinfo("Added:", name)
            root.destroy()
        else:
            messagebox.showwarning("Warning", "Please enter a sentence.")
            text_entry.focus_set()
    root = tk.Tk()
    root.withdraw()
    name = simpledialog.askstring("Input", "Enter Short Description:")
    text_window = tk.Toplevel(root)
    text_window.title("Enter sentence to be pasted:")
    text_entry = tk.Text(text_window, height=10, width=50)
    text_entry.pack()
    submit_button = tk.Button(text_window, text="Submit", command= lambda: submit())
    submit_button.pack()
    root.mainloop()
    return name, sentence

def paste_func_gen(text: str) -> Callable:
    def paste():
        pyautogui.hotkey('alt', 'tab')
        sleep(0.1)
        pyautogui.write(message=ui.phrases[text], _pause=False)
    return lambda: paste()

def delete_func_gen(ui: UI, short_description: str) -> Callable:
    def delete_row():
        conn = sqlite3.connect(phrases_db)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM Phrases WHERE short_description = ?', (short_description,))
        conn.commit()
        cursor.close()
        conn.close()
        ui.refresh()
    return lambda: delete_row()

def get_phrases_from_db() -> dict:
    conn = sqlite3.connect(phrases_db)
    cursor = conn.cursor()
    cursor.execute('SELECT short_description, phrase FROM Phrases')
    rows = cursor.fetchall()
    phrases = {short_desc: phrase for short_desc, phrase in rows}
    cursor.close()
    conn.close()
    return phrases

def add_phrase_to_database(short_description: str, phrase: str):
    conn = sqlite3.connect(phrases_db)
    cursor = conn.cursor()
    cursor.execute('INSERT INTO Phrases (short_description, phrase) VALUES (?, ?)', (short_description, phrase))
    conn.commit()
    cursor.close()
    conn.close()

def main():
    global ui
    phrases = get_phrases_from_db()
    print(phrases)
    ui = UI(phrases)
    ui.window.mainloop()

if __name__ == '__main__':
    main()