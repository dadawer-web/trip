"""
Vibe Trip E2E 测试 — Playwright (Python)
=========================================
测试目标：验证前端筛选栏点击后，旅行卡片列表能正确过滤并渲染。

运行前请确保已安装依赖：
    pip install playwright pytest
    playwright install chromium

运行方式：
    pytest e2e_test.py -v
    # 或带浏览器可视化调试
    pytest e2e_test.py -v --headed --slowmo 500
"""

import subprocess
import sys
import time
from pathlib import Path

import pytest
from playwright.sync_api import Page, expect, sync_playwright

# ============================================
# 常量配置
# ============================================
# index.html 位于项目根目录，backend 是其子目录
PROJECT_ROOT = Path(__file__).resolve().parent.parent
INDEX_PATH = PROJECT_ROOT / "index.html"

# 本地静态服务器配置
SERVER_HOST = "127.0.0.1"
SERVER_PORT = 8765
BASE_URL = f"http://{SERVER_HOST}:{SERVER_PORT}"

# 测试中使用的真实标签（index.html mock 数据里存在的）
# "治愈" 仅出现在「京都岚山竹林」这一张卡片中，
# 点击后卡片数量应从 5 变为 1，变化最明显，适合断言。
TARGET_TAG_NAME = "治愈"
TARGET_TAG_SLUG = "healing"
EXPECTED_TRIP_NAME = "京都岚山竹林"


# ============================================
# Fixtures
# ============================================

@pytest.fixture(scope="session")
def http_server():
    """
    启动一个本地静态文件服务器，为 index.html 提供 HTTP 访问。
    测试结束后自动关闭进程。
    """
    if not INDEX_PATH.exists():
        raise FileNotFoundError(f"找不到 index.html: {INDEX_PATH}")

    proc = subprocess.Popen(
        [sys.executable, "-m", "http.server", str(SERVER_PORT), "--bind", SERVER_HOST],
        cwd=PROJECT_ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    # 等待服务器就绪（简单轮询）
    for _ in range(50):
        import socket

        try:
            with socket.create_connection((SERVER_HOST, SERVER_PORT), timeout=0.1):
                break
        except OSError:
            time.sleep(0.05)
    else:
        proc.terminate()
        raise RuntimeError("本地 HTTP 服务器启动超时")

    yield f"http://{SERVER_HOST}:{SERVER_PORT}"

    proc.terminate()
    try:
        proc.wait(timeout=5)
    except subprocess.TimeoutExpired:
        proc.kill()


@pytest.fixture
def page(http_server):
    """
    为每个测试用例启动一个新的浏览器页面实例，
    测试结束后自动关闭。
    """
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1280, "height": 800})
        pg = context.new_page()
        yield pg
        context.close()
        browser.close()


# ============================================
# 辅助函数
# ============================================

def get_trip_card_count(page: Page) -> int:
    """获取当前页面中旅行卡片的数量。"""
    return page.locator("#tripsGrid article.trip-card").count()


def get_trip_card_titles(page: Page) -> list[str]:
    """获取当前所有可见旅行卡片的标题文本。"""
    return page.locator("#tripsGrid article.trip-card h3").all_text_contents()


# ============================================
# E2E 测试用例
# ============================================

def test_filter_by_tag_updates_card_list(page: Page, http_server: str):
    """
    端到端场景：用户打开首页 → 点击顶部筛选栏的「治愈」标签 →
    验证卡片列表从全部（5张）过滤为仅含该标签的旅行地（1张），
    且正确渲染了对应数据。
    """
    # ----------------------------------------
    # 1. 打开首页并等待初始渲染完成
    # ----------------------------------------
    page.goto(http_server)

    # 等待筛选按钮容器和至少一张卡片出现，确保 JS 初始化完毕
    page.wait_for_selector("#filterContainer .filter-btn", state="visible")
    page.wait_for_selector("#tripsGrid article.trip-card", state="visible")

    # ----------------------------------------
    # 2. 记录初始状态（未筛选时的卡片数量与标题）
    # ----------------------------------------
    initial_count = get_trip_card_count(page)
    initial_titles = get_trip_card_titles(page)

    # 根据 mock 数据，初始应展示全部 5 张卡片
    assert initial_count == 5, f"初始卡片数量应为 5，实际为 {initial_count}"

    # ----------------------------------------
    # 3. 定位并点击「治愈」筛选按钮
    # ----------------------------------------
    # 筛选按钮的 data-filter 属性对应标签 slug，文本内容包含图标和名称
    target_button = page.locator(f"#filterContainer .filter-btn[data-filter='{TARGET_TAG_SLUG}']")

    # 断言按钮存在且可见
    expect(target_button).to_be_visible()
    expect(target_button).to_contain_text(TARGET_TAG_NAME)

    # 点击按钮触发过滤
    target_button.click()

    # 等待卡片网格重新渲染（动画约 0.6s，这里给足余量）
    page.wait_for_timeout(800)

    # ----------------------------------------
    # 4. 验证卡片数量发生了变化（从 5 变为 1）
    # ----------------------------------------
    filtered_count = get_trip_card_count(page)
    filtered_titles = get_trip_card_titles(page)

    assert filtered_count != initial_count, (
        f"点击筛选后卡片数量应发生变化，但前后均为 {filtered_count}"
    )
    assert filtered_count == 1, (
        f"「{TARGET_TAG_NAME}」标签应只匹配 1 张卡片，实际为 {filtered_count}"
    )

    # ----------------------------------------
    # 5. 验证渲染的数据正确（标题、标签、情绪文案）
    # ----------------------------------------
    assert filtered_titles == [EXPECTED_TRIP_NAME], (
        f"过滤后卡片标题应为 ['{EXPECTED_TRIP_NAME}']，实际为 {filtered_titles}"
    )

    # 断言卡片内部包含正确的标签 pill
    card = page.locator("#tripsGrid article.trip-card").first
    tag_pill = card.locator(".tag-pill").filter(has_text=TARGET_TAG_NAME)
    expect(tag_pill).to_be_visible()

    # 断言情绪描述文案正确渲染
    emotion_text = card.locator(".emotion-text")
    expect(emotion_text).to_contain_text("穿越千年的绿色隧道，让风带走所有喧嚣")

    # ----------------------------------------
    # 6. 额外验证：切换回「全部」应恢复初始状态
    # ----------------------------------------
    all_button = page.locator("#filterContainer .filter-btn[data-filter='all']")
    all_button.click()
    page.wait_for_timeout(800)

    restored_count = get_trip_card_count(page)
    restored_titles = get_trip_card_titles(page)

    assert restored_count == initial_count, (
        f"切回「全部」后卡片数量应恢复为 {initial_count}，实际为 {restored_count}"
    )
    assert set(restored_titles) == set(initial_titles), (
        "切回「全部」后卡片标题列表应与初始状态一致"
    )
