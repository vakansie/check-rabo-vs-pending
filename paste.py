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
        self.add_button = tk.Button(self.window, text='Add Line', command= self.add_line)
        self.refresh_button = tk.Button(self.window, text='Refresh', command= self.refresh)
        self.add_button.grid(row=len(self.phrases), column=0)
        self.refresh_button.grid(row=len(self.phrases), column=1)

    def create_elements(self):
        for position, phrase in enumerate(self.phrases.keys()):
            label = tk.Label(self.window, text=phrase, font=('calibre',10, 'bold'))
            paste_button = tk.Button(self.window, text='Alt-Tab and Paste', command= paste_func_gen(phrase))
            delete_button = tk.Button(self.window, text='Delete', command= delete_func_gen(self, self.phrases[phrase]))
            label.grid(row=position, column=0)
            paste_button.grid(row=position, column=1)
            delete_button.grid(row=position, column=2)

    def add_line(self):
        short_description, phrase = get_new_phrase()
        if not short_description or not phrase: return
        database.add_phrase_to_database(short_description, phrase)
        self.refresh()

    def refresh(self):
        self.window.destroy()
        main()

class Service:
    def __init__(self, database) -> None:
        self.database = database
        self.connection = sqlite3.connect(database)
        self.cursor = self.connection.cursor()

    def get_phrases_from_db(self) -> dict:
        self.cursor.execute('SELECT short_description, phrase FROM Phrases')
        rows = self.cursor.fetchall()
        phrases = {short_desc: phrase for short_desc, phrase in rows}
        return phrases

    def add_phrase_to_database(self, short_description: str, phrase: str):
        self.cursor.execute('INSERT INTO Phrases (short_description, phrase) VALUES (?, ?)', (short_description, phrase))
        self.connection.commit()

def get_new_phrase():
    sentence = ''
    def submit():
        nonlocal sentence
        sentence = text_entry.get("1.0", tk.END).strip()
        if not sentence: return
        messagebox.showinfo("Added:", name)
        root.destroy()
    root = tk.Tk()
    root.withdraw()
    name = simpledialog.askstring("Input", "Enter Short Description:")
    text_window = tk.Toplevel(root)
    text_window.title("Enter sentence to be pasted:")
    text_entry = tk.Text(text_window, height=10, width=50)
    text_entry.pack()
    submit_button = tk.Button(text_window, text="Submit", command= submit)
    submit_button.pack()
    root.mainloop()
    return name, sentence

def paste_func_gen(text: str) -> Callable:
    def paste():
        pyautogui.hotkey('alt', 'tab')
        sleep(0.1)
        pyautogui.write(message=ui.phrases[text], _pause=False)
    return paste

def delete_func_gen(ui: UI, phrase: str) -> Callable:
    def delete_row():
        database.cursor.execute('DELETE FROM Phrases WHERE phrase = ?', (phrase,))
        database.connection.commit()
        ui.refresh()
    return delete_row

def main():
    global ui
    global database
    database = Service(phrases_db)
    phrases = database.get_phrases_from_db()
    print(phrases)
    ui = UI(phrases)
    ui.window.mainloop()

if __name__ == '__main__':
    main()