from build_tree_ui import *
from storage import *
from selection_window_ui import *

root = None
root_objective = None


def on_closing():
    global saved_once
    if not saved_once:
        user_decision = ask_to_save_tree()
        if user_decision == "save":
            filename = get_save_filename()
            if filename:
                save_tree_with_unique_name(root_objective, filename)
    root.destroy()


def on_selection_window_close():
    global root_tmp, root, root_objective
    root, root_objective = create_ui()
    if root_tmp is None:
        print("hell")
        root.protocol("WM_DELETE_WINDOW", on_closing)
        root.mainloop()
    else:
        print("hell")
        root.protocol("WM_DELETE_WINDOW", on_closing)
        root_objective = root_tmp
        root.mainloop()


def main():
    # selection_window.protocol("WM_DELETE_WINDOW", on_selection_window_close)
    selection_window.mainloop()  # 主循环


if __name__ == "__main__":
    main()