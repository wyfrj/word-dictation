# -*- coding: utf-8 -*-
"""
英语单词听写软件 - 图形界面版
基于 customtkinter,复用 dictation.py 中的语音与存储逻辑。
运行: python gui.py
"""

import random
import threading

import customtkinter as ctk

from dictation import Speaker, load_words, save_words

# 全局外观
ctk.set_appearance_mode("dark")          # dark / light / system
ctk.set_default_color_theme("blue")

# 颜色常量
COLOR_OK = "#2ecc71"
COLOR_ERR = "#e74c3c"
COLOR_HINT = "#9aa0a6"
COLOR_CARD = "#2b2b2b"


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("英语单词听写软件")
        self.geometry("900x640")
        self.minsize(780, 560)

        self.speaker = Speaker()
        self.words = load_words()

        # 听写状态
        self.quiz = []
        self.q_idx = 0
        self.q_correct = 0
        self.q_answered = 0

        # 字体
        self.f_title = ctk.CTkFont(size=26, weight="bold")
        self.f_sub = ctk.CTkFont(size=13)
        self.f_word = ctk.CTkFont(size=17, weight="bold")
        self.f_big = ctk.CTkFont(size=22, weight="bold")
        self.f_normal = ctk.CTkFont(size=14)

        self._build_header()
        self._build_tabs()
        self.refresh_list()

    # ---------- 语音 ----------
    def speak(self, text):
        """后台线程朗读,避免阻塞界面。"""
        if not text:
            return
        threading.Thread(target=self.speaker.say, args=(text,), daemon=True).start()

    # ---------- 顶部标题 ----------
    def _build_header(self):
        header = ctk.CTkFrame(self, corner_radius=0, height=80)
        header.pack(fill="x")
        ctk.CTkLabel(header, text="📖 英语单词听写", font=self.f_title).pack(
            anchor="w", padx=24, pady=(16, 0)
        )
        ctk.CTkLabel(
            header,
            text="添加单词 · 朗读发音 · 随机听写自动判分",
            font=self.f_sub,
            text_color=COLOR_HINT,
        ).pack(anchor="w", padx=24, pady=(0, 12))

    # ---------- 选项卡 ----------
    def _build_tabs(self):
        self.tabs = ctk.CTkTabview(self, corner_radius=12)
        self.tabs.pack(fill="both", expand=True, padx=16, pady=(0, 16))
        self.tab_manage = self.tabs.add("📝 单词管理")
        self.tab_quiz = self.tabs.add("🎧 听写测试")
        self._build_manage_tab()
        self._build_quiz_tab()

    # ===== 单词管理 =====
    def _build_manage_tab(self):
        tab = self.tab_manage
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_rowconfigure(1, weight=1)

        # 输入区
        bar = ctk.CTkFrame(tab, corner_radius=10)
        bar.grid(row=0, column=0, sticky="ew", padx=4, pady=(8, 6))
        bar.grid_columnconfigure(0, weight=2)
        bar.grid_columnconfigure(1, weight=3)

        self.entry_word = ctk.CTkEntry(
            bar, placeholder_text="英文单词", font=self.f_normal, height=38
        )
        self.entry_word.grid(row=0, column=0, sticky="ew", padx=(10, 6), pady=10)
        self.entry_meaning = ctk.CTkEntry(
            bar, placeholder_text="中文释义(可选)", font=self.f_normal, height=38
        )
        self.entry_meaning.grid(row=0, column=1, sticky="ew", padx=6, pady=10)
        ctk.CTkButton(
            bar, text="➕ 添加", width=90, height=38, command=self.add_word
        ).grid(row=0, column=2, padx=(6, 10), pady=10)

        self.entry_word.bind("<Return>", lambda e: self.entry_meaning.focus())
        self.entry_meaning.bind("<Return>", lambda e: self.add_word())

        # 列表区
        self.list_frame = ctk.CTkScrollableFrame(
            tab, corner_radius=10, label_text="单词库"
        )
        self.list_frame.grid(row=1, column=0, sticky="nsew", padx=4, pady=(6, 4))
        self.list_frame.grid_columnconfigure(0, weight=1)

        self.count_label = ctk.CTkLabel(
            tab, text="", font=self.f_sub, text_color=COLOR_HINT
        )
        self.count_label.grid(row=2, column=0, sticky="w", padx=8, pady=(0, 4))

    def refresh_list(self):
        """重建单词列表。"""
        for child in self.list_frame.winfo_children():
            child.destroy()

        if not self.words:
            ctk.CTkLabel(
                self.list_frame,
                text="单词库为空,先在上方添加单词吧~",
                text_color=COLOR_HINT,
                font=self.f_normal,
            ).grid(row=0, column=0, pady=30)
        else:
            for i, item in enumerate(self.words):
                self._build_word_row(i, item)

        self.count_label.configure(text=f"共 {len(self.words)} 个单词")

    def _build_word_row(self, index, item):
        row = ctk.CTkFrame(self.list_frame, corner_radius=8, fg_color=COLOR_CARD)
        row.grid(row=index, column=0, sticky="ew", padx=6, pady=4)
        row.grid_columnconfigure(2, weight=1)

        ctk.CTkLabel(row, text=f"{index + 1:>2}", width=28, text_color=COLOR_HINT).grid(
            row=0, column=0, padx=(10, 4), pady=8
        )
        ctk.CTkLabel(row, text=item["word"], font=self.f_word, anchor="w").grid(
            row=0, column=1, padx=6, pady=8, sticky="w"
        )
        meaning = item["meaning"] if item["meaning"] else "(无释义)"
        ctk.CTkLabel(
            row, text=meaning, font=self.f_normal, text_color=COLOR_HINT, anchor="w"
        ).grid(row=0, column=2, padx=6, pady=8, sticky="w")

        ctk.CTkButton(
            row, text="🔊 朗读", width=70, height=30,
            command=lambda w=item["word"]: self.speak(w),
        ).grid(row=0, column=3, padx=4, pady=6)
        ctk.CTkButton(
            row, text="🗑 删除", width=70, height=30,
            fg_color=COLOR_ERR, hover_color="#c0392b",
            command=lambda it=item: self.delete_word(it),
        ).grid(row=0, column=4, padx=(4, 10), pady=6)

    def add_word(self):
        word = self.entry_word.get().strip()
        if not word:
            self._toast(self.count_label, "单词不能为空", COLOR_ERR)
            return
        if any(it["word"].lower() == word.lower() for it in self.words):
            self._toast(self.count_label, f"'{word}' 已存在", COLOR_ERR)
            return
        meaning = self.entry_meaning.get().strip()
        self.words.append({"word": word, "meaning": meaning})
        save_words(self.words)
        self.entry_word.delete(0, "end")
        self.entry_meaning.delete(0, "end")
        self.entry_word.focus()
        self.refresh_list()
        self.speak(word)

    def delete_word(self, item):
        if item in self.words:
            self.words.remove(item)
            save_words(self.words)
            self.refresh_list()

    # ===== 听写测试 =====
    def _build_quiz_tab(self):
        tab = self.tab_quiz
        tab.grid_columnconfigure(0, weight=1)

        # 设置行
        setting = ctk.CTkFrame(tab, corner_radius=10)
        setting.grid(row=0, column=0, sticky="ew", padx=4, pady=(8, 10))
        ctk.CTkLabel(setting, text="听写数量:", font=self.f_normal).grid(
            row=0, column=0, padx=(12, 6), pady=12
        )
        self.entry_count = ctk.CTkEntry(
            setting, placeholder_text="留空=全部", width=120, height=36
        )
        self.entry_count.grid(row=0, column=1, padx=6, pady=12)
        self.btn_start = ctk.CTkButton(
            setting, text="▶ 开始听写", width=120, height=36, command=self.start_quiz
        )
        self.btn_start.grid(row=0, column=2, padx=6, pady=12)
        self.btn_stop = ctk.CTkButton(
            setting, text="■ 结束", width=90, height=36, state="disabled",
            fg_color="#7f8c8d", hover_color="#636e72", command=self.finish_quiz,
        )
        self.btn_stop.grid(row=0, column=3, padx=(6, 12), pady=12)

        # 听写卡片
        card = ctk.CTkFrame(tab, corner_radius=12)
        card.grid(row=1, column=0, sticky="ew", padx=4, pady=4)
        card.grid_columnconfigure(0, weight=1)

        self.lbl_progress = ctk.CTkLabel(
            card, text="点击「开始听写」,根据读音输入拼写", font=self.f_big
        )
        self.lbl_progress.grid(row=0, column=0, pady=(26, 14))

        self.entry_answer = ctk.CTkEntry(
            card, placeholder_text="在此输入听到的单词",
            font=ctk.CTkFont(size=18), height=46, width=380, justify="center",
            state="disabled",
        )
        self.entry_answer.grid(row=1, column=0, pady=10)
        self.entry_answer.bind("<Return>", lambda e: self.submit_answer())

        btns = ctk.CTkFrame(card, fg_color="transparent")
        btns.grid(row=2, column=0, pady=14)
        self.btn_replay = ctk.CTkButton(
            btns, text="🔁 重听", width=110, height=40, state="disabled",
            fg_color="#34495e", hover_color="#2c3e50", command=self.replay,
        )
        self.btn_replay.grid(row=0, column=0, padx=8)
        self.btn_submit = ctk.CTkButton(
            btns, text="✓ 提交", width=140, height=40, state="disabled",
            command=self.submit_answer,
        )
        self.btn_submit.grid(row=0, column=1, padx=8)

        self.lbl_feedback = ctk.CTkLabel(card, text="", font=self.f_word)
        self.lbl_feedback.grid(row=3, column=0, pady=(6, 8))
        self.lbl_score = ctk.CTkLabel(
            card, text="", font=self.f_big, text_color=COLOR_OK
        )
        self.lbl_score.grid(row=4, column=0, pady=(0, 24))

    def start_quiz(self):
        if not self.words:
            self.lbl_progress.configure(text="单词库为空,请先添加单词", text_color=COLOR_ERR)
            return
        raw = self.entry_count.get().strip()
        total = len(self.words)
        if raw:
            if not raw.isdigit() or not (1 <= int(raw) <= total):
                self.lbl_feedback.configure(
                    text=f"数量需为 1~{total} 的整数", text_color=COLOR_ERR
                )
                return
            total = int(raw)

        self.quiz = random.sample(self.words, total)
        self.q_idx = 0
        self.q_correct = 0
        self.q_answered = 0

        # 切换控件状态
        self._set_quiz_running(True)
        self.lbl_score.configure(text="")
        self.lbl_feedback.configure(text="")
        self._present_current()

    def _set_quiz_running(self, running):
        run_state = "normal" if running else "disabled"
        idle_state = "disabled" if running else "normal"
        self.entry_answer.configure(state=run_state)
        self.btn_submit.configure(state=run_state)
        self.btn_replay.configure(state=run_state)
        self.btn_stop.configure(state=run_state)
        self.btn_start.configure(state=idle_state)
        self.entry_count.configure(state=idle_state)

    def _present_current(self):
        item = self.quiz[self.q_idx]
        self.lbl_progress.configure(
            text=f"第 {self.q_idx + 1}/{len(self.quiz)} 个 · 请输入拼写",
            text_color=("gray10", "gray90"),
        )
        self.entry_answer.delete(0, "end")
        self.entry_answer.focus()
        self.speak(item["word"])

    def replay(self):
        if self.quiz and 0 <= self.q_idx < len(self.quiz):
            self.speak(self.quiz[self.q_idx]["word"])

    def submit_answer(self):
        if not self.quiz or self.btn_submit.cget("state") == "disabled":
            return
        ans = self.entry_answer.get().strip()
        if not ans:
            self.lbl_feedback.configure(text="请输入拼写或点击重听", text_color=COLOR_HINT)
            return
        item = self.quiz[self.q_idx]
        self.q_answered += 1
        if ans.lower() == item["word"].lower():
            self.q_correct += 1
            self.lbl_feedback.configure(text="✓ 正确!", text_color=COLOR_OK)
        else:
            meaning = f"  ({item['meaning']})" if item["meaning"] else ""
            self.lbl_feedback.configure(
                text=f"✗ 正确答案: {item['word']}{meaning}", text_color=COLOR_ERR
            )

        self.q_idx += 1
        if self.q_idx < len(self.quiz):
            self.after(900, self._present_current)  # 略停,让用户看清反馈
        else:
            self.after(900, self.finish_quiz)

    def finish_quiz(self):
        self._set_quiz_running(False)
        self.lbl_progress.configure(text="听写结束 🎉")
        if self.q_answered == 0:
            self.lbl_score.configure(text="未作答任何单词", text_color=COLOR_HINT)
            self.lbl_feedback.configure(text="")
            return
        rate = self.q_correct / self.q_answered * 100
        color = COLOR_OK if rate >= 60 else COLOR_ERR
        self.lbl_score.configure(
            text=f"得分 {self.q_correct}/{self.q_answered}   正确率 {rate:.0f}%",
            text_color=color,
        )

    # ---------- 小工具 ----------
    def _toast(self, label, text, color):
        """在指定 label 上短暂显示提示。"""
        old = label.cget("text")
        old_color = label.cget("text_color")
        label.configure(text=text, text_color=color)
        label.after(1800, lambda: label.configure(text=old, text_color=old_color))


if __name__ == "__main__":
    App().mainloop()
