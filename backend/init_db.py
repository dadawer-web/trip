import sqlite3
import json

DB_PATH = "trips.db"

SEED_TRIPS = [
    {
        "id": 1,
        "name": "冰岛蓝湖",
        "description": "火山岩环绕的地热温泉，奶蓝色的水面上升腾着朦胧蒸汽。",
        "tags": [
            {"id": 1, "name": "温泉", "slug": "hotspring", "color": "#4ECDC4", "icon": "♨️"},
            {"id": 2, "name": "极光", "slug": "aurora", "color": "#A8E6CF", "icon": "🌌"},
        ],
        "image_url": "https://images.unsplash.com/photo-1610623532431-94a3f48c0c56?q=80&w=1920&auto=format&fit=crop",
    },
    {
        "id": 2,
        "name": "马尔代夫水上屋",
        "description": "面朝印度洋的私人露台，脚下是透明的珊瑚花园。",
        "tags": [
            {"id": 3, "name": "海岛", "slug": "island", "color": "#45B7D1", "icon": "🏝️"},
        ],
        "image_url": "https://images.unsplash.com/photo-1514282401047-d79a71a590e8?q=80&w=1920&auto=format&fit=crop",
    },
    {
        "id": 3,
        "name": "瑞士阿尔卑斯徒步",
        "description": "穿行于雪山、草甸与牛铃声中。",
        "tags": [
            {"id": 4, "name": "徒步", "slug": "hiking", "color": "#96CEB4", "icon": "🥾"},
            {"id": 2, "name": "极光", "slug": "aurora", "color": "#A8E6CF", "icon": "🌌"},
        ],
        "image_url": "https://images.unsplash.com/photo-1531366936337-7c912a4589a7?q=80&w=1920&auto=format&fit=crop",
    },
    {
        "id": 4,
        "name": "京都岚山竹林",
        "description": "千竿翠竹织成一条幽深的绿色隧道，风过处叶声如潮。",
        "tags": [
            {"id": 5, "name": "文化", "slug": "culture", "color": "#DDA0DD", "icon": "⛩️"},
            {"id": 6, "name": "自然", "slug": "nature", "color": "#77DD77", "icon": "🌿"},
        ],
        "image_url": "https://images.unsplash.com/photo-1528360983277-13d9012356ee?q=80&w=1920&auto=format&fit=crop",
    },
    {
        "id": 5,
        "name": "撒哈拉沙漠星空露营",
        "description": "绵延无际的金色沙丘，夜幕降临后银河如瀑倾泻。",
        "tags": [
            {"id": 7, "name": "沙漠", "slug": "desert", "color": "#F4A460", "icon": "🏜️"},
            {"id": 2, "name": "极光", "slug": "aurora", "color": "#A8E6CF", "icon": "🌌"},
        ],
        "image_url": "https://images.unsplash.com/photo-1509023464722-18d996393ca8?q=80&w=1920&auto=format&fit=crop",
    },
]


def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("DROP TABLE IF EXISTS trips")
    cursor.execute("""
        CREATE TABLE trips (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT,
            tags TEXT,
            image_url TEXT
        )
    """)

    for trip in SEED_TRIPS:
        cursor.execute(
            """
            INSERT INTO trips (id, name, description, tags, image_url)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                trip["id"],
                trip["name"],
                trip["description"],
                json.dumps(trip["tags"], ensure_ascii=False),
                trip["image_url"],
            ),
        )

    conn.commit()
    conn.close()
    print(f"数据库初始化完成: {DB_PATH}")
    print(f"已插入 {len(SEED_TRIPS)} 条旅行地数据")


if __name__ == "__main__":
    init_db()
