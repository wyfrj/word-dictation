[app]
# 应用显示名
title = 单词听写
package.name = worddictation
package.domain = org.example

source.dir = .
source.include_exts = py,png,jpg,kv,atlas,ttf,json

version = 1.0

# 依赖: kivy 界面, plyer 调系统 TTS, pyjnius 供 plyer 安卓后端使用
requirements = python3,kivy,plyer,pyjnius

orientation = portrait
fullscreen = 0

# 系统 TTS 不需要特殊权限; 如需联网/读写存储可在此添加
android.permissions =

# 目标/最低 API 与架构
android.api = 33
android.minapi = 21
android.archs = arm64-v8a, armeabi-v7a

# 允许备份
android.allow_backup = 1

# 允许以 root 身份运行(用于 CI 环境)
allow_root = 1

[buildozer]
log_level = 2
warn_on_root = 1
