# -*- coding: utf-8 -*-
"""
Помощник для переименования файлов (для Залифа)
Простая и дружелюбная программа для Windows 10.

Запуск: двойной щелчок, или из терминала:  python rename_zalif.py

Ничего на компьютере не меняется, пока вы не нажмёте большую зелёную
кнопку "Переименовать файлы". Любое действие можно отменить.
"""

import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox


APP_TITLE = "Помощник переименования (Залиф)"
USER_NAME = "Залиф"

# Спокойные, приятные цвета
BG = "#f4f7fb"
CARD = "#ffffff"
ACCENT = "#2e7d32"        # зелёный для главного действия
ACCENT_DARK = "#1b5e20"
TEXT = "#1f2d3d"
MUTED = "#5b6b7b"
BORDER = "#d6e0ea"


def greeting():
    """Возвращает приветствие в зависимости от времени суток."""
    import datetime
    hour = datetime.datetime.now().hour
    if hour < 6:
        part = "Доброй ночи"
    elif hour < 12:
        part = "Доброе утро"
    elif hour < 18:
        part = "Добрый день"
    else:
        part = "Добрый вечер"
    return part + ", " + USER_NAME + "!"


class RenameApp:
    def __init__(self, root):
        self.root = root
        self.folder = ""
        self.files = []          # список текущих имён файлов (только имя, без пути)
        self.last_batch = []     # список (старый_путь, новый_путь) для отмены

        root.title(APP_TITLE)
        root.configure(bg=BG)
        root.minsize(860, 720)

        self._build_styles()
        self._build_header()
        self._build_controls()
        self._build_preview()
        self._build_footer()

        self._refresh_preview()

    # ---------- оформление ----------
    def _build_styles(self):
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure("Treeview",
                        font=("Segoe UI", 11),
                        rowheight=28,
                        background=CARD,
                        fieldbackground=CARD,
                        foreground=TEXT)
        style.configure("Treeview.Heading",
                        font=("Segoe UI", 11, "bold"),
                        foreground=TEXT)
        style.map("Treeview", background=[("selected", "#cfe8d4")])

    # ---------- шапка ----------
    def _build_header(self):
        header = tk.Frame(self.root, bg=BG)
        header.pack(fill="x", padx=24, pady=(20, 8))

        tk.Label(header, text=greeting(), font=("Segoe UI", 22, "bold"),
                 bg=BG, fg=TEXT).pack(anchor="w")
        tk.Label(header,
                 text="Давайте наведём порядок в именах файлов. Выберите папку, "
                      "укажите, что изменить, проверьте предпросмотр и нажмите "
                      "переименовать. Ничего не произойдёт, пока вы сами не нажмёте "
                      "кнопку.",
                 font=("Segoe UI", 11), bg=BG, fg=MUTED,
                 justify="left", wraplength=800).pack(anchor="w", pady=(4, 0))

    # ---------- карточки ----------
    def _card(self, parent):
        outer = tk.Frame(parent, bg=BORDER)
        inner = tk.Frame(outer, bg=CARD)
        inner.pack(fill="both", expand=True, padx=1, pady=1)
        return outer, inner

    def _build_controls(self):
        wrap = tk.Frame(self.root, bg=BG)
        wrap.pack(fill="x", padx=24, pady=8)

        # Строка выбора папки
        outer, card = self._card(wrap)
        outer.pack(fill="x")
        row = tk.Frame(card, bg=CARD)
        row.pack(fill="x", padx=16, pady=14)

        tk.Label(row, text="Шаг 1.  Выберите папку", font=("Segoe UI", 12, "bold"),
                 bg=CARD, fg=TEXT).pack(anchor="w")

        pick_row = tk.Frame(card, bg=CARD)
        pick_row.pack(fill="x", padx=16, pady=(0, 14))

        self.folder_var = tk.StringVar(value="Папка ещё не выбрана")
        tk.Label(pick_row, textvariable=self.folder_var, font=("Segoe UI", 10),
                 bg="#eef3f8", fg=MUTED, anchor="w", padx=10, pady=8,
                 relief="flat").pack(side="left", fill="x", expand=True)

        tk.Button(pick_row, text="Обзор...", font=("Segoe UI", 11, "bold"),
                  bg="#1565c0", fg="white", activebackground="#0d47a1",
                  activeforeground="white", relief="flat", padx=18, pady=6,
                  cursor="hand2", command=self.choose_folder).pack(side="left", padx=(10, 0))

        # Карточка с настройками
        outer2, card2 = self._card(wrap)
        outer2.pack(fill="x", pady=(12, 0))

        tk.Label(card2, text="Шаг 2.  Укажите, что изменить",
                 font=("Segoe UI", 12, "bold"), bg=CARD, fg=TEXT).pack(
                     anchor="w", padx=16, pady=(14, 6))

        opts = tk.Frame(card2, bg=CARD)
        opts.pack(fill="x", padx=16, pady=(0, 14))

        # Новое общее имя для всех файлов (необязательно)
        self.newbase_var = tk.StringVar()
        self._labeled_entry(opts, "Новое имя для всех:", self.newbase_var, 0)
        tk.Label(opts, text="например Track. Оставьте пустым, чтобы сохранить имена.",
                 font=("Segoe UI", 9), bg=CARD, fg=MUTED).grid(
                     row=1, column=1, sticky="w", padx=(8, 0))

        # Найти и заменить
        self.find_var = tk.StringVar()
        self.replace_var = tk.StringVar()
        self._labeled_entry(opts, "или найти текст:", self.find_var, 2)
        self._labeled_entry(opts, "заменить на:", self.replace_var, 3)

        # Префикс и суффикс
        self.prefix_var = tk.StringVar()
        self.suffix_var = tk.StringVar()
        self._labeled_entry(opts, "добавить в начало:", self.prefix_var, 4)
        self._labeled_entry(opts, "добавить в конец:", self.suffix_var, 5)

        # Нумерация
        numrow = tk.Frame(opts, bg=CARD)
        numrow.grid(row=6, column=0, columnspan=2, sticky="w", pady=(10, 0))
        self.number_var = tk.BooleanVar(value=False)
        tk.Checkbutton(numrow, text="Добавить нумерацию (1, 2, 3 ...)",
                       variable=self.number_var, bg=CARD, fg=TEXT,
                       activebackground=CARD, font=("Segoe UI", 11),
                       selectcolor="#cfe8d4", cursor="hand2",
                       command=self._refresh_preview).pack(side="left")

        # Настройки нумерации
        numopts = tk.Frame(opts, bg=CARD)
        numopts.grid(row=7, column=0, columnspan=2, sticky="w", pady=(4, 0), padx=(24, 0))

        tk.Label(numopts, text="Где:", font=("Segoe UI", 10), bg=CARD,
                 fg=TEXT).pack(side="left")
        self.number_pos_var = tk.StringVar(value="в конце")
        pos_menu = ttk.Combobox(numopts, textvariable=self.number_pos_var, width=10,
                                state="readonly", font=("Segoe UI", 10),
                                values=["в конце", "в начале"])
        pos_menu.pack(side="left", padx=(4, 14))
        pos_menu.bind("<<ComboboxSelected>>", lambda e: self._refresh_preview())

        tk.Label(numopts, text="Разделитель:", font=("Segoe UI", 10), bg=CARD,
                 fg=TEXT).pack(side="left")
        self.sep_var = tk.StringVar(value="_")
        tk.Entry(numopts, textvariable=self.sep_var, font=("Segoe UI", 10), width=5,
                 relief="solid", bd=1).pack(side="left", padx=(4, 14))

        tk.Label(numopts, text="Начать с:", font=("Segoe UI", 10), bg=CARD,
                 fg=TEXT).pack(side="left")
        self.start_var = tk.StringVar(value="1")
        tk.Entry(numopts, textvariable=self.start_var, font=("Segoe UI", 10), width=5,
                 relief="solid", bd=1).pack(side="left", padx=(4, 14))

        self.pad_var = tk.BooleanVar(value=False)
        tk.Checkbutton(numopts, text="ведущие нули (01, 02)",
                       variable=self.pad_var, bg=CARD, fg=TEXT,
                       activebackground=CARD, font=("Segoe UI", 10),
                       selectcolor="#cfe8d4", cursor="hand2",
                       command=self._refresh_preview).pack(side="left")

        # Регистр букв
        caserow = tk.Frame(opts, bg=CARD)
        caserow.grid(row=8, column=0, columnspan=2, sticky="w", pady=(10, 0))
        tk.Label(caserow, text="Изменить буквы на:", font=("Segoe UI", 11),
                 bg=CARD, fg=TEXT).pack(side="left")
        self.case_var = tk.StringVar(value="Оставить как есть")
        case_menu = ttk.Combobox(caserow, textvariable=self.case_var, width=28,
                                 state="readonly", font=("Segoe UI", 10),
                                 values=["Оставить как есть",
                                         "все строчные",
                                         "ВСЕ ПРОПИСНЫЕ",
                                         "Первая Буква Каждого Слова"])
        case_menu.pack(side="left", padx=(8, 0))
        case_menu.bind("<<ComboboxSelected>>", lambda e: self._refresh_preview())

        # Живое обновление при вводе
        for var in (self.newbase_var, self.find_var, self.replace_var,
                    self.prefix_var, self.suffix_var, self.sep_var, self.start_var):
            var.trace_add("write", lambda *a: self._refresh_preview())

    def _labeled_entry(self, parent, label, var, row):
        tk.Label(parent, text=label, font=("Segoe UI", 11), bg=CARD, fg=TEXT,
                 width=20, anchor="w").grid(row=row, column=0, sticky="w", pady=4)
        e = tk.Entry(parent, textvariable=var, font=("Segoe UI", 11), width=44,
                     relief="solid", bd=1)
        e.grid(row=row, column=1, sticky="w", pady=4, padx=(8, 0))

    # ---------- предпросмотр ----------
    def _build_preview(self):
        wrap = tk.Frame(self.root, bg=BG)
        wrap.pack(fill="both", expand=True, padx=24, pady=8)

        tk.Label(wrap, text="Шаг 3.  Проверьте предпросмотр (старое имя  ->  новое имя)",
                 font=("Segoe UI", 12, "bold"), bg=BG, fg=TEXT).pack(anchor="w")

        table_wrap = tk.Frame(wrap, bg=BORDER)
        table_wrap.pack(fill="both", expand=True, pady=(6, 0))

        cols = ("old", "new")
        self.tree = ttk.Treeview(table_wrap, columns=cols, show="headings")
        self.tree.heading("old", text="Текущее имя")
        self.tree.heading("new", text="Новое имя")
        self.tree.column("old", width=380, anchor="w")
        self.tree.column("new", width=380, anchor="w")

        vsb = ttk.Scrollbar(table_wrap, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        self.tree.pack(side="left", fill="both", expand=True, padx=1, pady=1)
        vsb.pack(side="right", fill="y")

        self.tree.tag_configure("changed", foreground=ACCENT_DARK)
        self.tree.tag_configure("same", foreground=MUTED)
        self.tree.tag_configure("clash", foreground="#c62828")

    # ---------- нижняя панель / действия ----------
    def _build_footer(self):
        footer = tk.Frame(self.root, bg=BG)
        footer.pack(fill="x", padx=24, pady=(8, 20))

        self.status_var = tk.StringVar(value="Чтобы начать, выберите папку.")
        tk.Label(footer, textvariable=self.status_var, font=("Segoe UI", 10),
                 bg=BG, fg=MUTED).pack(side="left")

        self.undo_btn = tk.Button(footer, text="Отменить последнее переименование",
                                  font=("Segoe UI", 11, "bold"),
                                  bg="#ef6c00", fg="white",
                                  activebackground="#e65100", activeforeground="white",
                                  relief="flat", padx=16, pady=10, cursor="hand2",
                                  state="disabled", command=self.undo)
        self.undo_btn.pack(side="right", padx=(10, 0))

        self.rename_btn = tk.Button(footer, text="Переименовать файлы",
                                    font=("Segoe UI", 13, "bold"),
                                    bg=ACCENT, fg="white",
                                    activebackground=ACCENT_DARK,
                                    activeforeground="white",
                                    relief="flat", padx=24, pady=10, cursor="hand2",
                                    command=self.apply_rename)
        self.rename_btn.pack(side="right")

    # ---------- логика ----------
    def choose_folder(self):
        chosen = filedialog.askdirectory(title="Выберите папку с файлами для переименования")
        if not chosen:
            return
        self.folder = chosen
        self.folder_var.set(chosen)
        self._load_files()
        self._refresh_preview()

    def _load_files(self):
        try:
            entries = sorted(os.listdir(self.folder), key=str.lower)
        except OSError as exc:
            messagebox.showerror("Не удалось открыть папку", str(exc))
            self.files = []
            return
        # Только настоящие файлы, без папок и скрытых системных файлов
        self.files = [f for f in entries
                      if os.path.isfile(os.path.join(self.folder, f))
                      and not f.startswith(".")]

    def _new_name_for(self, name, index, total):
        base, ext = os.path.splitext(name)

        newbase = self.newbase_var.get().strip()
        if newbase:
            # Дать всем файлам одно общее имя (номер ниже сделает их разными)
            base = newbase
        else:
            # Найти и заменить (только в имени, расширение .xxx не трогаем)
            find = self.find_var.get()
            if find:
                base = base.replace(find, self.replace_var.get())

        # Изменение регистра
        mode = self.case_var.get()
        if mode == "все строчные":
            base = base.lower()
        elif mode == "ВСЕ ПРОПИСНЫЕ":
            base = base.upper()
        elif mode == "Первая Буква Каждого Слова":
            base = base.title()

        # Префикс и суффикс
        base = self.prefix_var.get() + base + self.suffix_var.get()

        # Нумерация
        if self.number_var.get():
            try:
                start = int(self.start_var.get())
            except ValueError:
                start = 1
            number = start + index
            sep = self.sep_var.get()
            if self.pad_var.get():
                last = start + max(total - 1, 0)
                width = max(2, len(str(last)))
                num_str = str(number).zfill(width)
            else:
                num_str = str(number)
            if self.number_pos_var.get() == "в начале":
                base = num_str + sep + base
            else:
                base = base + sep + num_str

        return base + ext

    def _planned(self):
        """Возвращает список (старое_имя, новое_имя)."""
        total = len(self.files)
        return [(name, self._new_name_for(name, i, total))
                for i, name in enumerate(self.files)]

    def _refresh_preview(self):
        self.tree.delete(*self.tree.get_children())
        if not self.folder:
            self.status_var.set("Чтобы начать, выберите папку.")
            return

        plan = self._planned()
        new_names = [n for _, n in plan]
        changes = 0
        clashes = set()

        # Поиск повторяющихся новых имён
        seen = {}
        for n in new_names:
            seen[n] = seen.get(n, 0) + 1
        dupes = {n for n, c in seen.items() if c > 1}

        for old, new in plan:
            if new in dupes or (not new.strip()):
                tag = "clash"
                clashes.add(new)
            elif old != new:
                tag = "changed"
                changes += 1
            else:
                tag = "same"
            self.tree.insert("", "end", values=(old, new), tags=(tag,))

        if not self.files:
            self.status_var.set("В этой папке нет файлов для переименования.")
            self.rename_btn.config(state="disabled")
        elif clashes:
            self.status_var.set("У некоторых файлов получилось бы одинаковое имя "
                                "(показаны красным). Измените настройки перед "
                                "переименованием.")
            self.rename_btn.config(state="disabled")
        elif changes == 0:
            self.status_var.set("Пока менять нечего. Укажите настройки выше.")
            self.rename_btn.config(state="disabled")
        else:
            self.status_var.set("Будет переименовано файлов: " + str(changes) + ".")
            self.rename_btn.config(state="normal")

    def apply_rename(self):
        plan = [(o, n) for o, n in self._planned() if o != n]
        if not plan:
            return

        count = len(plan)
        if not messagebox.askyesno(
                "Подтвердите",
                "Переименовать файлов: " + str(count) + " в этой папке?\n\n"
                + self.folder + "\n\nСразу после этого можно будет отменить."):
            return

        done = []
        try:
            # Переименование в два прохода через временные имена. Это исключает
            # конфликты, когда файлы меняются именами местами.
            temp_map = []
            for i, (old, new) in enumerate(plan):
                old_path = os.path.join(self.folder, old)
                temp_path = os.path.join(self.folder, "__renaming_tmp_" + str(i) + "__")
                os.rename(old_path, temp_path)
                temp_map.append((temp_path, new, old))

            for temp_path, new, old in temp_map:
                new_path = os.path.join(self.folder, new)
                os.rename(temp_path, new_path)
                done.append((os.path.join(self.folder, old), new_path))
        except OSError as exc:
            messagebox.showerror("Что-то пошло не так",
                                 "Не удалось переименовать файл:\n\n" + str(exc)
                                 + "\n\nУже переименованные файлы сохранены. "
                                   "Можно нажать отмену, чтобы вернуть их обратно.")

        self.last_batch = done
        self.undo_btn.config(state="normal" if done else "disabled")
        self._load_files()
        self._refresh_preview()
        messagebox.showinfo("Готово",
                            "Переименовано файлов: " + str(len(done)) + ". "
                            + "Отлично, " + USER_NAME + "!")

    def undo(self):
        if not self.last_batch:
            return
        if not messagebox.askyesno("Отмена",
                                   "Вернуть имена файлов как было?"):
            return
        restored = 0
        # В обратном порядке, снова через временные имена для надёжности
        for i, (old_path, new_path) in enumerate(reversed(self.last_batch)):
            try:
                if os.path.exists(new_path):
                    os.rename(new_path, old_path)
                    restored += 1
            except OSError as exc:
                messagebox.showerror("Не удалось отменить", str(exc))
                break
        self.last_batch = []
        self.undo_btn.config(state="disabled")
        self._load_files()
        self._refresh_preview()
        messagebox.showinfo("Отменено",
                            "Возвращено имён: " + str(restored) + ".")


def main():
    root = tk.Tk()
    RenameApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
