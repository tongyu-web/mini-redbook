# Mini 小红书

小红书风格图文/视频笔记社区平台

## 技术栈

- **后端：** Django 4.2 + DRF 3.15 + SimpleJWT 5.3
- **前端：** Vue 3 (Composition API) + Vite 5 + Pinia + Vue Router 4 + Element Plus
- **数据库：** SQLite（开发）/ MySQL（生产）

## 快速启动

### 后端

```bash
cd backend
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

### 前端

```bash
cd frontend
npm install
npm run dev
```

访问 http://localhost:5173
