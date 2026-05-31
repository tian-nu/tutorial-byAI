# 全局术语索引

> 本文件为多教程共用的术语索引。每个教程新增术语在此追加。

| 术语 | 简要解释 | 出处教程 | 是否项目特有 |
|------|---------|---------|:--:|
| SSH Key / 公钥 / 私钥 | 锁和钥匙模型，公钥放GitHub，私钥留本地，用于免密身份验证 | Git到GitHub教程 | 否 |
| ed25519 | 一种现代SSH加密算法，比RSA更快更安全，密钥更短 | Git到GitHub教程 | 否 |
| passphrase | SSH私钥的二次密码，设置后每次使用私钥都需要输入 | Git到GitHub教程 | 否 |
| HTTPS vs SSH | 两种Git远程连接方式。SSH配置一次永久免密，HTTPS每次需输密码 | Git到GitHub教程 | 否 |
| `~` (tilde) | 表示用户主目录的简写，Windows在C:\Users\用户名，Mac/Linux在/home/用户名 | Git到GitHub教程 | 否 |
| Repository（仓库） | 一个项目的Git存储空间，包含所有文件和历史版本 | Git到GitHub教程 | 否 |
| .gitignore | 告诉Git忽略哪些文件/文件夹的配置文件 | Git到GitHub教程 | 否 |
| License（许可证） | 声明别人可以如何使用你的代码的法律文件，常见MIT/GPL/Apache | Git到GitHub教程 | 否 |
| origin | Git约定：默认远程仓库别名，通常指向你自己的GitHub仓库 | Git到GitHub教程 | 否（Git约定） |
| remote | Git概念：远程仓库的统称，可以添加多个（origin、upstream等） | Git到GitHub教程 | 否 |
| main/master | Git仓库的主分支名。Git 2.28+默认main，旧版用master，本质相同 | Git到GitHub教程 | 否 |
| Pull Request (PR) | 请求别人把你的代码合并到目标分支的机制，含审查、讨论、批准流程 | Git到GitHub教程 | 否 |
| Merge Request (MR) | GitLab对PR的叫法，功能相同 | Git到GitHub教程 | 否 |
| Code Review | 代码审查：逐行检查代码改动是否合理、是否引入Bug | Git到GitHub教程 | 否 |
| Approve | Review通过，认可改动可以合并（Code Review三种结论之一） | Git到GitHub教程 | 否 |
| Request Changes | 要求修改后重新审查（Code Review三种结论之一） | Git到GitHub教程 | 否 |
| Merge Commit | 合并策略：保留所有提交历史，新增一个合并提交 | Git到GitHub教程 | 否 |
| Squash | 合并策略：把所有提交压成一个干净提交，历史简洁 | Git到GitHub教程 | 否 |
| Rebase | 合并策略：变基后合并，历史完全线性 | Git到GitHub教程 | 否 |
| Issue | GitHub中的"任务便利贴"：Bug报告、功能请求、讨论话题 | Git到GitHub教程 | 否 |
| Bug Report | Bug报告：描述复现步骤、预期行为、实际行为 | Git到GitHub教程 | 否 |
| Feature Request | 功能请求：提出新功能或改进建议 | Git到GitHub教程 | 否 |
| Label | GitHub Issues/PR的分类标签（bug/enhancement/documentation等） | Git到GitHub教程 | 否 |
| Milestone | 里程碑：将一组Issues/PR归到同一个版本目标 | Git到GitHub教程 | 否 |
| Assignee | 被指定负责处理某个Issue或PR的人 | Git到GitHub教程 | 否 |
| Fork | 在GitHub上把别人的仓库完整复制到自己账户下的操作 | Git到GitHub教程 | 否 |
| upstream（上游） | Fork的原仓库。数据从上游流向下游，贡献从下游反馈回上游 | Git到GitHub教程 | 否（Git约定） |
| downstream（下游） | Fork出来的仓库，相对于原仓库是下游 | Git到GitHub教程 | 否（Git约定） |
| CI/CD | 持续集成/持续交付：代码提交后自动测试、自动部署的流水线 | Git到GitHub教程 | 否 |
| Workflow | GitHub Actions的顶级单元：定义触发条件和要执行的任务 | Git到GitHub教程 | 否 |
| Job | Workflow中的一个独立任务单元。多个Job默认并行运行 | Git到GitHub教程 | 否 |
| Step | Job中的一个执行步骤，按从上到下顺序依次执行 | Git到GitHub教程 | 否 |
| Runner | 执行Workflow的虚拟机。GitHub提供Ubuntu/Windows/macOS三种 | Git到GitHub教程 | 否 |
| Action | 别人封装好的可复用步骤（类似函数库），如actions/checkout | Git到GitHub教程 | 否 |
| GitHub Pages | GitHub免费静态网站托管服务，从仓库文件自动生成公网网站 | Git到GitHub教程 | 否 |
| 静态网站 | 全部由HTML/CSS/JS组成的网页，无后端代码处理逻辑 | Git到GitHub教程 | 否 |