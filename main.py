import zipfile
import os
import plistlib
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk

# タブ1: Game Modeサポート追加機能
def add_game_mode_support(ipa_path, output_path):
    # IPAファイルを解凍
    temp_dir = 'temp'
    os.makedirs(temp_dir, exist_ok=True)

    with zipfile.ZipFile(ipa_path, 'r') as zip_ref:
        zip_ref.extractall(temp_dir)

    # Payload内の.appディレクトリを探索
    payload_dir = os.path.join(temp_dir, 'Payload')
    app_dir = None

    for item in os.listdir(payload_dir):
        if item.endswith('.app'):
            app_dir = os.path.join(payload_dir, item)
            break

    if app_dir is None:
        messagebox.showerror("エラー", "アプリのディレクトリが見つかりません。")
        return

    # Info.plistを読み込む
    info_plist_path = os.path.join(app_dir, 'Info.plist')

    try:
        # XML形式のplistを読み込み
        with open(info_plist_path, 'rb') as f:
            plist = plistlib.load(f)

        # GCSupportsGameModeキーが存在しない、またはFalseの場合はTrueに変更
        if 'GCSupportsGameMode' not in plist:
            plist['GCSupportsGameMode'] = True  # キーがない場合はTrueを追加
        elif plist['GCSupportsGameMode'] is False:
            plist['GCSupportsGameMode'] = True  # 既にFalseの場合はTrueに変更

        # 変更した内容を保存
        with open(info_plist_path, 'wb') as f:
            plistlib.dump(plist, f)  # XML形式で保存

    except (FileNotFoundError, plistlib.InvalidFileException) as e:
        messagebox.showerror("エラー", f"Info.plistの読み込みまたは保存でエラーが発生しました: {e}")
        return

    # 新しいIPAファイルを作成
    output_ipa_path = f'{output_path}/modified_{os.path.basename(ipa_path)}'
    with zipfile.ZipFile(output_ipa_path, 'w', zipfile.ZIP_DEFLATED) as zip_ref:
        for root, dirs, files in os.walk(temp_dir):
            for file in files:
                zip_ref.write(os.path.join(root, file), os.path.relpath(os.path.join(root, file), temp_dir))

    # 一時ディレクトリのクリーンアップ
    for root, dirs, files in os.walk(temp_dir, topdown=False):
        for file in files:
            os.remove(os.path.join(root, file))
        for dir in dirs:
            os.rmdir(os.path.join(root, dir))
    os.rmdir(temp_dir)

    messagebox.showinfo("成功", f"変更されたIPAファイルを出力しました: {output_ipa_path}")

def select_ipa_file():
    file_path = filedialog.askopenfilename(filetypes=[("IPA Files", "*.ipa")])
    if file_path:
        ipa_path_entry.delete(0, tk.END)
        ipa_path_entry.insert(0, file_path)

def select_output_dir():
    dir_path = filedialog.askdirectory()
    if dir_path:
        output_dir_entry.delete(0, tk.END)
        output_dir_entry.insert(0, dir_path)

def process_ipa():
    ipa_path = ipa_path_entry.get()
    output_path = output_dir_entry.get()

    if not ipa_path or not output_path:
        messagebox.showerror("エラー", "IPAファイルと出力先ディレクトリを指定してください。")
        return

    add_game_mode_support(ipa_path, output_path)

# タブ2: plistとbplist形式の相互変換
def convert_plist_to_bplist():
    plist_file = filedialog.askopenfilename(filetypes=[("Plist Files", "*.plist")])
    if plist_file:
        try:
            with open(plist_file, 'rb') as f:
                plist = plistlib.load(f)

            bplist_file = filedialog.asksaveasfilename(defaultextension=".bplist", filetypes=[("Binary Plist Files", "*.bplist")])
            if bplist_file:
                with open(bplist_file, 'wb') as f:
                    plistlib.dump(plist, f, fmt=plistlib.FMT_BINARY)

                messagebox.showinfo("成功", f"bplistファイルが作成されました: {bplist_file}")
        except Exception as e:
            messagebox.showerror("エラー", f"エラーが発生しました: {e}")

def convert_bplist_to_plist():
    bplist_file = filedialog.askopenfilename(filetypes=[("Binary Plist Files", "*.bplist")])
    if bplist_file:
        try:
            with open(bplist_file, 'rb') as f:
                bplist = plistlib.load(f, fmt=plistlib.FMT_BINARY)

            plist_file = filedialog.asksaveasfilename(defaultextension=".plist", filetypes=[("Plist Files", "*.plist")])
            if plist_file:
                with open(plist_file, 'wb') as f:
                    plistlib.dump(bplist, f, fmt=plistlib.FMT_XML)

                messagebox.showinfo("成功", f"plistファイルが作成されました: {plist_file}")
        except Exception as e:
            messagebox.showerror("エラー", f"エラーが発生しました: {e}")

# GUIの設定
root = tk.Tk()
root.title("複数機能ツール")
root.geometry("500x400")

# タブウィジェット
tab_control = ttk.Notebook(root)

# タブ1: Game Modeサポート追加
tab1 = ttk.Frame(tab_control)
tab_control.add(tab1, text="タブ1: Game Modeサポート追加")

# タブ2: plistとbplist形式の変換
tab2 = ttk.Frame(tab_control)
tab_control.add(tab2, text="タブ2: plistとbplist形式の変換")

tab_control.pack(expand=1, fill="both")

# タブ1: Game Modeサポート追加
ipa_label = tk.Label(tab1, text="IPAファイル:")
ipa_label.pack(pady=5)
ipa_path_entry = tk.Entry(tab1, width=40)
ipa_path_entry.pack(pady=5)
ipa_button = tk.Button(tab1, text="選択", command=select_ipa_file)
ipa_button.pack(pady=5)

output_label = tk.Label(tab1, text="出力先ディレクトリ:")
output_label.pack(pady=5)
output_dir_entry = tk.Entry(tab1, width=40)
output_dir_entry.pack(pady=5)
output_button = tk.Button(tab1, text="選択", command=select_output_dir)
output_button.pack(pady=5)

process_button = tk.Button(tab1, text="処理開始", command=process_ipa)
process_button.pack(pady=20)

# タブ2: plistとbplist形式の変換
convert_plist_button = tk.Button(tab2, text="plist to bplist", command=convert_plist_to_bplist)
convert_plist_button.pack(pady=10)

convert_bplist_button = tk.Button(tab2, text="bplist to plist", command=convert_bplist_to_plist)
convert_bplist_button.pack(pady=10)

# GUIの実行
root.mainloop()
