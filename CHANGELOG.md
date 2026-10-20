# Changelog

## 2.0.0

### Breaking changes

- 移除千帆 V1 推理服务（AK/SK + access_token）支持，仅保留千帆 V2 API。
- 移除 `wenxin_appid` 配置；V2 接口只需要 `wenxin_api_key`。
- `wenxin_sendpic` 默认值改为 `false`。
- 默认文本模型由 `ernie-4.0-turbo-8k` 改为 `ernie-4.5-turbo-128k`。

### Features

- 适配 NoneBot2 2.5+ 与 nonebot-plugin-alconna 0.62+。
- 使用千帆 V2 OpenAI 兼容接口：`/v2/chat/completions`、`/v2/images/generations`。
- 新增 `wenxin_image_model`、`wenxin_image_size`、`wenxin_system_prompt`、`wenxin_temperature`、`wenxin_max_tokens`、`wenxin_base_url`、`wenxin_proxy` 配置。
- 兼容 nonebot-plugin-htmlrender 新旧 Markdown 渲染 API；渲染不可用时自动回退为文本。
- 长回答自动分段发送。
- 默认超时时间调整为 120 秒，适配图片生成和思考模型。
- 更友好的 API 错误提示（401/403/404/429/超时/安全拦截）。
- 改用 PEP 621 + hatchling 打包，新增测试与 CI。
