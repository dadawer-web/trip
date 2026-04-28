import pytest
from fastapi.testclient import TestClient

from main import app


client = TestClient(app)


# ==================== Fixtures ====================

@pytest.fixture
def sample_trips():
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
            "is_featured": True,
            "tags": [
                {"id": 1, "name": "温泉", "slug": "hotspring", "color": "#4ECDC4", "icon": "♨️"},
                {"id": 2, "name": "极光", "slug": "aurora", "color": "#A8E6CF", "icon": "🌌"},
            ],
            "created_at": "2026-04-27T10:00:00Z",
            "updated_at": "2026-04-27T10:00:00Z",
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
            "is_featured": True,
            "tags": [
                {"id": 3, "name": "海岛", "slug": "island", "color": "#45B7D1", "icon": "🏝️"},
            ],
            "created_at": "2026-04-27T10:00:00Z",
            "updated_at": "2026-04-27T10:00:00Z",
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
            "is_featured": False,
            "tags": [
                {"id": 4, "name": "徒步", "slug": "hiking", "color": "#96CEB4", "icon": "🥾"},
                {"id": 2, "name": "极光", "slug": "aurora", "color": "#A8E6CF", "icon": "🌌"},
            ],
            "created_at": "2026-04-27T10:00:00Z",
            "updated_at": "2026-04-27T10:00:00Z",
        },
    ]


@pytest.fixture(autouse=True)
def override_trips_dependency(monkeypatch, sample_trips):
    def mock_get_trips(tag: str | None = None):
        if tag is None:
            return sample_trips
        return [
            trip
            for trip in sample_trips
            if any(t["slug"] == tag for t in trip["tags"])
        ]

    monkeypatch.setattr("main.get_trips", mock_get_trips)


# ==================== 基础功能测试 ====================

def test_get_trips_filter_by_existing_tag():
    """传入存在的 tag，应返回包含该标签的旅行地"""
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
    """传入不存在的标签，应返回空列表"""
    response = client.get("/api/trips?tag=nonexistent")
    assert response.status_code == 200

    data = response.json()
    assert data["items"] == []
    assert data["total"] == 0


def test_get_trips_without_tag_returns_all():
    """不传 tag 参数，应返回全部旅行地"""
    response = client.get("/api/trips")
    assert response.status_code == 200

    data = response.json()
    assert data["total"] == 3
    assert len(data["items"]) == 3

    slugs = {t["slug"] for t in data["items"]}
    assert slugs == {"iceland-blue-lagoon", "maldives-overwater", "swiss-alps-hiking"}


def test_get_trips_filter_by_aurora_returns_multiple():
    """极光标签关联多个旅行地，应全部返回"""
    response = client.get("/api/trips?tag=aurora")
    assert response.status_code == 200

    data = response.json()
    assert data["total"] == 2
    for trip in data["items"]:
        assert any(t["slug"] == "aurora" for t in trip["tags"])


# ==================== Schema 字段对齐测试 ====================

def test_response_schema_fields_aligned():
    """响应字段必须与 schema-design.md 严格对齐"""
    response = client.get("/api/trips")
    assert response.status_code == 200

    data = response.json()
    trip = data["items"][0]

    required_fields = [
        "id", "name", "slug", "description", "emotion_description",
        "cover_image_url", "country", "region", "latitude", "longitude",
        "best_season", "is_featured", "tags", "created_at", "updated_at",
    ]
    for field in required_fields:
        assert field in trip, f"缺少字段: {field}"

    assert isinstance(trip["tags"], list)
    assert len(trip["tags"]) > 0
    tag = trip["tags"][0]
    for tag_field in ("id", "name", "slug", "color", "icon"):
        assert tag_field in tag, f"标签缺少字段: {tag_field}"


def test_is_featured_boolean_type():
    """is_featured 应为布尔类型"""
    response = client.get("/api/trips")
    data = response.json()

    for trip in data["items"]:
        assert isinstance(trip["is_featured"], bool)


def test_cover_image_url_not_empty():
    """cover_image_url 必须有值"""
    response = client.get("/api/trips")
    data = response.json()

    for trip in data["items"]:
        assert trip.get("cover_image_url")
        assert trip["cover_image_url"].startswith("http")


def test_latitude_longitude_are_float():
    """latitude 和 longitude 应为浮点数"""
    response = client.get("/api/trips")
    data = response.json()

    for trip in data["items"]:
        if trip.get("latitude") is not None:
            assert isinstance(trip["latitude"], float)
        if trip.get("longitude") is not None:
            assert isinstance(trip["longitude"], float)


def test_created_at_iso8601_format():
    """created_at 应为 ISO 8601 格式"""
    response = client.get("/api/trips")
    data = response.json()

    for trip in data["items"]:
        assert trip["created_at"].endswith("Z")
        assert "T" in trip["created_at"]


# ==================== 响应结构测试 ====================

def test_response_has_items_and_total():
    """响应体必须包含 items 和 total"""
    response = client.get("/api/trips")
    data = response.json()

    assert "items" in data
    assert "total" in data
    assert isinstance(data["items"], list)
    assert isinstance(data["total"], int)
    assert data["total"] == len(data["items"])


def test_total_matches_filtered_count():
    """total 应与 items 长度一致"""
    for tag in [None, "hotspring", "aurora", "nonexistent"]:
        url = "/api/trips" if tag is None else f"/api/trips?tag={tag}"
        response = client.get(url)
        data = response.json()
        assert data["total"] == len(data["items"])


# ==================== 数据一致性测试 ====================

def test_slug_is_unique():
    """所有旅行地的 slug 应唯一"""
    response = client.get("/api/trips")
    data = response.json()

    slugs = [trip["slug"] for trip in data["items"]]
    assert len(slugs) == len(set(slugs))


def test_emotion_description_not_empty():
    """emotion_description 不应为空"""
    response = client.get("/api/trips")
    data = response.json()

    for trip in data["items"]:
        assert trip.get("emotion_description")
        assert len(trip["emotion_description"]) > 0


def test_country_not_empty():
    """country 不应为空"""
    response = client.get("/api/trips")
    data = response.json()

    for trip in data["items"]:
        assert trip.get("country")
        assert len(trip["country"]) > 0


def test_best_season_not_empty():
    """best_season 不应为空"""
    response = client.get("/api/trips")
    data = response.json()

    for trip in data["items"]:
        assert trip.get("best_season")
        assert len(trip["best_season"]) > 0


def test_featured_trips_have_true_value():
    """精选旅行地的 is_featured 应为 True"""
    response = client.get("/api/trips")
    data = response.json()

    featured = [t for t in data["items"] if t["is_featured"]]
    non_featured = [t for t in data["items"] if not t["is_featured"]]
    assert len(featured) > 0
    assert len(non_featured) > 0
