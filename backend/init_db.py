import os
import sqlite3
import json
from datetime import datetime, timezone

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "trips.db")

SEED_TRIPS = [
    {
        "id": 1,
        "name": "冰岛蓝湖",
        "slug": "iceland-blue-lagoon",
        "description": "火山岩环绕的地热温泉，奶蓝色的水面上升腾着朦胧蒸汽。",
        "emotion_description": "在硫磺与蒸汽中感受地球的呼吸",
        "cover_image_url": "https://images.unsplash.com/photo-1504893524553-b855bce32c67?q=80&w=1920&auto=format&fit=crop",
        "country": "冰岛",
        "region": "格林达维克",
        "latitude": 63.8804,
        "longitude": -22.4495,
        "best_season": "9月-次年5月",
        "is_featured": 1,
        "tags": [
            {"id": 1, "name": "温泉", "slug": "hotspring", "color": "#4ECDC4", "icon": "♨️"},
            {"id": 2, "name": "极光", "slug": "aurora", "color": "#A8E6CF", "icon": "🌌"},
        ],
    },
    {
        "id": 2,
        "name": "马尔代夫水上屋",
        "slug": "maldives-overwater",
        "description": "面朝印度洋的私人露台，脚下是透明的珊瑚花园。",
        "emotion_description": "在印度洋的摇篮里听见自己的心跳",
        "cover_image_url": "https://images.unsplash.com/photo-1514282401047-d79a71a590e8?q=80&w=1920&auto=format&fit=crop",
        "country": "马尔代夫",
        "region": "马累环礁",
        "latitude": 4.1755,
        "longitude": 73.5093,
        "best_season": "11月-次年4月",
        "is_featured": 1,
        "tags": [
            {"id": 3, "name": "海岛", "slug": "island", "color": "#45B7D1", "icon": "🏝️"},
        ],
    },
    {
        "id": 3,
        "name": "瑞士阿尔卑斯徒步",
        "slug": "swiss-alps-hiking",
        "description": "穿行于雪山、草甸与牛铃声中。",
        "emotion_description": "每一步都是与山神的对话",
        "cover_image_url": "https://images.unsplash.com/photo-1531366936337-7c912a4589a7?q=80&w=1920&auto=format&fit=crop",
        "country": "瑞士",
        "region": "因特拉肯",
        "latitude": 46.6863,
        "longitude": 7.8632,
        "best_season": "6月-9月",
        "is_featured": 0,
        "tags": [
            {"id": 4, "name": "徒步", "slug": "hiking", "color": "#96CEB4", "icon": "🥾"},
            {"id": 2, "name": "极光", "slug": "aurora", "color": "#A8E6CF", "icon": "🌌"},
        ],
    },
    {
        "id": 4,
        "name": "京都岚山竹林",
        "slug": "kyoto-arashiyama-bamboo",
        "description": "千竿翠竹织成一条幽深的绿色隧道，风过处叶声如潮。",
        "emotion_description": "在竹影婆娑中听见风的声音",
        "cover_image_url": "https://images.unsplash.com/photo-1545569341-9eb8b30979d9?q=80&w=1920&auto=format&fit=crop",
        "country": "日本",
        "region": "京都",
        "latitude": 35.0094,
        "longitude": 135.6668,
        "best_season": "3月-5月 / 10月-11月",
        "is_featured": 1,
        "tags": [
            {"id": 5, "name": "文化", "slug": "culture", "color": "#DDA0DD", "icon": "⛩️"},
            {"id": 6, "name": "自然", "slug": "nature", "color": "#77DD77", "icon": "🌿"},
        ],
    },
    {
        "id": 5,
        "name": "撒哈拉沙漠星空露营",
        "slug": "sahara-stargazing-camp",
        "description": "绵延无际的金色沙丘，夜幕降临后银河如瀑倾泻。",
        "emotion_description": "在宇宙的幕布下，重新认识自己",
        "cover_image_url": "https://images.unsplash.com/photo-1509023464722-18d996393ca8?q=80&w=1920&auto=format&fit=crop",
        "country": "摩洛哥",
        "region": "梅尔祖卡",
        "latitude": 31.0966,
        "longitude": -4.0116,
        "best_season": "10月-次年4月",
        "is_featured": 0,
        "tags": [
            {"id": 7, "name": "沙漠", "slug": "desert", "color": "#F4A460", "icon": "🏜️"},
            {"id": 2, "name": "极光", "slug": "aurora", "color": "#A8E6CF", "icon": "🌌"},
        ],
    },
]


def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("DROP TABLE IF EXISTS trips")
    cursor.execute("""
        CREATE TABLE trips (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            slug TEXT NOT NULL UNIQUE,
            description TEXT,
            emotion_description TEXT,
            cover_image_url TEXT,
            country TEXT,
            region TEXT,
            latitude REAL,
            longitude REAL,
            best_season TEXT,
            is_featured INTEGER DEFAULT 0 CHECK(is_featured IN (0, 1)),
            tags TEXT,
            created_at TEXT DEFAULT (datetime('now')),
            updated_at TEXT DEFAULT (datetime('now'))
        )
    """)

    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    for trip in SEED_TRIPS:
        cursor.execute(
            """
            INSERT INTO trips (
                id, name, slug, description, emotion_description,
                cover_image_url, country, region, latitude, longitude,
                best_season, is_featured, tags, created_at, updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                trip["id"],
                trip["name"],
                trip["slug"],
                trip["description"],
                trip["emotion_description"],
                trip["cover_image_url"],
                trip["country"],
                trip["region"],
                trip["latitude"],
                trip["longitude"],
                trip["best_season"],
                trip["is_featured"],
                json.dumps(trip["tags"], ensure_ascii=False),
                now,
                now,
            ),
        )

    conn.commit()
    conn.close()
    print(f"数据库初始化完成: {DB_PATH}")
    print(f"已插入 {len(SEED_TRIPS)} 条旅行地数据")


if __name__ == "__main__":
    init_db()
