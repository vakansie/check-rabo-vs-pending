import tkinter as tk
from tkinter import simpledialog
import pyautogui
from time import sleep
import csv
from typing import Callable

phrases_file = 'phrases.csv'

class UI:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Pasty Paste")
        self.create_elements()
        self.add_button = tk.Button(self.window, text='Add Line', command= lambda: self.add_line())
        self.refresh_button = tk.Button(self.window, text='Refresh', command= lambda: self.refresh())
        self.add_button.grid(row=len(phrases), column=0)
        self.refresh_button.grid(row=len(phrases), column=1)

    def create_elements(self):
        for position, phrase in enumerate(phrases.keys()):
            label = tk.Label(self.window, text=phrase, font=('calibre',10, 'bold'))
            button = tk.Button(self.window, text='Alt Tab and Paste', command= paste_func_gen(phrase))
            label.grid(row=position, column=0)
            button.grid(row=position, column=1)

    def add_line(self):
        line = get_new_phrase()
        if not line: return
        with open(phrases_file, encoding='utf-8', mode='a') as file:
            file.write(f'\n{line}')
        self.refresh()

    def refresh(self):
        ui.window.destroy()
        main()

def get_new_phrase() -> str:
    root = tk.Tk()
    root.withdraw()
    name = simpledialog.askstring("Input", "Enter Short Description:")
    sentence = simpledialog.askstring("Input", "Enter sentence to be pasted:")
    if not name or not sentence: return ''
    response = f'"{name}","{sentence}"'
    tk.messagebox.showinfo("Added:", response)
    return response

def paste_func_gen(text) -> Callable:
    def paste():
        pyautogui.hotkey('alt', 'tab')
        sleep(0.1)
        pyautogui.write(phrases[text])
    return lambda: paste()

def get_phrases_from_file() -> dict:
    with open(phrases_file, encoding='utf-8') as file:
        return {row[0]: row[1] for row in csv.reader(file)}

def main():
    global ui
    global phrases
    phrases = get_phrases_from_file()
    ui = UI()
    ui.window.mainloop()

if __name__ == '__main__':
    main()