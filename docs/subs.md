# 订阅服务接口

## GET /subs/live

获取单个用户的直播状态

### API 输入

| 参数名 | 类型 | 必需 | 说明 |
|--------|------|------|------|
| uid | integer | 是 | 用户UID |

```bash
curl -X GET "http://localhost:40432/bilichatapi/subs/live?uid=12345678" \
  -H "Authorization: Bearer <your_token>"
```

### API 输出

返回LiveRoom对象数组：

| 字段名 | 类型 | 说明 |
|--------|------|------|
| title | string | 直播间标题 |
| room_id | integer | 直播间实际房间号 |
| uid | integer | 主播UID |
| online | integer | 直播间在线人数 |
| live_time | integer | 直播持续时长 |
| live_status | integer | 直播状态(0:未开播, 1:正在直播, 2:轮播中) |
| short_id | integer | 直播间短房间号 |
| area | integer | 直播间分区ID |
| area_name | string | 直播间分区名 |
| area_v2_id | integer | 直播间新版分区ID |
| area_v2_name | string | 直播间新版分区名 |
| area_v2_parent_id | integer | 直播间父分区ID |
| area_v2_parent_name | string | 直播间父分区名 |
| uname | string | 主播用户名 |
| face | string | 主播头像URL |
| tag_name | string | 直播间标签 |
| tags | string | 直播间自定标签 |
| cover_from_user | string | 直播间封面URL |
| keyframe | string | 直播间关键帧URL |
| lock_till | string | 直播间封禁信息 |
| hidden_till | string | 直播间隐藏信息 |
| broadcast_type | integer | 直播类型(0:普通直播, 1:手机直播) |

```json
[
  {
    "title": "今天也要开心鸭~",
    "room_id": 123456,
    "uid": 12345678,
    "online": 1024,
    "live_time": 3600,
    "live_status": 1,
    "short_id": 123,
    "area": 371,
    "area_name": "虚拟主播",
    "area_v2_id": 371,
    "area_v2_name": "虚拟主播",
    "area_v2_parent_id": 9,
    "area_v2_parent_name": "虚拟主播",
    "uname": "测试主播",
    "face": "https://i0.hdslb.com/bfs/face/xxx.jpg",
    "tag_name": "",
    "tags": "",
    "cover_from_user": "https://i0.hdslb.com/bfs/live/xxx.jpg",
    "keyframe": "https://i0.hdslb.com/bfs/live-key-frame/xxx.jpg",
    "lock_till": "",
    "hidden_till": "",
    "broadcast_type": 0
  }
]
```

---

## POST /subs/lives

批量获取多个用户的直播状态

### API 输入

| 参数名 | 类型 | 必需 | 说明 |
|--------|------|------|------|
| uids | array[integer] | 是 | 用户UID列表 |

```bash
curl -X POST "http://localhost:40432/bilichatapi/subs/lives" \
  -H "Authorization: Bearer <your_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "uids": [12345678, 87654321, 11111111]
  }'
```

### API 输出

返回LiveRoom对象数组，字段结构与单个用户查询相同。

```json
[
  {
    "title": "今天也要开心鸭~",
    "room_id": 123456,
    "uid": 12345678,
    "online": 1024,
    "live_time": 3600,
    "live_status": 1,
    "short_id": 123,
    "area": 371,
    "area_name": "虚拟主播",
    "area_v2_id": 371,
    "area_v2_name": "虚拟主播",
    "area_v2_parent_id": 9,
    "area_v2_parent_name": "虚拟主播",
    "uname": "测试主播1",
    "face": "https://i0.hdslb.com/bfs/face/xxx.jpg",
    "tag_name": "",
    "tags": "",
    "cover_from_user": "https://i0.hdslb.com/bfs/live/xxx.jpg",
    "keyframe": "https://i0.hdslb.com/bfs/live-key-frame/xxx.jpg",
    "lock_till": "",
    "hidden_till": "",
    "broadcast_type": 0
  },
  {
    "title": "学习直播间",
    "room_id": 654321,
    "uid": 87654321,
    "online": 512,
    "live_time": 1800,
    "live_status": 1,
    "short_id": 456,
    "area": 145,
    "area_name": "学习",
    "area_v2_id": 145,
    "area_v2_name": "学习",
    "area_v2_parent_id": 11,
    "area_v2_parent_name": "学习",
    "uname": "测试主播2",
    "face": "https://i0.hdslb.com/bfs/face/yyy.jpg",
    "tag_name": "",
    "tags": "",
    "cover_from_user": "https://i0.hdslb.com/bfs/live/yyy.jpg",
    "keyframe": "https://i0.hdslb.com/bfs/live-key-frame/yyy.jpg",
    "lock_till": "",
    "hidden_till": "",
    "broadcast_type": 0
  }
]
```

---

## GET /subs/dynamic

获取用户动态列表，可设置缓存机制

### API 输入

| 参数名 | 类型 | 必需 | 说明 |
|--------|------|------|------|
| uid | integer | 是 | 用户UID |
| offset | integer | 否 | 偏移量，默认0 |

```bash
curl -X GET "http://localhost:40432/bilichatapi/subs/dynamic?uid=12345678&offset=0" \
  -H "Authorization: Bearer <your_token>"
```

### API 输出

返回Dynamic对象数组：

| 字段名 | 类型 | 说明 |
|--------|------|------|
| dyn_id | integer | 动态ID |
| dyn_type | string | 动态类型 |
| dyn_timestamp | integer | 动态发布时间戳 |

**动态类型说明**:
- `DYNAMIC_TYPE_FORWARD`: 动态转发
- `DYNAMIC_TYPE_AV`: 投稿视频
- `DYNAMIC_TYPE_WORD`: 纯文字动态
- `DYNAMIC_TYPE_DRAW`: 带图动态
- `DYNAMIC_TYPE_ARTICLE`: 投稿专栏
- `DYNAMIC_TYPE_PGC`: 剧集
- `DYNAMIC_TYPE_MUSIC`: 音乐
- `DYNAMIC_TYPE_LIVE`: 直播间分享

```json
[
  {
    "dyn_id": 123456789,
    "dyn_type": "DYNAMIC_TYPE_AV",
    "dyn_timestamp": 1640995200
  },
  {
    "dyn_id": 123456790,
    "dyn_type": "DYNAMIC_TYPE_DRAW",
    "dyn_timestamp": 1640908800
  },
  {
    "dyn_id": 123456791,
    "dyn_type": "DYNAMIC_TYPE_WORD",
    "dyn_timestamp": 1640822400
  }
]
```
