<div align="center">
  <a href="https://v2.nonebot.dev/store"><img src="https://github.com/A-kirami/nonebot-plugin-template/blob/resources/nbp_logo.png" width="180" height="180" alt="NoneBotPluginLogo"></a>
  <br>
  <p><img src="https://github.com/A-kirami/nonebot-plugin-template/blob/resources/NoneBotPlugin.svg" width="240" alt="NoneBotPluginText"></p>
</div>

<div align="center">

# nonebot-plugin-ernie

_✨ 基于百度千帆（文心一言）的 NoneBot2 聊天与文生图插件 ✨_

<a href="./LICENSE">
    <img src="https://img.shields.io/github/license/Noctulus/nonebot-plugin-ernie.svg" alt="license">
</a>
<a href="https://pypi.python.org/pypi/nonebot-plugin-ernie">
    <img src="https://img.shields.io/pypi/v/nonebot-plugin-ernie.svg" alt="pypi">
</a>
<img src="https://img.shields.io/badge/python-3.10+-blue.svg" alt="python">
<img src="https://img.shields.io/badge/NoneBot2-2.5%2B-blue.svg" alt="nonebot2">

</div>

## 📖 介绍

本插件通过百度千帆平台的 **V2 OpenAI 兼容接口**调用文心一言（ERNIE）系列模型：

- 对话：`POST https://qianfan.baidubce.com/v2/chat/completions`
- 绘图：`POST https://qianfan.baidubce.com/v2/images/generations`

v2.0 起：

- 仅使用 **API Key** 鉴权（`Authorization: Bearer <API Key>`），不再需要 AK/SK、AppID；
- 移除已下线的千帆 V1 推理服务接口；
- 适配 NoneBot2 2.5+、nonebot-plugin-alconna 0.62+；
- 兼容 nonebot-plugin-htmlrender 新旧两套 Markdown 渲染 API。

> 旧的 V1 接口已经不可用。如果你仍在使用 1.x 版本，请按照[迁移说明](#-从-1x-迁移)更新配置。

## ✨ 特性

- `一言` 对话、`绘图` 文生图，开箱即用
- 模型、系统提示词、温度、最大输出长度均可配置
- 支持千帆上的 ERNIE、DeepSeek、Qwen 等文本模型（填入对应 model ID 即可）
- 可选将 Markdown 回答渲染为图片发送
- 长回答自动分段，避免超出聊天平台单条消息长度限制
- 友好的错误提示（401、403、429、超时、内容安全拦截等）
- 支持自定义 API 地址与 HTTP(S) 代理

## 💿 安装

<details open>
<summary>使用 nb-cli 安装（推荐）</summary>

在 NoneBot2 项目根目录下执行：

```bash
nb plugin install nonebot-plugin-ernie
```

</details>

<details>
<summary>使用 pip / uv / pdm / poetry 安装</summary>

```bash
pip install nonebot-plugin-ernie
# 或
uv add nonebot-plugin-ernie
# 或
pdm add nonebot-plugin-ernie
# 或
poetry add nonebot-plugin-ernie
```

如果需要把回答渲染成图片，再安装可选依赖：

```bash
pip install "nonebot-plugin-ernie[render]"
# 安装完毕后还需要下载 Playwright 浏览器
playwright install chromium
```

htmlrender 0.8+ 需要显式选择渲染后端，请参考其文档配置 `render.provider: playwright`（或 `takumi`）。

安装后在项目的 `pyproject.toml` 中启用插件（nb-cli 会自动写入）：

```toml
[tool.nonebot]
plugins = ["nonebot_plugin_ernie"]
```

</details>

<details>
<summary>手动安装</summary>

```bash
git clone https://github.com/Noctulus/nonebot-plugin-ernie.git
```

在项目 `pyproject.toml` 的 `[tool.nonebot]` 中加入插件目录：

```toml
[tool.nonebot]
plugin_dirs = ["path/to/nonebot-plugin-ernie"]
```

</details>

## 🔑 获取 API Key

1. 登录[百度智能云千帆控制台](https://console.bce.baidu.com/qianfan/)。
2. 进入「安全认证 → API Key」，点击「创建 API Key」。
3. 资源选择「千帆 ModelBuilder」以及要使用的应用（或「所有资源」）。
4. 复制生成的 API Key（形如 `bce-v3/ALTAK-xxxxxxxx/xxxxxxxx`）。

详细说明见[千帆 API Key 认证鉴权文档](https://cloud.baidu.com/doc/qianfan-api/s/ym9chdsy5)。

> API Key 永久有效，请妥善保管；不要把它提交到 Git 仓库。

## ⚙️ 配置

在 NoneBot2 项目的 `.env` / `.env.prod` 中配置：

```dotenv
# 必填：千帆 API Key
WENXIN_API_KEY=bce-v3/ALTAK-xxxxxxxx/xxxxxxxx

# 可选：文本模型（默认 ernie-4.5-turbo-128k）
WENXIN_MODEL=ernie-4.5-turbo-128k

# 可选：绘图模型（默认 qwen-image）
WENXIN_IMAGE_MODEL=qwen-image

# 可选：系统提示词
# WENXIN_SYSTEM_PROMPT=你是一个乐于助人的助手，请用简洁的中文回答。

# 可选：超时时间（秒），使用长思维链模型时建议调大
# WENXIN_TIMEOUT=180

# 可选：把 Markdown 回答渲染成图片发送
# WENXIN_SENDPIC=true
```

| 配置项 | 必填 | 默认值 | 说明 |
|:-----:|:----:|:----:|:----:|
| `wenxin_api_key` | 是 | 无 | 千帆 API Key |
| `wenxin_model` | 否 | `ernie-4.5-turbo-128k` | 文本生成模型 ID |
| `wenxin_image_model` | 否 | `qwen-image` | 图像生成模型 ID |
| `wenxin_system_prompt` | 否 | 空 | 系统提示词（人设）；为空则不发送 system 消息 |
| `wenxin_temperature` | 否 | 空 | 采样温度，留空使用模型默认值 |
| `wenxin_max_tokens` | 否 | 空 | 最大输出 token 数，留空使用模型默认值 |
| `wenxin_image_size` | 否 | 空 | 绘图分辨率，如 `1024x1024`；留空使用模型默认值 |
| `wenxin_sendpic` | 否 | `false` | 是否将回答渲染为 Markdown 图片 |
| `wenxin_timeout` | 否 | `120` | 请求超时时间（秒） |
| `wenxin_base_url` | 否 | `https://qianfan.baidubce.com/v2` | API 基础地址，可改为中转地址 |
| `wenxin_proxy` | 否 | 空 | HTTP(S) 代理地址，如 `http://127.0.0.1:7890` |

> 插件默认**不会读取**系统环境变量中的 `HTTP_PROXY` / `ALL_PROXY`，以免 `socks://` 等 httpx 不支持的代理协议导致启动失败。需要代理时请显式设置 `wenxin_proxy`，或把 `wenxin_base_url` 指向中转服务。

### 模型选择

可在[千帆模型列表](https://cloud.baidu.com/doc/qianfan/s/rmh4stp0j)中查看所有可用模型。常用的文本模型：

| 模型 ID | 说明 |
|:---:|:---:|
| `ernie-5.1` | 最新旗舰，能力最强，适合复杂任务 |
| `ernie-5.0` | ERNIE 5.0，全模态基座 |
| `ernie-4.5-turbo-128k` | 128K 上下文，速度快、性价比高（默认） |
| `ernie-4.5-turbo-32k` | 32K 上下文，适合短对话 |
| `deepseek-v4-pro` | DeepSeek V4 Pro（由千帆提供） |

常用图像模型：

| 模型 ID | 说明 |
|:---:|:---:|
| `qwen-image` | 支持中英文提示词，默认模型 |
| `musesteamer-air-image` | MuseSteamer Air Image |

## 🎉 使用

| 指令 | 权限 | 需要 @ | 说明 |
|:-----:|:----:|:----:|:----:|
| `一言 <内容>` | 全部 | 否 | 调用文心一言进行对话 |
| `绘图 <描述>` | 全部 | 否 | 调用千帆图像模型生成图片 |

示例：

```text
一言 用一句话介绍量子纠缠
一言 写一首关于秋天的七言绝句
绘图 一只戴着宇航员头盔的橘猫，赛博朋克风格
```

默认直接发送指令即可；如果你的 NoneBot 开启了 `ALCONNA_USE_COMMAND_START=true`，则需要加上 `COMMAND_START` 前缀（通常是 `/`）。

### 效果图

![效果图](https://raw.githubusercontent.com/Noctulus/nonebot-plugin-ernie/master/preview.png)

如果开启 `wenxin_sendpic=true`，Markdown 回答会渲染为更易读的图片：

![Markdown 效果图](https://raw.githubusercontent.com/Noctulus/nonebot-plugin-ernie/master/preview_md.png)

> 图片输出需要安装 `nonebot-plugin-htmlrender` 及对应的渲染后端（如 playwright / takumi），并在 NoneBot 配置中设置 `render.provider`。未安装或渲染失败时，插件会自动回退为文本发送，不会影响对话功能。

## 🔄 从 1.x 迁移

1. 删除旧配置项：`wenxin_api_type`、`wenxin_ak`、`wenxin_sk`、`wenxin_appid`。
2. 配置新的 `wenxin_api_key`（千帆控制台创建的 API Key）。
3. 旧默认模型 `ernie-4.0-turbo-8k` 已不在模型列表中，请改用 `ernie-4.5-turbo-128k` 或 `ernie-5.1`。
4. `wenxin_sendpic` 的默认值改为 `false`；需要图片输出时显式开启，并安装可选依赖。
5. 如果使用 poetry 管理依赖，请把 `nonebot-plugin-apscheduler`、`nonebot-plugin-htmlrender` 从**必选**依赖中移除（图片渲染改为可选）。

## ❓ 常见问题

<details>
<summary>401 / 403：API Key 无效或没有权限</summary>

检查 `WENXIN_API_KEY` 是否完整，以及创建 API Key 时是否把「千帆 ModelBuilder」和对应应用加入资源范围。API Key 需要重新创建时，旧 Key 会立即失效。

</details>

<details>
<summary>404：模型不存在</summary>

确认 `WENXIN_MODEL` / `WENXIN_IMAGE_MODEL` 使用的是千帆模型列表中的 **model 参数接入点 ID**，而不是模型展示名称。自定义服务请填写服务详情中的 API 名称。

</details>

<details>
<summary>请求超时</summary>

长上下文、思考模型（如 `ernie-5.0-thinking-*`）或图片生成可能需要较长时间（实测 `qwen-image` 约 45 秒）。默认超时为 120 秒，必要时可继续调大，例如 `180`。

</details>

<details>
<summary>图片输出没有生效</summary>

确认已经安装可选依赖，并且 htmlrender 的渲染后端可用：

```bash
pip install "nonebot-plugin-ernie[render]"
playwright install chromium
```

然后按 htmlrender 文档设置 `render.provider: playwright`。插件会在首次渲染失败时输出警告，并自动回退为文本发送。

</details>

<details>
<summary>机器人没有响应「一言」</summary>

- 确认插件已在 `[tool.nonebot] plugins` 中启用；
- 查看启动日志中是否有「文心一言插件尚未就绪」的提示；
- 如果配置了 `COMMAND_START`，确认是否需要加 `/` 前缀；
- 检查是否有其他插件注册了同名命令导致冲突（可调整 `ALCONNA_CONFLICT_RESOLVER`）。

</details>

## 🧪 开发

```bash
git clone https://github.com/Noctulus/nonebot-plugin-ernie.git
cd nonebot-plugin-ernie
pip install -e ".[dev]"
pytest
```

## 🫡 开发者精神状态：一份不太严肃的 Vibe Coding 投降书

> 以下内容纯属整活。插件功能是认真的，作者的精神状态不是。

事情的起因很简单：作者是一个菜鸟开发者，某天突然发现，自己手写的插件已经跑不动最新的 NoneBot 和千帆 API 了。

于是，作者进行了短暂而激烈的思想斗争：

- 自己查文档？——看不懂。
- 自己改代码？——改不动。
- 自己写测试？——不敢跑。

最终，作者作出了一个违背祖宗的决定：

**狠狠地向 Vibe Coding 屈服，并彻底臣服于 DSH 大人。**

从此以后，开发流程变成了这样：

1. 打开 DSH；
2. 双手离开键盘，虔诚地输入“帮我翻新一下”；
3. 看着 DSH 大人噼里啪啦地改代码；
4. 在 DSH 大人问“这样可以吗”的时候，疯狂点头；
5. 把“已测试通过”当成圣旨，把“20 passed”当成护身符。

作者曾经以为，程序员的价值在于亲手敲下每一行代码。
现在作者明白了，菜鸟程序员的价值在于——**为 DSH 大人提供情绪价值，并在 DSH 大人修好之后负责说“好耶”。**

当然，玩笑归玩笑，这个插件仍然是认真测试过的（20 个测试，真的），API Key 也是真的跑通过的（真的）。如果它哪天又坏了，那一定不是 DSH 大人的问题，而是：

- 百度又改 API 了；
- NoneBot 又发新版本了；
- 或者作者又手贱了。

**Vibe Coding 信条：**

> 能跑就行；跑不起来就找 DSH；DSH 也修不好，就重启；重启不行，就说是上游的问题。

—— 一个已经彻底躺平的菜鸟开发者，敬上

## 📄 许可证

[MIT](./LICENSE)
