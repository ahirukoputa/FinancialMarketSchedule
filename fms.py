
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import calcu  # calcu.pyをインポート
import config 
import pandas as pd

class Model:
    def __init__(self):
        print("Model")
        self.data = pd.DataFrame(columns=config.treeview_columns)
        self.de = calcu.DataEvents()
        
    def update_event(self, index, event):
        print("model_update_event")
        self.data.at[index, 'event'] = event

    def erase_data(self):
        print("model_erase_data:", len(self.data))
        self.data = pd.DataFrame(columns=config.treeview_columns)
    
    def set_data(self):
        print("model_set_data")
        self.de.load_annual_data(config.current_year)
        self.ss = calcu.ScheduleSaver()
        self.ss.load_events(config.current_year)
        self.de.load_and_merge_schedules(config.event_filenames)
        finance_filename = 'finance-' + str(config.current_year) + '.csv'
        self.de.load_finance_and_merge_schedules(finance_filename)
        self.data = self.de.get_data()

    def get_data(self):
        print("model_get_data:", len(self.data))
        return self.data

class View:
    def __init__(self, root, controller):
        print("View")
        self.controller = controller
        self.tree = None
        self.setup_ui(root)

    def center_window(self, window): 
        print("view_center_window")
        window.update_idletasks() 
        width = window.winfo_screenwidth() 
        height = window.winfo_screenheight()
        return width, height

    def setup_ui(self, root):
        print("view_setup_ui")
        #self.init_window(root)
        self.create_menu(root)
        self.create_combobox(root)
        frame = self.create_treeview_frame(root)
        self.setup_treeview(frame)
        self.apply_styles()
        self.create_scrollbars(frame)
        self.tree.bind("<Double-1>", self.controller.on_double_click)
        self.init_window(root)
        self.update_treeview(self.controller.model.get_data())

    def init_window(self, root):
        print("view_init_window")
        windows_width, window_height = self.center_window(root)
        offset_width = (windows_width // 2) - (config.form_width // 2)
        offset_height = (window_height // 2) - (config.form_height // 2)
        root.geometry(f'{config.form_width}x{config.form_height}+{offset_width}+{offset_height}')

    def create_menu(self, root):
        print("view_create_menu")
        menubar = tk.Menu(root)
        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label="Open", command=self.controller.open_file)
        filemenu.add_command(label="Save", command=self.controller.save_file_as)
        menubar.add_cascade(label="File", menu=filemenu)
        root.config(menu=menubar)

    def create_combobox(self, root):
        print("view_create_combobox")
        self.year_var = tk.StringVar(value=str(config.current_year))
        self.year_menu = ttk.Combobox(root, textvariable=self.year_var, values=[str(year) for year in range(2020, 2031)])
        self.year_menu.pack(pady=10)
        self.year_menu.bind("<<ComboboxSelected>>", self.controller.on_year_selected)

    def create_treeview_frame(self, root):
        print("view_create_treeview_frame")
        frame = ttk.Frame(root, width=config.form_width, height=400, padding=10)
        frame.pack(expand=True, fill='both')
        return frame

    def setup_treeview(self, frame):
        print("view_setup_treeview")
        self.tree = ttk.Treeview(frame, columns=config.treeview_columns, show="headings")
        for i, col in enumerate(config.treeview_columns):
            self.tree.heading(col, text=config.treeview_columns_text[i])
            self.tree.column(col, anchor=config.column_configs[col]['anchor'], width=config.column_configs[col]['width'], stretch=config.column_configs[col]['stretch'])
        self.tree.pack(expand=True, fill='both')

    def apply_styles(self):
        print("view_apply_styles")
        self.style = ttk.Style()
        self.style.theme_use('vista')
        self.style.configure("Treeview", background="orange", font=(None, 10))
        self.style.configure("Treeview.Heading", background="orange")
        for tag in config.tag_configs:
            self.tree.tag_configure(tag, foreground=config.tag_configs[tag]['foreground'], background=config.tag_configs[tag]['background'])

    def create_scrollbars(self, frame):
        print("view_create_scrollbars")
        yscrollbar = ttk.Scrollbar(frame, orient="vertical", command=self.tree.yview, style="Vertical.TScrollbar")
        yscrollbar.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=yscrollbar.set)
        self.tree.pack(side="left", expand=True, fill="both")

    def update_treeview(self, data):
        print("view_update_treeview")

        # Treeviewの全アイテムを削除
        for row in self.tree.get_children():
            self.tree.delete(row)

        for index, row in data.iterrows():
            tag = ""
            if index % 2 == 0:
                tag = "evenrow"
            else:
                tag = "oddrow"
            if row['weekday'] == "sat":
                tag = ("saturday", tag)
            elif row['weekday'] == "sun":
                tag = ("sunday", tag)

            self.tree.insert("", "end", values=row.tolist(), tags=tag, iid=index)

class Controller:
    def __init__(self, root):
        print("Controller")
        self.model = Model()
        self.view = View(root, self)
        self.root = root
        self.new_data()

        # キーボードショートカットの設定
        root.bind('<Control-s>', self.save_file_shortcut)

    def new_data(self):
        print("controller_new_data")
        self.is_modified = False
        self.openfile_path = ''
        self.update_title("")
        #Modelデータの初期化
        self.model.erase_data()
        self.model.set_data()
        newdata = self.model.get_data()
        self.update_and_refresh(newdata)

    def open_file(self):
        print("controller_open_file")
        file_path = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt")])
        self.openfile_path = file_path
        if file_path:
            with open(file_path, "r") as file:
                data = pd.read_csv(file)
                self.update_and_refresh(data)
                self.update_title(file_path)
                self.is_modified = False
                # インポートしたデータの年を取得してリストボックスを更新
                imported_year = data.iloc[0, 1]  # データの最初の行から年を取得
                self.model.year = int(imported_year)
                self.view.year_var.set(imported_year)  # リストボックスの値を更新

    def save_file_as(self):
        print("controller_save_file_as")
        file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text Files", "*.txt")])
        if file_path:
            self.save_file(file_path)
            return 1
        else :
            return 0

    def save_file(self, file_path):
        print("controller_save_file")
        if file_path:
            self.model.get_data().to_csv(file_path, index=False)
            self.openfile_path = file_path
            self.is_modified = False
            self.update_title(file_path)

    def save_file_shortcut(self, event):
        print("controller_save_file_shortcut")
        if self.openfile_path == '':
            self.save_file_as()
        else:
            self.save_file(self.openfile_path)

    def update_title(self, path):
        print("controller_update_title")
        title = "Calendar Data Viewer"
        if path:
            title += f" - {path}"
        else:
            title += " - 新規"
        if self.is_modified:
            title += " *"
        self.root.title(title)

    def on_year_selected(self, event):
        print("controller_on_year_selected")
        if self.is_modified:
            response = messagebox.askyesnocancel("Save Changes", "Do you want to save changes before changing the year?")
            if response is None:  # Cancel
                self.view.year_var.set(str(config.current_year))  # Reset combobox to current year
                return
            elif response:  # Yes
                if not self.save_file_as():
                    self.view.year_var.set(str(config.current_year))  # Reset combobox to current year
                    return
        
        year = int(self.view.year_var.get())
        config.current_year = year
        print("on_year_selected!!!!!")
        self.new_data()
        self.update_and_refresh(self.model.get_data())

    def on_double_click(self, event):
        print("controller_on_double_click")
        item_id = self.view.tree.selection()[0]
        event_index = config.treeview_columns.index("event")
        
        current_value = self.view.tree.item(item_id, "values")
        date_title = f"{current_value[1]}年 {current_value[2]}月 {current_value[3]}日"

        popup = tk.Toplevel()
        popup.title(f"Edit Event: {date_title}")
        popup.grab_set()

        tk.Label(popup, text="Event:").grid(row=0, column=0, padx=10, pady=10)
        event_var = tk.StringVar(value=current_value[event_index])
        event_entry = tk.Entry(popup, textvariable=event_var, width=160)
        event_entry.grid(row=0, column=1, padx=10, pady=10)
        event_entry.focus_set()

        def save_event():
            new_value = list(current_value)
            new_value[event_index] = event_var.get()
            self.model.update_event(int(item_id), event_var.get())
            self.update_and_refresh(self.model.get_data())
            self.is_modified = True
            self.update_title(self.openfile_path)
            popup.destroy()

        def cancel_event():
            popup.destroy()

        tk.Button(popup, text="OK", command=save_event).grid(row=1, column=1, pady=10, padx=10)
        tk.Button(popup, text="キャンセル", command=cancel_event).grid(row=1, column=0, pady=10, padx=10)

        # ポップアップウィンドウを中央に配置
        popup.update_idletasks() 
        width = popup.winfo_width() 
        height = popup.winfo_height() 
        x = (popup.winfo_screenwidth() // 2) - (width // 2) 
        y = (popup.winfo_screenheight() // 2) - (height // 2)
        popup.geometry(f'{width}x{height}+{x}+{y}')

    def update_and_refresh(self, data):
        print("controller_update_and_refresh")
        #情報の更新
        self.view.update_treeview(data)

if __name__ == "__main__":
    root = tk.Tk()
    app = Controller(root)
    root.mainloop()
