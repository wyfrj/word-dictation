# -*- coding: utf-8 -*-
"""
英语单词听写 - 安卓版 (Kivy)
- UI: Kivy
- 朗读: plyer.tts 调用安卓系统 TextToSpeech (桌面无此实现时自动忽略)
- 数据: words.json 存于 App.user_data_dir (安卓可写目录)
桌面也可直接运行 (python main.py) 预览界面。
"""

import json
import os
import random
import sys

# Windows 控制台编码修复
if sys.platform == "win32":
    import io
    sys.stdin = io.TextIOWrapper(sys.stdin.buffer, encoding="utf-8")
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")

from kivy.app import App
from kivy.core.text import LabelBase
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelItem
from kivy.uix.textinput import TextInput

# plyer 的 tts 在桌面平台可能未实现,容错导入
try:
    from plyer import tts as _tts
except Exception:
    _tts = None

# 颜色
BG = (0.13, 0.13, 0.15, 1)
OK = (0.18, 0.80, 0.44, 1)
ERR = (0.91, 0.30, 0.24, 1)
HINT = (0.6, 0.62, 0.65, 1)
PRIMARY = (0.20, 0.55, 0.90, 1)
CARD = (0.18, 0.18, 0.21, 1)


def register_cjk_font():
    """注册支持中文的字体, 覆盖 Kivy 默认字体, 否则中文显示为方块。"""
    candidates = [
        # 安卓系统字体
        "/system/fonts/NotoSansCJK-Regular.ttc",
        "/system/fonts/NotoSansSC-Regular.otf",
        "/system/fonts/DroidSansFallbackFull.ttf",
        "/system/fonts/DroidSansFallback.ttf",
        # 桌面 Windows 字体
        "C:/Windows/Fonts/msyh.ttc",
        "C:/Windows/Fonts/simhei.ttf",
    ]
    for path in candidates:
        if os.path.exists(path):
            try:
                LabelBase.register(name="Roboto", fn_regular=path)
                return path
            except Exception:
                continue
    return None


def speak(text):
    """调用系统 TTS 朗读, 失败则静默(桌面预览时无声)。"""
    if not text or _tts is None:
        return
    try:
        _tts.speak(text)
    except Exception:
        pass


def load_words(path):
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
    return []


def save_words(path, words):
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(words, f, ensure_ascii=False, indent=2)
    except Exception:
        pass


class DictationApp(App):
    def build(self):
        self.title = "英语单词听写"
        register_cjk_font()
        Window.clearcolor = BG

        self.data_path = os.path.join(self.user_data_dir, "words.json")
        self.words = load_words(self.data_path)

        # 听写状态
        self.quiz = []
        self.q_idx = 0
        self.q_correct = 0
        self.q_answered = 0

        panel = TabbedPanel(do_default_tab=False, tab_height=dp(48))
        tab1 = TabbedPanelItem(text="单词管理")
        tab2 = TabbedPanelItem(text="听写测试")
        tab1.add_widget(self._build_manage())
        tab2.add_widget(self._build_quiz())
        panel.add_widget(tab1)
        panel.add_widget(tab2)
        return panel

    # ---------- 单词管理 ----------
    def _build_manage(self):
        root = BoxLayout(orientation="vertical", padding=dp(10), spacing=dp(8))

        bar = BoxLayout(size_hint_y=None, height=dp(48), spacing=dp(6))
        self.in_word = TextInput(hint_text="英文单词", multiline=False, size_hint_x=0.38)
        self.in_meaning = TextInput(
            hint_text="中文释义(可选)", multiline=False, size_hint_x=0.42
        )
        btn_add = Button(text="添加", size_hint_x=0.2, background_color=PRIMARY)
        btn_add.bind(on_release=lambda *_: self.add_word())
        bar.add_widget(self.in_word)
        bar.add_widget(self.in_meaning)
        bar.add_widget(btn_add)
        root.add_widget(bar)

        self.count_lbl = Label(
            text="", size_hint_y=None, height=dp(24), color=HINT, font_size="13sp"
        )
        root.add_widget(self.count_lbl)

        scroll = ScrollView()
        self.list_grid = GridLayout(cols=1, size_hint_y=None, spacing=dp(6), padding=(0, dp(2)))
        self.list_grid.bind(minimum_height=self.list_grid.setter("height"))
        scroll.add_widget(self.list_grid)
        root.add_widget(scroll)

        self.refresh_list()
        return root

    def refresh_list(self):
        self.list_grid.clear_widgets()
        if not self.words:
            self.list_grid.add_widget(
                Label(text="单词库为空,在上方添加单词", color=HINT,
                      size_hint_y=None, height=dp(60))
            )
        else:
            for i, item in enumerate(self.words):
                self.list_grid.add_widget(self._word_row(i, item))
        self.count_lbl.text = f"共 {len(self.words)} 个单词"

    def _word_row(self, index, item):
        row = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(4), padding=(dp(6), 0))
        meaning = item["meaning"] if item["meaning"] else "(无释义)"
        row.add_widget(Label(
            text=f"[b]{item['word']}[/b]", markup=True, halign="left", valign="middle",
            size_hint_x=0.34, text_size=(dp(110), None),
        ))
        row.add_widget(Label(
            text=meaning, color=HINT, halign="left", valign="middle",
            size_hint_x=0.34, text_size=(dp(110), None), font_size="13sp",
        ))
        b_read = Button(text="朗读", size_hint_x=0.16, background_color=PRIMARY)
        b_read.bind(on_release=lambda *_, w=item["word"]: speak(w))
        b_del = Button(text="删除", size_hint_x=0.16, background_color=ERR)
        b_del.bind(on_release=lambda *_, it=item: self.delete_word(it))
        row.add_widget(b_read)
        row.add_widget(b_del)
        return row

    def add_word(self):
        word = self.in_word.text.strip()
        if not word:
            self.count_lbl.text = "单词不能为空"
            return
        if any(it["word"].lower() == word.lower() for it in self.words):
            self.count_lbl.text = f"'{word}' 已存在"
            return
        meaning = self.in_meaning.text.strip()
        self.words.append({"word": word, "meaning": meaning})
        save_words(self.data_path, self.words)
        self.in_word.text = ""
        self.in_meaning.text = ""
        self.refresh_list()
        speak(word)

    def delete_word(self, item):
        if item in self.words:
            self.words.remove(item)
            save_words(self.data_path, self.words)
            self.refresh_list()

    # ---------- 听写测试 ----------
    def _build_quiz(self):
        root = BoxLayout(orientation="vertical", padding=dp(12), spacing=dp(10))

        bar = BoxLayout(size_hint_y=None, height=dp(48), spacing=dp(6))
        self.in_count = TextInput(
            hint_text="数量(留空=全部)", multiline=False, input_filter="int",
            size_hint_x=0.4,
        )
        self.btn_start = Button(text="开始听写", size_hint_x=0.35, background_color=PRIMARY)
        self.btn_start.bind(on_release=lambda *_: self.start_quiz())
        self.btn_stop = Button(text="结束", size_hint_x=0.25, disabled=True)
        self.btn_stop.bind(on_release=lambda *_: self.finish_quiz())
        bar.add_widget(self.in_count)
        bar.add_widget(self.btn_start)
        bar.add_widget(self.btn_stop)
        root.add_widget(bar)

        self.lbl_progress = Label(
            text="点击开始, 根据读音输入拼写", font_size="20sp",
            size_hint_y=None, height=dp(60),
        )
        root.add_widget(self.lbl_progress)

        self.in_answer = TextInput(
            hint_text="输入听到的单词", multiline=False, disabled=True,
            size_hint_y=None, height=dp(50), font_size="18sp",
        )
        self.in_answer.bind(on_text_validate=lambda *_: self.submit_answer())
        root.add_widget(self.in_answer)

        btns = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(8))
        self.btn_replay = Button(text="重听", disabled=True)
        self.btn_replay.bind(on_release=lambda *_: self.replay())
        self.btn_submit = Button(text="提交", disabled=True, background_color=PRIMARY)
        self.btn_submit.bind(on_release=lambda *_: self.submit_answer())
        btns.add_widget(self.btn_replay)
        btns.add_widget(self.btn_submit)
        root.add_widget(btns)

        self.lbl_feedback = Label(text="", font_size="16sp", size_hint_y=None, height=dp(40))
        root.add_widget(self.lbl_feedback)
        self.lbl_score = Label(text="", font_size="20sp", color=OK)
        root.add_widget(self.lbl_score)
        return root

    def _set_running(self, running):
        self.in_answer.disabled = not running
        self.btn_submit.disabled = not running
        self.btn_replay.disabled = not running
        self.btn_stop.disabled = not running
        self.btn_start.disabled = running
        self.in_count.disabled = running

    def start_quiz(self):
        if not self.words:
            self.lbl_progress.text = "单词库为空, 请先添加单词"
            self.lbl_progress.color = ERR
            return
        raw = self.in_count.text.strip()
        total = len(self.words)
        if raw:
            n = int(raw)
            if not (1 <= n <= total):
                self.lbl_feedback.text = f"数量需为 1~{total}"
                self.lbl_feedback.color = ERR
                return
            total = n
        self.quiz = random.sample(self.words, total)
        self.q_idx = self.q_correct = self.q_answered = 0
        self.lbl_score.text = ""
        self.lbl_feedback.text = ""
        self._set_running(True)
        self._present()

    def _present(self):
        item = self.quiz[self.q_idx]
        self.lbl_progress.text = f"第 {self.q_idx + 1}/{len(self.quiz)} 个 · 请输入拼写"
        self.lbl_progress.color = (1, 1, 1, 1)
        self.in_answer.text = ""
        self.in_answer.focus = True
        speak(item["word"])

    def replay(self):
        if self.quiz and 0 <= self.q_idx < len(self.quiz):
            speak(self.quiz[self.q_idx]["word"])

    def submit_answer(self):
        if not self.quiz or self.btn_submit.disabled:
            return
        ans = self.in_answer.text.strip()
        if not ans:
            self.lbl_feedback.text = "请输入拼写或点击重听"
            self.lbl_feedback.color = HINT
            return
        item = self.quiz[self.q_idx]
        self.q_answered += 1
        if ans.lower() == item["word"].lower():
            self.q_correct += 1
            self.lbl_feedback.text = "✓ 正确!"
            self.lbl_feedback.color = OK
        else:
            extra = f"  ({item['meaning']})" if item["meaning"] else ""
            self.lbl_feedback.text = f"✗ 正确答案: {item['word']}{extra}"
            self.lbl_feedback.color = ERR
        self.q_idx += 1
        if self.q_idx < len(self.quiz):
            Clock.schedule_once(lambda dt: self._present(), 0.9)
        else:
            Clock.schedule_once(lambda dt: self.finish_quiz(), 0.9)

    def finish_quiz(self):
        self._set_running(False)
        self.lbl_progress.text = "听写结束"
        if self.q_answered == 0:
            self.lbl_score.text = "未作答任何单词"
            self.lbl_score.color = HINT
            return
        rate = self.q_correct / self.q_answered * 100
        self.lbl_score.color = OK if rate >= 60 else ERR
        self.lbl_score.text = f"得分 {self.q_correct}/{self.q_answered}   正确率 {rate:.0f}%"


if __name__ == "__main__":
    DictationApp().run()
