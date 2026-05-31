# Docker完全自学教程：从零基础到项目实战专家

- 对应文档版本：暂无具体版本，基于Docker最新稳定版
- 适用环境：Windows 10/11 (排除macOS)、Linux (Ubuntu/Debian/CentOS)，Docker Engine 24.x+
- 读者角色：覆盖所有技术角色，以完全零基础学习者为起点
- 预计耗时：新手约20-30小时，熟手约10-15小时（含实操）
- 前置教程：无需特殊前置，仅需基本电脑操作能力
- 可视化：有，包含架构图、流程图、状态转换图等（见可视化说明）

## 目标与完成效果
**目标**：使完全没有Docker经验的学习者通过系统学习，能够独立完成Docker环境安装配置、编写优化Dockerfile、使用Docker Compose编排多容器应用、部署完整Web项目，并能够流畅回答任何Docker相关理论和实操问题。

**完成后的可观测效果**：
- 成功在Windows/Linux环境中安装并运行Docker Engine
- 能够使用docker pull/run/build等命令管理容器生命周期
- 编写并构建一个多层次的自定义应用镜像（含依赖缓存优化）
- 使用Docker Volume实现数据持久化和容器间数据共享
- 配置自定义bridge网络实现服务间安全通信
- 使用docker-compose.yml定义并启动一个包含后端API、前端UI、数据库、缓存的完整微服务应用
- 通过docker logs、docker inspect、docker stats等工具排查常见问题
- 应用镜像多阶段构建、.dockerignore、资源限制等生产最佳实践

## 前置条件
- **软件/依赖**：
  - Windows 10/11 专业版或企业版（支持WSL2）或 Linux 发行版（Ubuntu 22.04 LTS 推荐）
  - 至少4GB内存（建议8GB+），20GB+可用磁盘空间
  - 管理员/root权限用于安装Docker
  - 基础网络连接能力（能够访问Docker Hub）
- **必须完成的前置步骤**：
  1. 确认操作系统版本满足Docker最低要求
  2. 如为Windows，启用WSL2并安装Linux内核更新包
  3. 如为Linux，确保发行版支持的内核版本 >= 4.9
- **环境验证命令**：
  ```powershell
  # Windows PowerShell 或 CMD
  docker version
  ```
  预期输出包含Client和Server的版本信息，无错误提示。

## 分步操作
（占位符，将在细纲中详细展开）

## 完整代码清单
（占位符）

## 验证方法
- 最终验证：使用docker-compose up启动完整项目，通过浏览器访问前端界面并验证后端API响应；执行docker-compose down清理资源；确保全过程无错误且能够重复执行。

## 术语附录
（占位符）

## 已知坑点与禁止事项
（占位符，将从AI必看.md中提取相关内容）

## 下一步建议
- 学习Docker Swarm基本概念
- 探索Kubernetes与Docker的关系
- 研究镜像安全扫描工具（如Trivy、Anchore）
- 了解生产环境监控方案（Prometheus + Grafana + ELK）
- 尝试将项目部署到云厂商托管容器服务（如AWS ECS、Azure Container Instances）

## 中断点标记
- [可暂停点 1/6]：完成第3章“基本命令操作”后，能够熟练使用docker run/pull/ps/stop/rm等命令
- [可暂停点 2/6]：完成第5章“Docker网络”后，能够配置自定义网络并验证容器间通信
- [可暂停点 3/6]：完成第7章“Docker Compose基础”后，能够编写docker-compose.yml启动多容器应用
- [可暂停点 4/6]：完成第9章“项目实战：后端API”后，能够独立构建并运行后端服务
- [可暂停点 5/6]：完成第10章“项目实战：全栈部署”后，能够部署完整Web应用并进行基本故障排除
- [可暂停点 6/6]：完成全部章节并通过最终验证

## 变更记录
- v1.0 (2026-05-30)：初版大纲完成