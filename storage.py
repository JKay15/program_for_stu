import pickle
from tkinter import filedialog, messagebox
import os

saved_once=False

def save_tree(tree, filename):
    with open(filename, 'wb') as file:
        pickle.dump(tree, file)

def load_tree(filename):
    with open(filename, 'rb') as file:
        tree = pickle.load(file)
    return tree

def get_save_filename():
    filename = filedialog.asksaveasfilename(initialdir=os.getcwd(),defaultextension=".pkl", filetypes=[("Pickle Files", "*.pkl")])
    return filename

def ask_to_save_tree():
    answer = messagebox.askyesnocancel("保存树", "是否保存当前的多叉树？")
    if answer is None:
        return "cancel"
    elif answer:
        return "save"
    else:
        return "discard"
    
def save_tree_with_unique_name(tree, filename):
    global saved_once 
    new_filename = filename
    counter = 1
    while os.path.exists(new_filename):
        filename_without_extension, extension = os.path.splitext(filename)
        new_filename = f"{filename_without_extension} ({counter}){extension}"
        counter += 1
    save_tree(tree, new_filename)
    saved_once = True  # 标记已保存
    
