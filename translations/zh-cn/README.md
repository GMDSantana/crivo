<p align="center">
翻译 <br>
<a href="../../README.md">🇬🇧 EN</a>
<a href="../es/README.md">🇪🇸 ES</a>
<a href="../pt-br/README.md">🇧🇷 PT-BR</a>
<a href="../zh-cn/README.md">🇨🇳 ZH-CN</a>
 <br><br>
</p>

# Crivo

Crivo 是一个基于 Python 的开源工具，专为攻击性安全分析师、渗透测试人员和漏洞奖励计划参与者设计。它可以从文本或网页中提取和过滤 URL、IP 地址、域名和子域名，并内置了网页抓取功能。该工具支持多种过滤选项、范围控制和灵活的输出配置。

Crivo 特别适合用于快速任务和自动化。其简单明了的输出格式，没有多余的信息，非常适合集成到自动化工作流程中。此外，Crivo 还能高效处理并“过滤”来自其他工具的报告或输出，例如 [Amass](https://github.com/owasp-amass/amass)，提取所需的相关信息，并以干净、整齐的列表形式呈现。

## 功能

- 从文本或网页中提取 IPv4、IPv6（包括 `2001:db8::1` 这样的压缩形式）、URL、域名和子域名。
- 对提取结果进行校验：逐段检查 IP 地址，域名必须以真实存在的顶级域名（TLD）结尾（内置 TLD 列表，包括国际化顶级域名）。
- 支持以下输入来源：
  - 单个文本文件（任意编码；可容忍无效字节）。
  - 标准输入，便于在管道中使用（`cat report.txt | crivo`）。
  - 单个网页。
  - 包含网页列表的文件。
- 支持灵活的范围过滤：可按结果类型、按域名（包括子域名）、按 IP 或 CIDR 网段，或按关键字过滤。
- 可选的爬取（crawling）功能，支持深度控制：按指定深度跟踪链接，同时遵守范围限制（或停留在起始站点）和页面数量上限。
- 将结果直接显示在控制台或保存到指定的文件中，并保持列表中 URL 的顺序。
- 稳健的网页请求：超时控制、临时错误自动重试、大小限制、重定向处理以及正确的字符解码。
- 提供详细模式（verbose），在执行过程中显示更多信息。诊断信息输出到标准错误，因此不会干扰结果输出。

## 安装

确保你的系统上安装了 Python 3.10 或更高版本。

```bash
# 克隆仓库：
git clone https://github.com/GMDSantana/crivo.git

# 进入项目目录：
cd crivo

# 将 Crivo 及其依赖安装到虚拟环境（.venv）中：
scripts/install_dependencies.sh
source .venv/bin/activate
```

也可以使用 pip 安装，这样还会提供 `crivo` 命令：

```bash
pip install .
```

## 使用

通过命令行运行 Crivo（`crivo`、`python -m crivo` 或 `python crivo.py`）：

```bash
# 从文本文件中提取和过滤：
crivo -f input.txt

# 从标准输入读取：
cat amass_output.txt | crivo --domain

# 从单个网页中获取并过滤（未指定协议时默认使用 https://）：
crivo -w https://example.com

# 同时提取 href/src/action 属性中的链接，并解析相对链接：
crivo -w https://example.com -r --url

# 从网页列表中获取并过滤：
crivo -W webpage_list.txt

# 爬取两层深度，只停留在 example.com 及其子域名上：
crivo -w https://example.com -c 2

# 获取报告中范围内的 URL，并同时从这些页面中提取域名：
crivo -f report.txt -c 1 -s example.com --domain

# 指定范围过滤器并保存到文件：
crivo -f input.txt -s example.com -o output.txt

# 只保留某个网段内的 IP，以及只保留 example.com 或其子域名上的 URL：
crivo -f input.txt -s ips,10.0.0.0/8
crivo -f input.txt -s urls,*.example.com

# 启用详细模式以显示更多信息：
crivo -f input.txt -v
```

### 命令行参数

- `-f`, `--file`: 要过滤的输入文本文件的路径（`-` 表示读取标准输入）。
- `-w`, `--webpage`: 单个网页的 URL，用于获取和过滤。
- `-W`, `--webpage-list`: 包含网页 URL 列表的文本文件的路径，每行一个，逐一获取并过滤。空行、以 `#` 开头的行以及重复的 URL 会被跳过。每个 URL 会在其结果之前输出。
- `-o`, `--output`: 过滤结果保存的输出文件路径。如果未指定，将结果打印到控制台。
- `-s`, `--scope`: 用逗号分隔的范围过滤器（见下文）。默认情况下，如果未指定范围，将包含所有类型的数据。
- `--ip`: 仅过滤和显示 IP 地址（包括 IPv4 和 IPv6）。
- `--ipv4`: 仅过滤和显示 IPv4 地址。
- `--ipv6`: 仅过滤和显示 IPv6 地址。
- `--domain`: 仅过滤和显示域名和子域名。
- `--url`: 仅过滤和显示 URL。
- `-r`, `--resolve-links`: 对于网页，同时提取 `href`、`src` 和 `action` 属性中的链接，并根据页面 URL 解析相对链接。
- `-t`, `--timeout`: HTTP 请求超时时间，单位为秒（默认：15）。
- `-k`, `--insecure`: 不验证 TLS 证书（适用于使用自签名证书的测试环境）。
- `-c`, `--crawl DEPTH`: 爬取深度（默认：`0`，不爬取）。详见下文“爬取”一节。
- `--max-pages N`: 每次爬取最多获取的页面数量（默认：`100`）。
- `-v`, `--verbose`: 启用详细模式，显示执行过程中的更多信息（输出到标准错误）。
- `-V`, `--version`: 显示 Crivo 程序的版本。

`-f`、`-w` 和 `-W` 不能同时使用。如果三者都未指定，Crivo 会读取标准输入。

### 范围过滤器

`-s`/`--scope` 中的每一项可以是以下之一：

| 项 | 含义 |
| --- | --- |
| `ips`、`ipv4`、`ipv6`、`urls`、`domains`、`subdomains` | 选择结果类型，作用与 `--ip`、`--ipv4`、`--ipv6`、`--url` 和 `--domain` 选项相同。`domains` 与 `subdomains` 等价。 |
| `example.com`、`*.example.com`、`https://example.com/` | 保留主机为 `example.com` 或其子域名的域名和 URL。`notexample.com` 或 `example.com.evil.net` 这类相似域名会被排除。 |
| `10.0.0.5`、`10.0.0.0/8`、`2001:db8::/32` | 保留位于该地址或网段内的 IP，以及主机为此类 IP 的 URL。 |
| 其他任何值，例如 `admin` 或 `192.168.` | 不区分大小写的关键字，可出现在结果的任意位置。 |

类型关键字和目标可以组合使用：`-s urls,example.com` 只保留 `example.com` 及其子域名上的 URL。

### 爬取

使用 `-c`/`--crawl` 时，Crivo 按广度优先的方式跟踪链接，并从获取的每个页面中提取结果：

- 深度 `0`（默认）：不爬取。Crivo 的行为与不使用 `-c` 时完全相同。
- 深度 `1`：Crivo 还会获取初始输入中找到的 URL：即 `-w` 指定页面（或 `-W` 列表中每个页面）上的链接，或文件、标准输入中找到的 URL。
- 深度 `2` 及以上：Crivo 还会继续跟踪这些页面上的链接，直到达到指定深度。

爬取如何保持可控：

- **每一层都会执行范围限制，包括重定向。** 指定范围目标时（例如 `-s example.com` 或 `-s 10.0.0.0/8`），只会获取匹配的 URL，并且不会跟随指向范围外 URL 的重定向。`urls` 这类类型关键字不会限制爬取。
- **未指定范围目标时，Crivo 只停留在起始站点上**：即起始主机（忽略开头的 `www.`）及其子域名。对于文件或标准输入，输入中的所有 URL 都会在深度 1 被获取，这些 URL 的主机决定了更深层级的站点范围。
- **每次爬取最多获取 `--max-pages` 个页面**（默认：100）；使用 `-W` 时，按列表中的每个页面分别计算。系统会发出警告，说明有多少范围内的 URL 未被访问。
- 每个页面只获取一次。不会获取指向图片、字体、样式表、音视频、文档和压缩包的链接，非文本响应也会被跳过；但如果这些 URL 出现在页面中，仍会作为结果输出。
- 爬取过程中获取失败的页面（例如返回 404）会以警告形式报告，不会改变退出码；只有起始页面失败才会改变退出码。
- 所有页面的结果会合并为一个排序后的列表（使用 `-W` 时，每个列表页面各对应一个列表）。

### 退出码

| 退出码 | 含义 |
| --- | --- |
| `0` | 成功（包括未找到任何结果的情况）。 |
| `1` | 发生错误，例如输入文件不存在或网页无法获取。使用 `-W` 时，其余页面仍会继续处理。 |
| `2` | 命令行参数无效。 |
| `130` | 被 Ctrl+C 中断。 |

## 运行测试

```bash
pip install -r requirements-dev.txt
pytest --cov=crivo
```

网页抓取相关的测试使用本地 HTTP 服务器，因此无需访问互联网。

## 贡献

欢迎贡献！开始之前，请阅读 [CONTRIBUTING.md](CONTRIBUTING.md) 文件，了解如何有效地贡献。当一切准备就绪后，请 fork 仓库，创建一个功能分支，并提交包含更改的 pull request。

## 许可证

Crivo 根据 [MIT 许可证](../../LICENSE) 授权。

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
