# Git到GitHub 教程 — 大纲

- 对应文档版本：requirements.md N/A, detailed_design.md N/A（独立教程，无上游设计文档）
- 适用环境：Windows/macOS/Linux，Git 2.30+，浏览器
- 读者角色：已掌握Git基本操作（init/add/commit/branch）的开发者
- 预计耗时：新手约3小时，熟手约1.5小时
- 前置教程：Git基础（或已读完 GO从零到后端教程 第101章）
- 可视化：有，pr_fork_visual.html（Fork+PR协作流程动画）
- 质量等级：P1 标准
- 测试仓库：https://github.com/tian-nu/test

## 教什么
从零开始：GitHub账号→SSH→创建仓库→推送→PR协作→Issue→Actions CI→Pages，完整走通"本地代码→云端协作"全链路。

## 不教什么
Git本地深入操作（add/commit/branch/merge/rebase原理）——这是纯Git教程的事。本教程只讲"从Git到GitHub这一段"。

## 学完能做什么
将自己的项目发布到GitHub、发起和审查Pull Request、用Actions自动测试、用Pages部署网站。

## 步骤
1. 环境准备：Git安装验证 + GitHub注册 + SSH密钥配置
2. 创建你的第一个GitHub仓库
3. 本地项目推送上线（目标：https://github.com/tian-nu/test）
4. Pull Request 完整流程
5. Issue 追踪与项目管理
6. Fork：参与开源的正确姿势
7. GitHub Actions 入门
8. GitHub Pages：免费发布网站

## 附加模块
- 术语附录、已知坑点、可视化(Fork+PR流程)、中断点(步骤3后、步骤5后)