<p align="center">
翻译 <br>
<a href=https://github.com/GMDSantana/crivo/tree/master/CONTRIBUTING.md>🇬🇧 EN</a>
<a href=https://github.com/GMDSantana/crivo/tree/master/translations/es/CONTRIBUTING.md>🇪🇸 ES</a>
<a href=https://github.com/GMDSantana/crivo/tree/master/translations/pt-br/CONTRIBUTING.md>🇧🇷 PT-BR</a>
<a href=https://github.com/GMDSantana/crivo/tree/master/translations/zh-cn/CONTRIBUTING.md>🇨🇳 ZH-CN</a>
 <br><br>
</p>

# 为 Crivo 做出贡献

你好！👋

你对为 Crivo 做出贡献感兴趣吗？🤔 这是一个好消息！

无论你是经验丰富的开发者，还是刚刚起步，你的贡献都非常受欢迎。你可能会想，“我的编程技能足够好吗？” 答案是：绝对可以！每个人都有自己独特的价值，我们很乐意与你合作，无论你的经验水平如何。如果你正在阅读这份文档，那你已经比很多人更进一步了——新手通常不会学着去为 GitHub 项目做贡献呢！😉

以下是一些你可以为 Crivo 做出贡献的方式：

- 添加新的过滤功能或增强功能 🛠️
- 改进网络爬虫功能 🌐
- 创建或改进文档（我们将对此感激不尽！） 📖
- 修复通过 GitHub issues 报告的错误 🐛
- 重构代码库，使其更简洁或更高效 ✨

听起来很复杂？别担心！这份文档会一步步引导你完成整个过程。你的贡献不仅会改善 Crivo，还会让你的名字出现在贡献者名单中——我们会永远感激你！🙏

我们在 GitHub 上创建了一个讨论页面，你可以在那里与维护人员交流、提出问题或建议新功能。或者，你也可以直接在 GitHub 仓库中提交一个 issue。

---

## 如何贡献

有很多方法可以让 Crivo 变得更好！以下是一些我们特别希望得到帮助的领域。

### 1. 添加新功能 🛠️

Crivo 因其多功能性而脱颖而出。如果你有一个新功能的想法，例如额外的范围过滤器、更强大的解析逻辑或新的输出格式，欢迎你实施它！

要开始：
- Fork 这个仓库。
- 创建一个功能分支：
  ```bash
  git checkout -b feature/your-feature-name
  ```
- 实现你的功能。
- 为你的功能添加测试（见下文）。
- 提交一个 Pull Request 以供审核。

---

### 2. 改进网络爬虫功能 🌐

Crivo 的网络爬虫功能是项目的重要组成部分。如果你有网络爬虫的经验，或者发现可以改进的地方，你的贡献将非常宝贵。例如：

- 改进相对链接的解析方式。
- 添加对边缘情况的处理，例如 HTML 格式错误或不常见的 URL 结构。

---

### 3. 创建或改进文档 📖

文档是每个成功项目的基石。优秀的文档能确保其他人能够高效地使用和为 Crivo 做出贡献。

你可以通过以下方式帮助改进文档：

- 为代码库添加 docstring。
- 改进现有的文档（例如 README.md 或本文件）。
- 将文档翻译成其他语言。
- 撰写教程或使用指南。

优秀的文档与代码贡献同样重要，我们将非常感激你的帮助！

---

### 4. 修复错误 🐛

我们在 GitHub Issues 页面上记录了已知问题。如果你喜欢挑战，可以：

- 选择一个感兴趣的错误。
- 在 issue 中评论，让我们知道你正在解决它。
- 提交你的修复作为一个 Pull Request。

修复错误是熟悉代码库并快速做出有意义贡献的绝佳方式。

---

### 5. 重构代码库 ✨

Crivo 的代码库并非完美，总有改进的空间。如果你发现以下优化机会：

- 删除重复代码。
- 使代码更模块化或更易读。
- 确保代码遵循 Python 的 PEP8 标准。

欢迎你投入其中！你的重构将使 Crivo 对所有人来说更易维护。

---

## 编写测试

在添加新功能或修复错误时，我们建议你编写测试以确保一切按预期工作。Crivo 使用 `pytest` 进行测试。

### 如何编写测试

1. 转到仓库中的 `tests/` 目录。
2. 创建一个新的测试文件（例如 `test_new_feature.py`），或者将你的测试添加到现有文件中。
3. 按照命名约定 `test_<feature_or_bug>()` 编写你的测试函数。

### 运行测试

要运行测试，在终端中使用 pytest 命令：

```bash
pytest
```

这将执行 `tests/` 目录中的所有测试，并显示结果。

---

## 提交你的贡献

1. 完成修改后，将其推送到你的 fork：
   ```bash
   git push origin feature/your-feature-name
   ```
2. 在主仓库中创建一个 Pull Request。

我们会审核你的贡献，必要时提供反馈，并在准备就绪后合并它。🎉

---

## 感谢！🙏

为开源项目做出贡献是一种非常有价值的体验，我们很高兴你选择为 Crivo 做出贡献。你的努力、时间和专业知识对我们来说意义重大。我们迫不及待地想看到你为 Crivo 带来的精彩内容！

祝编程愉快！💻  
