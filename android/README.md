# 安卓版英语单词听写软件

## 📱 项目结构
```
android/
  main.py          # Kivy 主程序(已修复 Windows 编码问题)
  buildozer.spec   # Buildozer 打包配置
  README.md        # 使用说明
.github/workflows/
  build-apk.yml    # GitHub Actions 自动构建配置
```

## ✅ 已完成功能
- [x] Kivy 现代化 UI 界面
- [x] 添加/删除单词(支持中文释义)
- [x] 单词列表展示(滚动视图)
- [x] 系统 TTS 朗读单词(plyer)
- [x] 随机听写测试
- [x] 自动判分与正确率统计
- [x] Windows 编码修复(支持中文输入/存储)
- [x] GitHub Actions 自动构建配置

## 🚀 使用方法

### 1. 本地桌面预览(Windows/Linux)
```bash
cd android
pip install kivy plyer
python main.py
```

### 2. GitHub Actions 云构建 APK

#### 第一步: 创建 GitHub 仓库
1. 在 GitHub 上创建新仓库
2. 将本项目推送到 GitHub

#### 第二步: 触发自动构建
- 推送到 `main` 或 `master` 分支会自动触发
- 或在 GitHub Actions 页面手动点击 "Run workflow"

#### 第三步: 下载 APK
1. 进入 GitHub 仓库的 Actions 标签页
2. 点击最新的 workflow run
3. 在 Artifacts 部分下载 `word-dictation-apk`

## 📋 buildozer.spec 配置说明
- `title`: 应用显示名
- `package.name`: 包名
- `requirements`: 依赖库(kivy, plyer, pyjnius)
- `android.permissions`: 权限列表(当前无需特殊权限)
- `android.api`: 目标 API 级别(33)
- `android.minapi`: 最低 API 级别(21)
- `android.archs`: 支持的架构(arm64-v8a, armeabi-v7a)

## ⚠️ 注意事项
1. **首次构建耗时**: 需要下载 Android SDK/NDK,约 2-3GB,首次构建可能需要 10-30 分钟
2. **TTS 引擎**: 安卓手机需安装英文 TTS 引擎(一般系统自带)
3. **构建环境**: GitHub Actions 使用 Ubuntu,自动安装所有依赖
4. **调试**: APK 为 debug 版本,如需发布请修改 buildozer.spec

## 🔧 技术栈
| 组件 | 用途 |
|------|------|
| Kivy | 跨平台 UI 框架 |
| plyer | 调用系统 TTS |
| pyjnius | plyer 的安卓后端 |
| Buildozer | 打包 APK |
| GitHub Actions | 云构建 |

## 📝 文件说明
- `main.py`: 主程序,包含 UI 和业务逻辑
- `buildozer.spec`: Buildozer 配置文件
- `build-apk.yml`: GitHub Actions 工作流配置
- `README.md`: 本说明文档
