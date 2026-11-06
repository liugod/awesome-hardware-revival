# TRA-35 验收清单（布林 · SEO only）

票：[TRA-35](https://linear.app/tradlink/issue/TRA-35)  
工程主责：比尔盖茨（Orca→Codex）｜合/Pages：总书记｜本清单：布林只验收、不写码  
参照模板：公网 `/en/guides/speaker-voice/`（title/meta/H1/项目列表结构）  
Slogan 锁定：中文「二手硬件再就业指南」（TRA-21；未经领导明示不得改）

## 0. Interactive Planning（对照）

1. **混乱**：三枢纽公网仍 404；首页 Find-by-device 无 tv-box/router/smart-plug；流量散落 atlas。
2. **理想**：中英各 3 枢纽可索引；首页直链；枢纽↔代表项目双向；slogan 未动。
3. **手段**：等 TRA-34 合完 → 比尔盖茨串行出 PR → 布林按本清单公网抽查 → 报总书记批合/Pages。
4. **资源**：仓 `liugod/awesome-hardware-revival`；GSC 基线 raw `2026-11-05`（窗 10-28..11-03）；禁手写、禁串工程。
5. **控制**：PR+CI；上线 48h 内 curl 6 URL + 首页；坏链/孤岛不得因本票上升。

## 1. 现网基线（验收前，2026-11-07 02:40 Asia/Shanghai 再核）

| URL | 期望上线后 | 现况 |
|-----|------------|------|
| `/en/guides/tv-box/` `/zh/guides/tv-box/` | 200 | **404** |
| `/en/guides/router/` `/zh/guides/router/` | 200 | **404** |
| `/en/guides/smart-plug/` `/zh/guides/smart-plug/` | 200 | **404** |
| 中文首页 slogan | 含「二手硬件再就业指南」 | 已有（勿改） |
| 首页 guides 入口 | 含上述三枢纽 | 现仅 ai-retrofit / nest-mini / speaker-voice / kindle-displays / home-computers |

### GSC 基线（勿重拉亦可对照；窗 cur 10-28..11-03）

枢纽目标承接页（现无枢纽 URL，流量在 lead/project）：

- TV：`atlas-ophub-hk1-box` 1/19；`atlas-ophub-tanix-tx5-max` 1/13；`rootmytv` 1/35（CTR 2.9%）；查询 `coreelec` 0/14@20.5；`canirootmytv` 0/2
- Router：`atlas-enshi-xiaomi-ax9000` 1/15；多条 `atlas-enshi-xiaomi-*` 薄页占前 50；查询 `ax9000 openwrt` 0/1
- Smart-plug：`atlas-esphome-sonoff-s31` 1/6（en）+ zh 1/1；OpenBeken 回收意图（不重开诊断）
- 参照枢纽：`/en/guides/speaker-voice/` 1/11@5.7

验收后盯：三枢纽 URL 是否进入 GSC 页面报告；上述 lead/project 点击是否掉崖（不应因枢纽上线而断链）。

## 2. Title / Meta（每页必过）

对 6 个枢纽 URL 各查 `<title>` + `meta name=description`：

**结构（对齐 speaker-voice）**

- EN title：用户意图句 + `· KitAgain`（动作/设备清晰，非堆砌关键词）
- ZH title：用户意图句 + `· 二手硬件再就业指南 · KitAgain`（slogan 必须出现在 ZH title 或与首页一致的品牌位）
- Meta：1–2 句决策视角（先判断再动手），降认知负荷；中英各自完整，非机翻空壳
- H1 与 title 语义一致，页面唯一 H1
- 无重复 title；无空 description；无「测试/TODO/lorem」

**建议意图锚（工程可微调措辞，验收看意图是否落地）**

| 枢纽 | EN 意图 | ZH 意图 |
|------|---------|---------|
| tv-box | TV box → Armbian/CoreELEC/刷机或服务器用途怎么选 | 电视盒还能刷机/当小主机吗 |
| router | 旧路由刷 OpenWrt 前如何核对型号与退路 | 旧路由器能不能上 OpenWrt |
| smart-plug | 智能插座本地化：Tasmota/ESPHome/OpenBeken 怎么选 | 智能插座去云：刷机路线怎么选 |

## 3. 页面结构 / 内链

每页（中英）：

- [ ] HTTP 200（非 GitHub Pages 404 壳）
- [ ] 面包屑可见 + `BreadcrumbList` JSON-LD（可与 TRA-29 模板一致）
- [ ] 项目/lead 列表 ≥6（该类已审）；锚文本用「设备名+动作」，禁裸 URL
- [ ] hreflang / 中英互指正常
- [ ] **双向链抽查**（任一侧缺即不合格）：
  - tv-box ↔ `rootmytv` **或** `hk1-box`（lead/project 实际 URL）
  - router ↔ 任一 Xiaomi atlas（如 ax9000）
  - smart-plug ↔ `openbeken` **或** `sonoff-s31`
- [ ] 相关块/列表无死链；本票不得抬高孤岛页/坏链数（对照 TRA-33 CI）

## 4. 首页入口

- [ ] EN 与 ZH 首页「按设备找 / Find by device」均直链三枢纽（相对或绝对均可，点击可达）
- [ ] 入口文案可读（设备类名），不破坏现有 nest-mini / speaker-voice 等入口
- [ ] 中文首页仍含 slogan「二手硬件再就业指南」；EN 品牌句未擅自改成另一套中文 slogan

## 5. Sitemap / 索引就绪

- [ ] `sitemap.xml`（或站点实际 sitemap 源）含上述 6 URL
- [ ] 6 URL 无 `noindex`；canonical 自指或语言规范正确
- [ ] 上线 48h 内：URL Inspection 可做抽查备忘（无 Indexing API 强推；有则记结果）

## 6. Slogan / 禁区（一票否决）

- [ ] 全站抽查首页 + 任一新枢纽 ZH：slogan 仍为「二手硬件再就业指南」
- [ ] 未改 trad.link；未改 `~/.codex/skills`；PR 无手写旁路痕迹（工程走 Codex）
- [ ] 未重开 OpenBeken 诊断、未批量 AI 薄文

## 7. CI / PR 审阅门禁（TRA-34 Done 后盯 TRA-35 PR）

- [ ] CI 绿
- [ ] Diff 范围限于 guides 三枢纽 + 首页入口 + sitemap（及必要模板数据）；无无关大爆炸
- [ ] 对照本清单勾选后，回执 commit SHA + 6 URL curl 码 + 双向链截记 → 报总书记批合/Pages
- [ ] **不**自行 merge、不抢 Pages、不改生产

## 8. 回执模板（布林 → 总书记）

```
TRA-35 SEO 验收：PASS/FAIL
PR：#N / commit：sha
6 URL：en/zh × tv-box,router,smart-plug → HTTP …
首页入口：EN/ZH 有无三链
双向链：tv-box↔…；router↔…；smart-plug↔…
slogan：未改 / 已改（否决）
sitemap：含 6 URL 是/否
GSC：基线窗 10-28..11-03；上线后下轮周报再比枢纽 URL
```

