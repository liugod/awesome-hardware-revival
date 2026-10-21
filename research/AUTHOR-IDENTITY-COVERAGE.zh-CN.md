# 项目账号与作者社交链接覆盖审计

日期：2026-10-21  
版本：1.8.0

## 结论

- 53 个正式目录条目现在都显示源码仓库所有者账号，作为项目来源追溯入口。
- 仓库所有者不自动等于唯一作者；页面明确写出这一边界。
- 4 个项目另有能从项目原帖、仓库或作者主页确认归属的个人作者社交账号：Onju Voice、Onju v2、ESPHome、HP Laser macOS driver。
- E0 社区线索仍以带说明的原始来源为主；没有明确归属证据时不猜测作者的 X/Twitter 账号。
- 原 Squeezelite 页面误放了 `squeezelite-esp32` 另一项目线的维护者资料，现已移除。

## 可核验数据

完整逐条清单由构建过程生成到 [`docs/data/author-identity-coverage.json`](../docs/data/author-identity-coverage.json)，每条包含：

- `project_id` 与项目名；
- 仓库所有者账号、平台和链接；
- 已核实个人作者账号、归属证据链接、核查方法和日期；
- 当前覆盖状态；
- 不把仓库归属解释为唯一作者的限定说明。

## 收录规则

1. GitHub 或 Codeberg 仓库 URL 可以确定仓库所有者页面，因此可作为项目身份追溯入口。
2. 个人 X/Twitter、博客或其他社交主页必须有项目原帖、项目仓库或作者主页提供的归属证据。
3. 同名、相似头像、搜索摘要和 GitHub 用户名相同都不足以单独确认外部社交账号。
4. 相邻项目、移植版和分支的作者不能自动挂到原项目页面。
5. 账号链接只说明身份和信息入口，不把作者陈述升级为 KitAgain 独立实测。

## 下一轮内容工作

优先核查用户最可能继续追踪的项目：XiaoGPT、Open-XiaoAI、Valetudo、wire-pod、KOReader、OpenIPC、Frigate、Rockbox、Gadgetbridge 和 Bazzite。只有找到一手归属链时才增加个人社交账号；否则保留仓库所有者入口和 `repository-owner-only` 状态。
