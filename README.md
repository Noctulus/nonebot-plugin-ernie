<div align="center">
  <a href="https://v2.nonebot.dev/store"><img src="https://github.com/A-kirami/nonebot-plugin-template/blob/resources/nbp_logo.png" width="180" height="180" alt="NoneBotPluginLogo"></a>
  <br>
  <p><img src="https://github.com/A-kirami/nonebot-plugin-template/blob/resources/NoneBotPlugin.svg" width="240" alt="NoneBotPluginText"></p>
</div>

<div align="center">

# nonebot-plugin-ernie

_✨ 简单的文心一言 AI 对话插件 ✨_

<a href="./LICENSE">
    <img src="https://img.shields.io/github/license/Noctulus/nonebot-plugin-ernie.svg" alt="license">
</a>
<a href="https://pypi.python.org/pypi/nonebot-plugin-ernie">
    <img src="https://img.shields.io/pypi/v/nonebot-plugin-ernie.svg" alt="pypi">
</a>
<img src="https://img.shields.io/badge/python-3.9+-blue.svg" alt="python">

</div>

</div>

## 📖 介绍  

- 本插件使用千帆ModelBuilder的推理服务 API V2进行对话请求，使用前需根据[API调用指南](https://cloud.baidu.com/doc/WENXINWORKSHOP/s/Fllg87pck)创建一个千帆应用以获取API Key、AppID。  
- [支持的API列表](https://cloud.baidu.com/doc/WENXINWORKSHOP/s/em4tsqo3v)，默认为`ernie-4.0-turbo-8k`。

## 💿 安装

<del>
<details>
<summary>使用 nb-cli 安装（推荐）</summary>
在 nonebot2 项目的根目录下打开命令行, 输入以下指令即可安装

    nb plugin install nonebot-plugin-ernie

</details>
<details>
<summary>使用包管理器安装</summary>
在 nonebot2 项目的插件目录下, 打开命令行, 根据你使用的包管理器, 输入相应的安装命令

<details>
<summary>pip</summary>

    pip install nonebot-plugin-ernie
</details>
<details>
<summary>pdm</summary>

    pdm add nonebot-plugin-ernie
</details>
<details>
<summary>poetry</summary>

    poetry add nonebot-plugin-ernie
</details>
<details>
<summary>conda</summary>

    conda install nonebot-plugin-ernie
</details>

打开 nonebot2 项目根目录下的 `pyproject.toml` 文件, 在 `[tool.nonebot]` 部分追加写入

    plugins = ["nonebot_plugin_example"]

</details>
</del>

**以上安装方式尚未更新该分支内容。**
<details open>
<summary>手动安装（注意指定分支）</summary>
    
    git clone -b v2-test https://github.com/Noctulus/nonebot-plugin-ernie.git
下载完成后在bot项目的pyproject.toml文件手动添加插件：

    plugin_dirs = ["xxxxxx","xxxxxx",......,"下载完成的插件路径/nonebot-plugin-ernie"]
</details>

## ⚙️ 配置

在 nonebot2 项目的`.env`文件中添加下表中的必填配置

| 配置项 | 必填 | 默认值 | 说明 |
|:-----:|:----:|:----:|:----:|
| wenxin_api_key | 是 | 无 | 百度千帆ModelBuilder的API Key |
| wenxin_appid | 是 | 无 | V2版本应用ID |
| wenxin_model | 否 | ernie-4.0-turbo-8k | 百度智能云千帆模型 |
| wenxin_sendpic | 否 | False | 是否以图片形式发送 |
| wenxin_timeout | 否 | 60 | 调用API多久无反应视为超时 |

> Note: 若调用`Deepseek R1`等大型模型，60秒以上的响应时间都是有可能的，请适当增加`wenxin_timeout`，并坐和放宽

## 🎉 使用
### 指令表
| 指令 | 权限 | 需要@ | 范围 | 说明 |
|:-----:|:----:|:----:|:----:|:----:|
| 一言 | 全部 | 否 | 全部 | 使用文心一言 API 进行对话生成 |

### 效果图
![效果图](./preview.png)

- 如果配置了以图片形式发送（`wenxin_sendpic=True`），可以将Markdown形式的回答以更易读的方式呈现：
![Markdown效果图](./preview_md.png)