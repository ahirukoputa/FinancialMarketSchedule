import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import calcu  # calcu.pyをインポート

class Model:
    def __init__(self):
        self.data = []
        self.de = calcu.DataEvents()
        self.year = self.de.get_today_year()
        self.data = self.de.load_events(self.year)

    def update_event(self, index, event):
        print("update_event")
        self.data[index][-1] = event

    def set_data(self,data):
        print("model.set_data:file-len : ",len(data))
        self.data = data

    def get_data(self):
        print("model.get_data:file-len : ", len(self.data))
        return self.data

class View:
    def __init__(self, root, controller):
        self.controller = controller
        self.tree = None
        self.setup_ui(root)

    def center_window(self,window): 
        window.update_idletasks() 
        width = window.winfo_screenwidth() 
        height = window.winfo_screenheight()
        return width,height

    def setup_ui(self, root):
        windows_width,window_height = self.center_window(root)
        form_width = 1200
        form_height = 500
        offset_width = (windows_width // 2) - (form_width // 2)
        offset_height = (window_height // 2) - (form_height // 2)
        root.geometry(f'{form_width}x{form_height}')

        menubar = tk.Menu(root)
        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label="Open", command=self.controller.open_file) # ラベルをOpenに変更 
        filemenu.add_command(label="Save", command=self.controller.save_file_as) # ラベルをSaveに変更 
        menubar.add_cascade(label="File", menu=filemenu) 
        root.config(menu=menubar) 
        #年選択コンボボックス
        self.year_var = tk.StringVar(value=str(self.controller.model.year)) 
        self.year_menu = ttk.Combobox(root, textvariable=self.year_var, values=[str(year) for year in range(2020, 2031)]) 
        self.year_menu.pack(pady=10) 
        self.year_menu.bind("<<ComboboxSelected>>", self.controller.on_year_selected) 
        #ツリービューを表示するフレーム
        frame = ttk.Frame(root,width=1200,height=400,padding=10) #width,heightは無視されている
        frame.pack(expand=True, fill='both') 
        #ツリービュー
        self.tree = ttk.Treeview(frame, columns=("weekday", "year", "month", "day", "event"), show="headings") 
        self.tree.heading("weekday", text="W") 
        self.tree.heading("year", text="Y") 
        self.tree.heading("month", text="M") 
        self.tree.heading("day", text="D") 
        self.tree.heading("event", text="Event") 
        self.tree.column("weekday", anchor='w',width=40, stretch=tk.NO) 
        self.tree.column("year", anchor='center', width=45, stretch=tk.NO) 
        self.tree.column("month", anchor='e', width=25, stretch=tk.NO) 
        self.tree.column("day", anchor='e', width=30, stretch=tk.NO) 
        self.tree.column("event", width=300, stretch=tk.YES) 
        self.style = ttk.Style() 
        self.style.configure("Treeview",font=(None, 12)) 
        self.style.configure("Treeview.Heading", foreground="gray", background="orange")#, font=( None, 10, "bold")) 
        self.tree.tag_configure("saturday", foreground="blue") 
        self.tree.tag_configure("sunday", foreground="red") 
        self.tree.tag_configure("evenrow",background="white") 
        self.tree.tag_configure("oddrow",background="#eeeeee") 

        xscrollbar = ttk.Scrollbar(frame, orient="horizontal", command=self.tree.xview) 
        yscrollbar = ttk.Scrollbar(frame, orient="vertical", command=self.tree.yview) 
        self.tree.configure(xscrollcommand=xscrollbar.set, yscrollcommand=yscrollbar.set) 
        yscrollbar.pack(side="right", fill="y") 
        xscrollbar.pack(side="bottom", fill="x")

        self.tree.bind("<Double-1>", self.controller.on_double_click) 
        self.tree.pack(expand=True, fill='both')

        root.geometry(f'{form_width}x{form_height}+{offset_width}+{offset_height}')
        
        self.update_treeview(self.controller.model.get_data())


    def update_treeview(self, data):
        # デバッグ用に呼び出し回数をログ出力 
        print(f"update_treeview called with data size: {len(data)}")
        #Treeviewの全アイテムを削除
        for row in self.tree.get_children():
            self.tree.delete(row)

        for index, row in enumerate(data):
            tag = ""
            if index % 2 == 0:
                tag = "evenrow"
            else:
                tag = "oddrow"
            if row[0] == "sat":
                tag = ("saturday", tag)
            elif row[0] == "sun":
                tag = ("sunday", tag)

            self.tree.insert("", "end", values=row, tags=tag, iid=index)

class Controller:
    def __init__(self, root):
        self.model = Model()
        self.view = View(root, self)
        self.root = root
        self.new_data(self.model.year)

        # キーボードショートカットの設定
        root.bind('<Control-s>', self.save_file_shortcut)

    def new_data(self, year):
        self.is_modified = False
        self.openfile_path = ''
        self.update_title("")
        self.model.set_data([])
        print("new_data : ",len(self.model.get_data()))
        newdata = self.model.de.load_events(year)
        print("new-year-data : ",len(newdata))
        self.update_and_refresh(newdata)

    def open_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt")])
        self.openfile_path = file_path
        if file_path:
            with open(file_path, "r") as file:
                data = [line.strip().split(",") for line in file.readlines()]
                self.update_and_refresh(data)
                self.update_title(file_path)
                self.is_modified = False
                # インポートしたデータの年を取得してリストボックスを更新
                imported_year = data[0][1]  # データの最初の行から年を取得
                self.model.year = int(imported_year)
                self.view.year_var.set(imported_year)  # リストボックスの値を更新

    def save_file_as(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text Files", "*.txt")])
        if file_path:
            self.save_file(file_path)
            return 1
        else :
            return 0

    def save_file(self, file_path):
        if file_path:
            with open(file_path, "w") as file:
                for row in self.model.get_data():
                    line = ",".join(map(str, row))
                    file.write(line + "\n")
            self.openfile_path = file_path
            self.is_modified = False
            self.update_title(file_path)

    def save_file_shortcut(self, event):
        if self.openfile_path == '':
            self.save_file_as()
        else:
            self.save_file(self.openfile_path)

    def update_title(self, path):
        title = "Calendar Data Viewer"
        if path:
            title += f" - {path}"
        else:
            title += " - 新規"
        if self.is_modified:
            title += " *"
        self.root.title(title)

    def on_year_selected(self, event):
        if self.is_modified:
            response = messagebox.askyesnocancel("Save Changes", "Do you want to save changes before changing the year?")
            if response is None:  # Cancel
                self.view.year_var.set(str(self.model.year))  # Reset combobox to current year
                return
            elif response:  # Yes
                if not self.save_file_as():
                    self.view.year_var.set(str(self.model.year))  # Reset combobox to current year
                    return
        
        year = int(self.view.year_var.get())
        self.model.year = year
        print("on_year_selected!!!!!")
        self.new_data(year)
        self.update_and_refresh(self.model.get_data())

    def on_double_click(self, event):
        item_id = self.view.tree.selection()[0]
        current_value = self.view.tree.item(item_id, "values")
        date_title = f"{current_value[1]}年 {current_value[2]}月 {current_value[3]}日"

        popup = tk.Toplevel()
        popup.title(f"Edit Event: {date_title}")
        popup.grab_set()

        tk.Label(popup, text="Event:").grid(row=0, column=0, padx=10, pady=10)
        event_var = tk.StringVar(value=current_value[4])
        event_entry = tk.Entry(popup, textvariable=event_var, width=50)
        event_entry.grid(row=0, column=1, padx=10, pady=10)
        event_entry.focus_set()

        def save_event():
            new_value = (current_value[0], current_value[1], current_value[2], current_value[3], event_var.get())
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
        print("update_and_refresh : ",len(data))
        #情報の更新
        self.model.set_data(data)
        self.view.update_treeview(data)

if __name__ == "__main__":
    root = tk.Tk()
    app = Controller(root)
    root.mainloop()
