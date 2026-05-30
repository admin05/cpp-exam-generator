# GESP C++ 在线测试平台

这是从当前 Word 试卷生成项目延伸出来的本地在线测试平台 MVP。

## 功能

- 管理员创建试卷：设置选择题数量、编程题数量和考试时长。
- 系统按 GESP C++ 四级偏上 / 五级入门原则均衡抽题。
- 考生在线完成选择题。
- 考生提交 C++17 编程题代码。
- 平台使用容器内 `g++` 编译代码，并用题目样例统计通过数量。
- SQLite 持久化保存试卷和提交记录。

## Docker Compose 部署

推荐方式：NAS 上克隆本仓库，以本地已拉取的代码构建镜像。

```bash
git clone https://github.com/admin05/gesp-cpp-exam-generator.git
cd gesp-cpp-exam-generator
docker compose up -d --build
```

以后更新：

```bash
git pull
docker compose up -d --build
```

如果只想让 Compose 直接从 GitHub 的 `main` 分支构建镜像，也可以使用：

```bash
docker compose -f docker-compose.github.yml up -d --build
```

如果 NAS 访问 `github.com` 不稳定，但可以像 metube 一样拉取 `ghcr.io` 镜像，推荐使用预构建镜像：

```bash
docker compose -f docker-compose.ghcr.yml up -d
```

每次代码推送到 GitHub 的 `main` 分支后，GitHub Actions 会自动发布：

```text
ghcr.io/admin05/gesp-cpp-exam-generator:latest
```

访问：

- 考试入口：http://NAS-IP:8088/
- 管理后台：http://NAS-IP:8088/admin

数据保存在项目根目录的 `data/exam.db`，NAS 重启或容器重建后不会丢失。

## 生产提醒

当前测评器适合本地教学、小范围信任环境使用。它会在应用容器内编译并运行考生代码，已经通过非 root 用户、内存限制、进程数限制和运行超时做了基础约束，但还不是严格安全沙箱。公开给不可信用户使用时，建议把判题服务拆到独立容器沙箱或专门 OJ 判题系统。
