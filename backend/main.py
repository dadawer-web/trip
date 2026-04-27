from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Vibe Trip API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

TRIPS_DATA = [
    {
        "id": 1,
        "name": "冰岛蓝湖",
        "slug": "iceland-blue-lagoon",
        "description": "火山岩环绕的地热温泉，奶蓝色的水面上升腾着朦胧蒸汽。",
        "emotion_description": "在硫磺与蒸汽中感受地球的呼吸",
        "cover_image_url": "https://images.unsplash.com/photo-1610623532431-94a3f48c0c56?q=80&w=1920&auto=format&fit=crop",
        "country": "冰岛",
        "region": "格林达维克",
        "latitude": 63.8804,
        "longitude": -22.4495,
        "best_season": "9月-次年5月",
        "tags": [
            {"id": 1, "name": "温泉", "slug": "hotspring", "color": "#4ECDC4", "icon": "♨️"},
            {"id": 2, "name": "极光", "slug": "aurora", "color": "#A8E6CF", "icon": "🌌"},
        ],
        "created_at": "2026-04-27T10:00:00Z",
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
        "tags": [
            {"id": 3, "name": "海岛", "slug": "island", "color": "#45B7D1", "icon": "🏝️"},
        ],
        "created_at": "2026-04-27T10:00:00Z",
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
        "tags": [
            {"id": 4, "name": "徒步", "slug": "hiking", "color": "#96CEB4", "icon": "🥾"},
            {"id": 2, "name": "极光", "slug": "aurora", "color": "#A8E6CF", "icon": "🌌"},
        ],
        "created_at": "2026-04-27T10:00:00Z",
    },
    {
        "id": 4,
        "name": "京都岚山竹林",
        "slug": "kyoto-arashiyama-bamboo",
        "description": "千竿翠竹织成一条幽深的绿色隧道，风过处叶声如潮。",
        "emotion_description": "在竹影婆娑间，与自己静静相遇",
        "cover_image_url": "https://images.unsplash.com/photo-1528360983277-13d9012356ee?q=80&w=1920&auto=format&fit=crop",
        "country": "日本",
        "region": "京都",
        "latitude": 35.0094,
        "longitude": 135.667,
        "best_season": "3月-5月、10月-11月",
        "tags": [
            {"id": 5, "name": "文化", "slug": "culture", "color": "#DDA0DD", "icon": "⛩️"},
            {"id": 6, "name": "自然", "slug": "nature", "color": "#77DD77", "icon": "🌿"},
        ],
        "created_at": "2026-04-27T10:00:00Z",
    },
    {
        "id": 5,
        "name": "撒哈拉沙漠星空露营",
        "slug": "sahara-stargazing",
        "description": "绵延无际的金色沙丘，夜幕降临后银河如瀑倾泻。",
        "emotion_description": "在亿万年的星光下，所有的烦恼都变得渺小",
        "cover_image_url": "https://images.unsplash.com/photo-1509023464722-18d996393ca8?q=80&w=1920&auto=format&fit=crop",
        "country": "摩洛哥",
        "region": "梅尔祖卡",
        "latitude": 31.0966,
        "longitude": -4.0115,
        "best_season": "10月-次年4月",
        "tags": [
            {"id": 7, "name": "沙漠", "slug": "desert", "color": "#F4A460", "icon": "🏜️"},
            {"id": 2, "name": "极光", "slug": "aurora", "color": "#A8E6CF", "icon": "🌌"},
        ],
        "created_at": "2026-04-27T10:00:00Z",
    },
]


def get_trips(tag: str | None = None) -> list[dict]:
    """Return trips, optionally filtered by tag slug."""
    if tag is None:
        return TRIPS_DATA

    return [
        trip
        for trip in TRIPS_DATA
        if any(t["slug"] == tag for t in trip.get("tags", []))
    ]


@app.get("/api/trips")
def list_trips(tag: str | None = Query(None)) -> dict:
    trips = get_trips(tag=tag)
    return {"items": trips, "total": len(trips)}
