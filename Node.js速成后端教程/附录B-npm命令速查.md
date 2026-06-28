# 附录B：npm 命令速查

> 本附录收录教程中使用的所有 npm 命令，按使用频率排列。每个命令给出最常用示例和对应教程章节。

---

| 命令 | 作用 | 示例 | 对应章节 |
|------|------|------|----------|
| `npm init` | 初始化项目，创建 `package.json` | `npm init -y`（`-y` 跳过提问，全部默认） | 02 |
| `npm install` | 安装 `package.json` 中列出的所有依赖 | `npm install` | 02 |
| `npm install <包名>` | 安装指定包到 `dependencies`（生产依赖） | `npm install express` | 02 |
| `npm install --save-dev <包名>` | 安装指定包到 `devDependencies`（开发依赖） | `npm install --save-dev jest` | 26 |
| `npm install <包名>@<版本>` | 安装指定版本的包 | `npm install express@4.18.2` | 02 |
| `npm uninstall <包名>` | 卸载指定包，从 `package.json` 中移除 | `npm uninstall bcrypt` | 17 |
| `npm update` | 更新所有依赖到符合版本范围的最新版 | `npm update` | 02 |
| `npm run <脚本名>` | 执行 `package.json` 中 `scripts` 定义的脚本 | `npm run dev` | 02 |
| `npm start` | 执行 `scripts` 中的 `start` 脚本（`npm run start` 的简写） | `npm start` | 02 |
| `npm test` | 执行 `scripts` 中的 `test` 脚本 | `npm test` | 26 |
| `npm list` | 查看已安装的依赖树 | `npm list --depth=0`（只看顶层依赖） | 02 |
| `npm audit` | 检查依赖中的已知安全漏洞 | `npm audit` | 02 |
| `npm audit fix` | 自动修复可修复的安全漏洞 | `npm audit fix` | 02 |
| `npm ci` | 严格按 `package-lock.json` 安装依赖（CI/CD 环境用） | `npm ci` | 30 |
| `npx <命令>` | 临时执行 npm 包的命令（不全局安装） | `npx jest --version` | 26 |
| `npm init -y` | 快速初始化项目，跳过所有提问 | `npm init -y` | 02 |
| `npm install -g <包名>` | 全局安装包（所有项目都能用） | `npm install -g pm2` | 27 |

---

## 常用安装命令速查

以下是在本教程中实际使用的安装命令：

```bash
# 生产依赖（dependencies）
npm install express
npm install better-sqlite3
npm install bcryptjs          # 如 bcrypt 编译失败，改用 bcryptjs
npm install jsonwebtoken
npm install dotenv
npm install multer
npm install morgan
npm install cors

# 开发依赖（devDependencies）
npm install --save-dev jest
npm install --save-dev supertest
npm install --save-dev nodemon

# 全局安装
npm install -g pm2
```

---

## package.json scripts 常用配置

```json
{
  "scripts": {
    "start": "node server.js",
    "dev": "nodemon server.js",
    "test": "jest --runInBand",
    "test:watch": "jest --watch",
    "test:coverage": "jest --coverage"
  }
}
```

| 脚本 | 运行命令 | 说明 |
|------|----------|------|
| `start` | `npm start` | 生产环境启动 |
| `dev` | `npm run dev` | 开发环境启动（nodemon 自动重启） |
| `test` | `npm test` | 运行测试（`--runInBand` 串行执行，避免 SQLite 锁冲突） |
| `test:watch` | `npm run test:watch` | 监视模式，文件变化自动重跑测试 |
| `test:coverage` | `npm run test:coverage` | 运行测试并生成覆盖率报告 |

---

## 版本号说明

`package.json` 中的版本号遵循**语义化版本（SemVer）**规则：

```
"express": "^4.18.2"
              │ │  └── 修订号（Patch）：修 Bug，不新增功能
              │ └──── 次版本号（Minor）：新增功能，向后兼容
              └────── 主版本号（Major）：不兼容的大改动
```

| 符号 | 含义 | 示例 `^4.18.2` 允许的版本 |
|------|------|---------------------------|
| `^` | 兼容版本——允许次版本和修订号更新 | `>=4.18.2` 且 `<5.0.0` |
| `~` | 约等于版本——只允许修订号更新 | `>=4.18.2` 且 `<4.19.0` |
| 无符号 | 精确版本——只允许这个版本 | 只允许 `4.18.2` |
| `*` | 任意版本 | 任意版本 |

---

## 常见问题

| 问题 | 原因 | 解决 |
|------|------|------|
| `npm install` 很慢 | 默认 npm 源在国外 | 换淘宝镜像：`npm config set registry https://registry.npmmirror.com` |
| `npm install` 报 EACCES 权限错误 | Linux/macOS 权限问题 | 不要用 `sudo`，改用 `npm config set prefix` 或 nvm 管理 Node |
| `npm install` 报 `node-gyp` 错误 | 原生模块编译失败（如 bcrypt） | 改用纯 JS 备选：`npm install bcryptjs` |
| `npm start` 报 `missing script: start` | `package.json` 中没有 `"start"` 脚本 | 添加 `"start": "node server.js"` |
| `npx` 命令找不到 | Node.js 版本太旧（< 5.2） | 升级 Node.js 到 18+ |