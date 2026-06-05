# Changelog

## 2026-06-05 — Vue速成前端教程 系列完成
- 新增教程系列：`Vue速成前端教程/`（29篇 + README导航）
- 技术栈：Vue 3（Composition API + `<script setup>`）/ Vite / Vue Router 4 / Pinia
- 贯穿项目：博客前端（与后端教程的博客 API 对接）
- 六阶段：导读 → 三件套速通 → Vue 3 入门 → 博客实战 → 进阶 → 部署上线 → 结业
- 第 28 章同时给出三种后端对接方案：Python FastAPI / Java Spring Boot / Go Gin
- 教程大纲：`.project/docs/tutorials/vue3_frontend_outline.md`
- 细纲：`.project/docs/tutorials/vue3_frontend_detailed_outline.md`
- 4个可视化HTML待制作（路由原理、API链路、组件结构、响应式原理）

## 2026-06-05 — Python速成后端教程 系列完成
- 新增教程系列：`Python速成后端教程/`（30篇 + README导航 + glossary）
- 技术栈：Python 3.11+ / FastAPI / SQLAlchemy / SQLite → PostgreSQL / JWT / Docker
- 贯穿项目：简易博客系统（用户+文章+评论）
- 九阶段：导读 → 上路准备 → 数据来去 → 数据库 → 用户系统 → 评论关联 → 进阶功能 → 测试 → 部署上线 → 结业
- 教程大纲：`.project/docs/tutorials/python_fastapi_backend_outline.md`
- 细纲：`.project/docs/tutorials/python_fastapi_backend_detailed_outline.md`
- 4个可视化HTML待制作（HTTP链路、ER图、JWT流程、Docker架构）
- 全局术语索引：教程目录内 `glossary.md`

## 2026-05-28 (第三次修订 — 去 tian-nu 化)
- 全面移除 `tian-nu/test` 的所有引用（原87处，现0处）
- 教程改为完全通用：读者在02章真正创建自己的仓库
- 重写02章：从"浏览创建页面但不创建"改为"真正创建一个属于自己的仓库 my-first-project"
- 重写03章：推送目标改为读者自己创建的仓库
- 修订04-08章+HTML：全部替换为通用占位符
- 06章Fork：改为推荐 `octocat/Spoon-Knife`（GitHub官方练习仓库）

## 2026-05-28 (第二次修订 — 小白级自检)
- 全面自检：逐章通读9个文件（~5,400行），以小白视角排查问题
- 修复4处：00章措辞、GitHub首页描述、02章仓库不一致、03章终端打开方式不一致

## 2026-05-28 (初版)
- 初始化 .project/ 管理体系
- 完成 Git到GitHub 教程全流程
- 小白级重写：新增第0章电脑基础，全部8章推倒重写