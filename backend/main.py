import sqlite3
import json
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Vibe Trip API")

# 保持 CORS 开启，允许前端 index.html 跨域请求
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db_connection():
    """建立与 SQLite 数据库的连接"""
    conn = sqlite3.connect("trips.db")
    # 让查询返回的数据可以像字典一样通过列名访问（非常重要）
    conn.row_factory = sqlite3.Row
    return conn

def get_trips(tag: str | None = None) -> list[dict]:
    """核心查询逻辑：从真实数据库读取并解析数据"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        if tag:
            # 这里的巧妙之处：由于 tags 在 SQLite 里存的是 JSON 字符串
            # 我们可以用 LIKE 模糊匹配 slug 值，比如 '%"hotspring"%'
            query = "SELECT * FROM trips WHERE tags LIKE ?"
            cursor.execute(query, (f'%"{tag}"%',))
        else:
            # 没有传标签，直接返回所有数据
            query = "SELECT * FROM trips"
            cursor.execute(query)
            
        rows = cursor.fetchall()
        
        trips = []
        for row in rows:
            trip_dict = dict(row)
            # 关键步骤：把数据库里的 tags (字符串) 重新解析为前端需要的 JSON 列表
            if isinstance(trip_dict.get("tags"), str):
                try:
                    trip_dict["tags"] = json.loads(trip_dict["tags"])
                except json.JSONDecodeError:
                    trip_dict["tags"] = []
            trips.append(trip_dict)
            
        return trips
    finally:
        # 确保哪怕发生异常也会关闭数据库连接
        conn.close()

@app.get("/api/trips")
def list_trips(tag: str | None = Query(None)) -> dict:
    trips = get_trips(tag=tag)
    return {"items": trips, "total": len(trips)}

if __name__ == "__main__":
    import uvicorn
    # 为了方便你直接 python main.py 启动
    uvicorn.run(app, host="127.0.0.1", port=8080)
