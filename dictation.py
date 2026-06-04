# -*- coding: utf-8 -*-
"""
英语单词听写软件
功能:
  1. 添加单词(可附中文释义)
  2. 查看 / 删除单词
  3. 朗读单词
  4. 随机报听写并自动判分
单词保存在同目录的 words.json 中。
依赖: pyttsx3 (离线语音, Windows 使用系统 SAPI5)
"""

import json
import os
import random
import sys

import pyttsx3

# Windows 控制台/管道默认编码常为 GBK,会导致中文输入输出乱码,统一改为 UTF-8
for stream in (sys.stdin, sys.stdout):
    try:
        stream.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

# 单词库文件路径: 打包成 exe 后存到 exe 所在目录,否则存到脚本目录
# (onefile 模式下 __file__ 指向临时解压目录,不能用于持久化)
if getattr(sys, "frozen", False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, "words.json")


class Speaker:
    """封装语音引擎,负责朗读英文单词。

    注意: pyttsx3 的同一引擎实例在一次 runAndWait() 之后,
    循环中再次朗读常会静默(SAPI5 已知缺陷),因此每次朗读都新建引擎。
    """

    def __init__(self, rate=150):
        self.rate = rate
        # 启动时选定一个英文嗓音 id,后续复用,保证发音准确
        engine = pyttsx3.init()
        self.voice_id = None
        for voice in engine.getProperty("voices"):
            name = (voice.name or "").lower()
            if "english" in name or "zira" in name or "david" in name:
                self.voice_id = voice.id
                break
        engine.stop()
        del engine

    def say(self, text):
        engine = pyttsx3.init()
        engine.setProperty("rate", self.rate)  # 语速
        if self.voice_id:
            engine.setProperty("voice", self.voice_id)
        engine.say(text)
        engine.runAndWait()
        engine.stop()
        del engine


def load_words():
    """读取单词库,返回 [{'word':..., 'meaning':...}, ...]。"""
    if not os.path.exists(DATA_FILE):
        return []
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        print("警告: 单词库文件损坏或无法读取,已按空库处理。")
        return []


def save_words(words):
    """把单词库写回磁盘。"""
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(words, f, ensure_ascii=False, indent=2)


def add_word(words, speaker):
    """添加一个新单词。"""
    word = input("请输入英文单词: ").strip()
    if not word:
        print("单词不能为空。\n")
        return
    # 检查是否已存在(忽略大小写)
    for item in words:
        if item["word"].lower() == word.lower():
            print(f"单词 '{word}' 已存在。\n")
            return
    meaning = input("请输入中文释义(可留空): ").strip()
    words.append({"word": word, "meaning": meaning})
    save_words(words)
    print(f"已添加: {word}  {meaning}")
    speaker.say(word)  # 添加后朗读一遍,加深印象
    print()


def list_words(words):
    """列出全部单词。"""
    if not words:
        print("单词库为空。\n")
        return
    print(f"\n共 {len(words)} 个单词:")
    for i, item in enumerate(words, 1):
        meaning = item["meaning"] if item["meaning"] else "(无释义)"
        print(f"  {i:>3}. {item['word']:<20} {meaning}")
    print()


def delete_word(words):
    """按编号删除单词。"""
    list_words(words)
    if not words:
        return
    raw = input("请输入要删除的编号(回车取消): ").strip()
    if not raw:
        return
    if not raw.isdigit() or not (1 <= int(raw) <= len(words)):
        print("编号无效。\n")
        return
    removed = words.pop(int(raw) - 1)
    save_words(words)
    print(f"已删除: {removed['word']}\n")


def read_word(words, speaker):
    """朗读指定单词。"""
    list_words(words)
    if not words:
        return
    raw = input("请输入要朗读的编号(回车取消): ").strip()
    if not raw:
        return
    if not raw.isdigit() or not (1 <= int(raw) <= len(words)):
        print("编号无效。\n")
        return
    item = words[int(raw) - 1]
    print(f"正在朗读: {item['word']}")
    speaker.say(item["word"])
    print()


def dictation(words, speaker):
    """随机报听写并判分。"""
    if not words:
        print("单词库为空,请先添加单词。\n")
        return
    raw = input(f"本次听写几个单词?(1-{len(words)}, 回车默认全部): ").strip()
    if raw:
        if not raw.isdigit() or not (1 <= int(raw) <= len(words)):
            print("数量无效。\n")
            return
        count = int(raw)
    else:
        count = len(words)

    quiz = random.sample(words, count)  # 不重复随机抽取
    print("\n=== 听写开始 ===")
    print("提示: 输入 'r' 重听, 输入 'q' 提前结束。\n")

    correct = 0
    answered = 0
    for i, item in enumerate(quiz, 1):
        print(f"第 {i}/{count} 个单词,请仔细听...")
        speaker.say(item["word"])
        while True:
            ans = input("你的拼写: ").strip()
            if ans.lower() == "r":
                speaker.say(item["word"])  # 重听
                continue
            if ans.lower() == "q":
                print("\n提前结束听写。")
                _show_score(correct, answered)
                return
            break
        answered += 1
        if ans.lower() == item["word"].lower():
            correct += 1
            print("✓ 正确!\n")
        else:
            meaning = f"  释义: {item['meaning']}" if item["meaning"] else ""
            print(f"✗ 错误。正确答案: {item['word']}{meaning}\n")

    print("=== 听写结束 ===")
    _show_score(correct, answered)


def _show_score(correct, answered):
    """显示成绩。"""
    if answered == 0:
        print("未作答任何单词。\n")
        return
    rate = correct / answered * 100
    print(f"得分: {correct}/{answered}  正确率: {rate:.1f}%\n")


def main():
    print("=" * 40)
    print("       英语单词听写软件")
    print("=" * 40)
    speaker = Speaker()
    words = load_words()

    menu = """请选择操作:
  1. 添加单词
  2. 查看全部单词
  3. 朗读单词
  4. 随机听写测试
  5. 删除单词
  0. 退出
请输入选项: """

    while True:
        choice = input(menu).strip()
        if choice == "1":
            add_word(words, speaker)
        elif choice == "2":
            list_words(words)
        elif choice == "3":
            read_word(words, speaker)
        elif choice == "4":
            dictation(words, speaker)
        elif choice == "5":
            delete_word(words)
        elif choice == "0":
            print("再见!")
            break
        else:
            print("无效选项,请重新输入。\n")


if __name__ == "__main__":
    main()
