# Mini 小红书

小红书风格的图文/视频笔记社区平台，包含用户系统、笔记发布、社交互动（点赞/评论/关注/收藏）、消息通知、搜索等功能。

## 技术栈

| 层级 | 技术 |
|------|------|
| **后端** | Django 4.2 + Django REST Framework 3.15 + SimpleJWT 5.3 |
| **前端** | Vue 3 (Composition API) + Vite 5 + Pinia + Vue Router 4 + Element Plus |
| **数据库** | SQLite（开发）/ MySQL（生产） |
| **其他** | django-cors-headers、Pillow（图片处理） |

## 项目结构

`
mini-redbook/
├── backend/                    # Django 后端
│   ├── apps/
│   │   ├── accounts/           # 用户注册/登录/资料/邮箱手机绑定
│   │   ├── notes/              # 笔记发布/编辑/删除/评论
│   │   ├── social/             # 关注/点赞/收藏/评论点赞
│   │   ├── messaging/          # 私信/通知系统
│   │   └── search/             # 搜索
│   ├── common/                 # 工具类（统一响应、分页、异常处理）
│   ├── config/                 # Django 配置
│   ├── media/                  # 上传文件存储
│   ├── manage.py
│   └── requirements.txt
├── frontend/                   # Vue 3 前端
│   ├── src/
│   │   ├── api/                # API 封装
│   │   ├── stores/             # Pinia 状态管理
│   │   ├── views/              # 页面组件
│   │   ├── utils/              # 工具函数
│   │   └── router/             # 路由配置
│   ├── package.json
│   └── vite.config.js
├── README.md
└── .gitignore
`

## 快速启动

### 环境要求

- Python 3.10+
- Node.js 18+
- npm 9+

### 1. 后端

`ash
cd backend
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
`

后端运行在 http://localhost:8000

### 2. 前端

`ash
cd frontend
npm install
npm run dev
`

前端运行在 http://localhost:5173

Vite 已配置代理，/api 和 /media 请求自动转发到后端 http://localhost:8000。

## 环境配置

### 后端配置（ackend/config/settings.py）

| 配置项 | 默认值 | 说明 |
|--------|--------|------|
| SECRET_KEY | django-insecure-... | JWT 签名密钥，生产环境必须替换 |
| DEBUG | True | 生产环境设为 False |
| DATABASES | SQLite | 生产环境建议切换为 MySQL |
| EMAIL_HOST | smtp.qq.com | QQ 邮箱 SMTP 服务器 |
| EMAIL_HOST_USER | 2825919095@qq.com | 发件邮箱地址 |
| EMAIL_HOST_PASSWORD | — | SMTP 授权码 |
| ACCESS_TOKEN_LIFETIME | 7 天 | JWT Access Token 有效期 |
| REFRESH_TOKEN_LIFETIME | 14 天 | JWT Refresh Token 有效期 |

### 前端配置（rontend/vite.config.js）

| 配置项 | 默认值 | 说明 |
|--------|--------|------|
| server.port | 5173 | 开发服务器端口 |
| proxy./api.target | http://localhost:8000 | API 代理目标地址 |

## API 概览

| 模块 | 端点 | 说明 |
|------|------|------|
| **账号** | POST /api/accounts/register/ | 注册（手机号为 11 位数字） |
| | POST /api/accounts/login/ | 登录 |
| | GET /api/accounts/profile/{id}/ | 获取用户资料 |
| | PATCH /api/accounts/profile/ | 更新个人资料 |
| **笔记** | GET/POST /api/notes/ | 笔记列表/发布 |
| | GET/PUT/DELETE /api/notes/{id}/ | 笔记详情/编辑/删除 |
| | POST /api/notes/{id}/comment/ | 评论 |
| **社交** | POST /api/social/follow/{id}/ | 关注/取消关注 |
| | POST /api/social/notes/{id}/like/ | 点赞/取消点赞 |
| | POST/DELETE /api/social/favorites/ | 收藏/取消收藏 |
| | GET /api/social/favorite-folders/ | 收藏夹列表 |
| **消息** | GET /api/messaging/notifications/ | 通知列表 |
| | GET /api/messaging/notifications/unread-count/ | 未读通知数 |
| | GET /api/messaging/conversations/ | 私信会话列表 |

## 已知问题

1. **开发环境验证码** — 手机/邮箱验证码固定为 666666，不真实发送（见 pps/accounts/views.py 中 SendPhoneCodeView 和 SendEmailCodeView）。
2. **昵称唯一性** — User 模型的 
ickname 字段设置了 unique=True，注册时不填昵称会默认使用手机号，若已被占用则注册失败。个人主页编辑资料时可修改昵称。
3. **收藏逻辑** — 每个用户对一篇笔记最多收藏一次（unique_together = [("user", "note")]），切换收藏夹即转移而非复制。
4. **邮箱配置** — SMTP 配置使用的是 QQ 邮箱，其中的 EMAIL_HOST_PASSWORD 为 SMTP 授权码。更换发件邮箱需同步修改。
5. **图片/视频上传** — 媒体文件存储在 ackend/media/ 目录下，生产环境建议切换为对象存储（如阿里云 OSS）。
6. **未登录状态** — 部分接口（如通知未读数、收藏管理等）依赖 JWT 认证，未登录时会返回 401，前端会弹出登录框。
7. **注册手机号校验** — 前端和后端均校验手机号必须为 11 位纯数字。
8. **密码最小长度** — 注册时密码至少 6 位。

## 开发模式

本项目的开发流程为 "Prompt → 实现 → 预览 → 修复" 的快速迭代模式（Vibe Coding）：
1. 自然语言描述需求（中文）
2. AI 生成/修改代码（前后端联动）
3. 即时预览（Vite HMR + Django auto-reload）
4. 发现问题再修（浏览器控制台 + UI 异常）
5. 反复打磨 UI
6. Git 提交

## License

MIT