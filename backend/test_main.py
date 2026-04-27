import pytest
from fastapi.testclient import TestClient

from main import app


client = TestClient(app)


# ==================== Fixtures ====================

@pytest.fixture
def sample_trips():
    """返回一组用于测试的 mock 旅行地数据"""
    return [
        {
            "id": 1,
            "name": "冰岛蓝湖",
            "slug": "iceland-blue-lagoon",
            "description": "火山岩环绕的地热温泉，奶蓝色的水面上升腾着朦胧蒸汽。",
            "emotion_description": "在硫磺与蒸汽中感受地球的呼吸",
            "cover_image_url": "https://cdn.example.com/iceland-blue-lagoon-4k.jpg",
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
            "cover_image_url": "https://cdn.example.com/maldives-overwater-4k.jpg",
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
            "cover_image_url": "https://cdn.example.com/swiss-alps-4k.jpg",
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
    ]


@pytest.fixture(autouse=True)
def override_trips_dependency(monkeypatch, sample_trips):
    """mock 数据层，使测试不依赖真实数据库

    假设 main.py 中暴露 get_trips(tag: str | None = None) -> list[dict]
    作为数据查询入口。若后续实现细节调整，同步修改此 fixture 即可。
    """

    def mock_get_trips(tag: str | None = None):
        if tag is None:
            return sample_trips
        return [
            trip
            for trip in sample_trips
            if any(t["slug"] == tag for t in trip["tags"])
        ]

    monkeypatch.setattr("main.get_trips", mock_get_trips)


# ==================== Tests ====================

def test_get_trips_filter_by_existing_tag():
    """场景1：正常匹配标签 —— 传入存在的 tag，应返回包含该标签的旅行地"""
    response = client.get("/api/trips?tag=hotspring")
    assert response.status_code == 200

    data = response.json()
    assert "items" in data
    assert data["total"] == 1
    assert len(data["items"]) == 1

    trip = data["items"][0]
    assert trip["slug"] == "iceland-blue-lagoon"
    assert any(t["slug"] == "hotspring" for t in trip["tags"])


def test_get_trips_filter_by_nonexistent_tag_returns_empty():
    """场景2：传入不存在的标签 —— 应返回空列表，total 为 0"""
    response = client.get("/api/trips?tag=nonexistent")
    assert response.status_code == 200

    data = response.json()
    assert data["items"] == []
    assert data["total"] == 0


def test_get_trips_without_tag_returns_all():
    """场景3：不传 tag 参数 —— 应返回全部旅行地列表"""
    response = client.get("/api/trips")
    assert response.status_code == 200

    data = response.json()
    assert data["total"] == 3
    assert len(data["items"]) == 3

    slugs = {t["slug"] for t in data["items"]}
    assert slugs == {"iceland-blue-lagoon", "maldives-overwater", "swiss-alps-hiking"}
