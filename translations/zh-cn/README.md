<p align="center">
翻译 <br>
<a href=https://github.com/GMDSantana/crivo/tree/master/README.md>🇬🇧 EN</a>
<a href=https://github.com/GMDSantana/crivo/tree/master/translations/es/README.md>🇪🇸 ES</a>
<a href=https://github.com/GMDSantana/crivo/tree/master/translations/pt-br/README.md>🇧🇷 PT-BR</a>
<a href=https://github.com/GMDSantana/crivo/tree/master/translations/zh-cn/README.md>🇨🇳 ZH-CN</a>
 <br><br>
</p>

# Crivo

Crivo 是一个基于 Python 的开源工具，专为攻击性安全分析师、渗透测试人员和漏洞奖励计划参与者设计。它可以从文本或网页中提取和过滤 URL、IP 地址、域名和子域名，并内置了网页抓取功能。该工具支持多种过滤选项、范围控制和灵活的输出配置。

Crivo 特别适合用于快速任务和自动化。其简单明了的输出格式，没有多余的信息，非常适合集成到自动化工作流程中。此外，Crivo 还能高效处理并“过滤”来自其他工具的报告或输出，例如 [Amass](https://github.com/owasp-amass/amass)，提取所需的相关信息，并以干净、整齐的列表形式呈现。

## 功能

- 从文本或网页中提取 IPv4、IPv6、URL、域名和子域名。
- 支持以下输入来源：
  - 单个文本文件。
  - 包含网页列表的文件。
  - 单个网页。
- 支持灵活的范围过滤，提供对 IP、域名和 URL 的详细控制。
- 将结果直接显示在控制台或保存到指定的文件中，并保持列表中 URL 的顺序。
- 提供详细模式（verbose），在执行过程中显示更多信息。

## 安装

确保你的系统上安装了 Python 3.7 或更高版本。

```bash
# 克隆仓库：
git clone https://github.com/GMDSantana/crivo.git

# 进入项目目录：
cd crivo

# 安装必要的依赖项：
pip install -r requirements.txt
```

## 使用

通过命令行运行 Crivo：

```bash
# 从文本文件中提取和过滤：
python crivo_cli.py -f input.txt

# 从单个网页中获取并过滤：
python crivo_cli.py -w https://example.com

# 从网页列表中获取并过滤：
python crivo_cli.py -W webpage_list.txt

# 指定范围过滤器并保存到文件：
python crivo_cli.py -f input.txt -s example.com -o output.txt

# 启用详细模式以显示更多信息：
python crivo_cli.py -f input.txt -v
```

### 命令行参数

- `-f`, `--file`: 要过滤的输入文本文件的路径。
- `-w`, `--webpage`: 单个网页的 URL，用于获取和过滤。
- `-W`, `--webpage-list`: 包含网页 URL 列表的文本文件的路径，逐一获取并过滤。
- `-o`, `--output`: 过滤结果保存的输出文件路径。如果未指定，将结果打印到控制台。
- `-s`, `--scope`: 用逗号分隔的过滤范围序列（例如 `ips, urls, domains`）。默认情况下，如果未指定范围，将包含所有类型的数据。
- `--ip`: 仅过滤和显示 IP 地址（包括 IPv4 和 IPv6）。
- `--ipv4`: 仅过滤和显示 IPv4 地址。
- `--ipv6`: 仅过滤和显示 IPv6 地址。
- `--domain`: 仅过滤和显示域名和子域名。
- `--url`: 仅过滤和显示 URL。
- `-v`, `--verbose`: 启用详细模式，显示执行过程中的更多信息。
- `-V`, `--version`: 显示 Crivo 程序的版本。

## 贡献

欢迎贡献！开始之前，请阅读 [CONTRIBUTING.md](CONTRIBUTING.md) 文件，了解如何有效地贡献。当一切准备就绪后，请 fork 仓库，创建一个功能分支，并提交包含更改的 pull request。

## 许可证

Crivo 根据 [MIT 许可证](../LICENSE) 授权。

## Contributors

<!-- ALL-CONTRIBUTORS-LIST:START - Do not remove or modify this section -->
<!-- prettier-ignore-start -->
<!-- markdownlint-disable -->
<table>
  <tbody>
    <tr>
      <td align="center" valign="top" width="14.28%"><a href="https://gmdsantana.com/"><img src="https://avatars.githubusercontent.com/u/6341823?v=4?s=100" width="100px;" alt="GMDSantana"/><br /><sub><b>GMDSantana</b></sub></a><br /><a href="#code-GMDSantana" title="Code">💻</a> <a href="#design-GMDSantana" title="Design">🎨</a> <a href="#doc-GMDSantana" title="Documentation">📖</a> <a href="#test-GMDSantana" title="Tests">⚠️</a></td>
    </tr>
  </tbody>
</table>

<!-- markdownlint-restore -->
<!-- prettier-ignore-end -->

<!-- ALL-CONTRIBUTORS-LIST:END -->

此项目遵循 [all-contributors](https://allcontributors.org) 规范。  
欢迎任何形式的贡献！
