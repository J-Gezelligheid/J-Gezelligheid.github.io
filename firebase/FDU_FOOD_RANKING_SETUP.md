# FDU Ranking Firebase 上线步骤（美食/咖啡/书店）

## 1. 创建 Firebase 项目

1. 打开 Firebase Console，创建一个新项目。
2. 在项目中创建 Realtime Database，选择离复旦用户较近的区域（如 `asia-southeast1`）。
3. 先用 `Locked mode` 建库，后续再粘贴本仓库规则。

## 2. 开启匿名登录

1. 打开 `Authentication` -> `Sign-in method`。
2. 启用 `Anonymous`。

## 3. 获取前端配置参数

1. 打开项目设置 -> `General` -> `Your apps`。
2. 新建或选择 `Web app`。
3. 记录 `Web API Key` 和 `Database URL`。

## 4. 写入站点配置

分别编辑以下三个配置文件的 `firebase` 节点：

- `_data/fdu_food_ranking.json`
- `_data/fdu_coffee_ranking.json`
- `_data/fdu_bookstore_ranking.json`

示例：

```json
"firebase": {
  "enabled": true,
  "database_url": "https://YOUR_PROJECT_ID-default-rtdb.firebaseio.com",
  "api_key": "YOUR_WEB_API_KEY",
  "data_root": "fdu_food_ranking",
  "sync_interval_ms": 15000
}
```

## 5. 发布数据库规则

1. 打开 `Realtime Database` -> `Rules`。
2. 复制 `firebase/fdu_food_ranking.database.rules.json` 全部内容。
3. 粘贴并点击 `Publish`。

## 6. 上线后验收

1. 用两个不同浏览器或无痕窗口打开 `/blogs/fdu-food-ranking/`。
2. A 端新增店铺或评分。
3. B 端应在 15 秒内自动同步出更新，且总榜均值同步变化。
4. 对 `/blogs/fdu-coffee-ranking/` 与 `/blogs/fdu-bookstore-ranking/` 重复同样测试。
