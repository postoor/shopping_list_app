# 家庭購物清單管理系統

全端購物清單協作平台，支援好友邀請、精細共享權限與購物計畫管理。

## 快速啟動

### 方法一：Docker Compose（推薦）

```bash
# 複製環境變數
cp backend/.env.example backend/.env
# 啟動所有服務
docker-compose up -d
```

訪問：
- 前端：http://localhost:5173
- 後端 API 文件：http://localhost:8000/api/docs

---

### 方法二：手動啟動

#### 後端

```bash
cd backend
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env              # 編輯 .env 填入 DB 和 SMTP 設定
uvicorn main:app --reload
```

#### 前端

```bash
cd frontend
npm install
npm run dev
```

---

## 系統架構

```
ShoppingList/
├── backend/
│   ├── main.py                   # FastAPI 主程式 & 啟動
│   ├── requirements.txt
│   ├── .env.example
│   └── app/
│       ├── core/
│       │   ├── config.py         # 環境設定 (pydantic-settings)
│       │   ├── database.py       # AsyncSession 連線池
│       │   ├── security.py       # JWT + bcrypt
│       │   └── deps.py           # get_current_user dependency
│       ├── models/               # SQLAlchemy ORM 模型
│       │   ├── user.py           # User, Friendship, InvitationToken
│       │   ├── item.py           # Item, ItemShare
│       │   ├── group.py          # Group, GroupMember
│       │   └── plan.py           # ShoppingPlan, PlanItem, PurchaseRecord
│       ├── schemas/              # Pydantic v2 驗證 Schema
│       ├── routers/              # API 路由
│       │   ├── auth.py           # 註冊/登入/刷新/個人資料
│       │   ├── friends.py        # 好友清單 & 郵件邀請
│       │   ├── items.py          # 物品 CRUD & 分享
│       │   ├── groups.py         # 群組 & 成員管理
│       │   └── plans.py          # 購物計畫 & 購買紀錄
│       └── services/
│           └── email.py          # SMTP 邀請信發送
└── frontend/
    └── src/
        ├── api/                  # Axios 封裝（自動 JWT 刷新）
        ├── stores/               # Pinia 狀態管理
        ├── router/               # Vue Router（含 Auth guard）
        ├── views/                # 頁面
        │   ├── LoginView.vue
        │   ├── RegisterView.vue
        │   ├── ItemsView.vue     # 物品清單 + 篩選
        │   ├── PlansView.vue     # 購物計畫
        │   ├── GroupsView.vue    # 群組管理
        │   ├── FriendsView.vue   # 好友 & 邀請
        │   └── HistoryView.vue   # 購買紀錄查詢
        └── components/
            ├── items/ItemCard.vue
            ├── items/ItemForm.vue
            ├── plans/PlanCard.vue
            ├── plans/PlanCreateModal.vue
            └── shared/ShareModal.vue
```

## API 路由總覽

| 方法   | 路徑                                | 說明                       |
|--------|-------------------------------------|----------------------------|
| POST   | /api/v1/auth/register               | 註冊（支援邀請 token）      |
| POST   | /api/v1/auth/login                  | 登入取得 JWT               |
| POST   | /api/v1/auth/refresh                | 刷新 Access Token          |
| GET    | /api/v1/auth/me                     | 取得個人資料               |
| GET    | /api/v1/friends                     | 好友清單                   |
| POST   | /api/v1/friends/invite              | 寄送邀請信                 |
| GET    | /api/v1/items                       | 物品清單（含共享）         |
| POST   | /api/v1/items                       | 新增物品                   |
| PATCH  | /api/v1/items/{id}                  | 更新物品                   |
| POST   | /api/v1/items/{id}/shares           | 分享物品給好友             |
| GET    | /api/v1/groups                      | 群組清單                   |
| POST   | /api/v1/groups/{id}/members         | 新增群組成員               |
| POST   | /api/v1/plans                       | 建立購物計畫               |
| PATCH  | /api/v1/plans/{id}/items/{piId}     | 勾除計畫物品               |
| POST   | /api/v1/plans/{id}/complete         | 完成計畫並轉存購買紀錄     |
| GET    | /api/v1/plans/{id}/records          | 查詢購買紀錄               |

## 環境變數說明

| 變數                        | 說明                          |
|-----------------------------|-------------------------------|
| `DATABASE_URL`              | PostgreSQL 連線字串           |
| `SECRET_KEY`                | JWT 簽名金鑰（請用隨機值）    |
| `SMTP_USERNAME/PASSWORD`    | Gmail App Password            |
| `FRONTEND_URL`              | 前端網址（CORS & 邀請連結）   |
| `INVITATION_EXPIRE_HOURS`   | 邀請連結有效時數（預設 48）   |
