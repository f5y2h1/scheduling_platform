"""
测试知识库文档入库功能
验证UI数字同步和向量数据同步
"""
import requests
import json

# 后端服务地址
BASE_URL = "http://localhost:8080/api"
LOGIN_URL = f"{BASE_URL}/auth/login"
DOCS_URL = f"{BASE_URL}/knowledge/documents"
STATS_URL = f"{BASE_URL}/knowledge/stats"

# 登录获取token
def login():
    response = requests.post(LOGIN_URL, json={
        "username": "admin",
        "password": "admin123"
    })
    if response.status_code == 200:
        data = response.json()
        # 尝试多种可能的token字段名
        token = (
            data.get("data", {}).get("access_token") or
            data.get("data", {}).get("accessToken") or
            data.get("access_token") or
            data.get("accessToken") or
            data.get("token")
        )
        if token:
            print(f"✓ 登录成功: {str(token)[:20]}...")
            return token
        else:
            print(f"✗ Token解析失败: {json.dumps(data, indent=2)[:200]}")
            return None
    else:
        print(f"✗ 登录失败: {response.status_code} - {response.text}")
        return None

# 获取统计信息
def get_stats(token):
    headers = {"Authorization": f"Bearer {token}"}
    try:
        response = requests.get(STATS_URL, headers=headers, timeout=5)
        if response.status_code == 200:
            data = response.json()
            stats = data.get("data", data)
            print(f"\n当前统计:")
            print(f"  知识文档: {stats.get('knowledge_count', stats.get('knowledgeCount', 0))}")
            print(f"  决策记录: {stats.get('decision_count', stats.get('decisionCount', 0))}")
            print(f"  业务规则: {stats.get('rule_count', stats.get('ruleCount', 0))}")
            print(f"  向量总数: {stats.get('total_vectors', stats.get('totalVectors', 0))}")
            return stats
        else:
            print(f"✗ 获取统计失败: {response.status_code} - {response.text}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"✗ 请求失败: {e}")
        return None

# 入库文档
def add_document(token, title, content, category="测试"):
    headers = {"Authorization": f"Bearer {token}"}
    payload = {
        "title": title,
        "content": content,
        "category": category,
        "tags": ["测试标签"],
        "source": "测试脚本"
    }
    print(f"\n入库文档: {title}")
    response = requests.post(f"{DOCS_URL}/advanced", json=payload, headers=headers)
    if response.status_code == 200:
        data = response.json()
        result = data.get("data", data)
        print(f"✓ 入库成功: {result.get('message')}")
        print(f"  文档ID: {result.get('doc_id')}")
        print(f"  分块数: {result.get('chunks')}")
        print(f"  平均质量: {result.get('avg_quality')}")
        return True
    else:
        print(f"✗ 入库失败: {response.status_code} - {response.text}")
        return False

# 获取文档列表
def list_documents(token):
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(DOCS_URL, headers=headers)
    if response.status_code == 200:
        data = response.json()
        docs = data.get("data", {}).get("documents", data.get("documents", []))
        print(f"\n文档列表: {len(docs)} 个文档")
        for i, doc in enumerate(docs[:3], 1):
            print(f"  {i}. {doc.get('title')} ({doc.get('category')}) - {doc.get('chunk_count')} 块")
        return docs
    else:
        print(f"✗ 获取文档列表失败: {response.status_code} - {response.text}")
        return []

def main():
    print("=" * 50)
    print("知识库文档入库测试")
    print("=" * 50)

    # 1. 登录
    token = login()
    if not token:
        return

    # 2. 获取初始统计
    initial_stats = get_stats(token)

    # 3. 入库测试文档
    test_docs = [
        {
            "title": "安全库存测试文档1",
            "content": """## 安全库存计算
安全库存 = Z × σ × √LT

其中：
- Z值：服务水平系数
- σ：需求标准差
- LT：提前期

示例计算：
Z=1.96 (97.5%服务水平)
σ=100
LT=7天
安全库存 = 1.96 × 100 × √7 = 518""",
            "category": "库存策略"
        },
        {
            "title": "调度规则测试文档2",
            "content": """## 调度优先级
1. 时效优先原则
   - 承诺时效订单优先
   - 覆盖率低于3天优先
   
2. 成本优化原则
   - 同向订单合并
   - 满载率最大化

3. 库存均衡原则
   - 避免单仓过度消耗
   - 考虑区域库存分布""",
            "category": "调度规则"
        }
    ]

    success_count = 0
    for i, doc_data in enumerate(test_docs, 1):
        if add_document(token, doc_data["title"], doc_data["content"], doc_data["category"]):
            success_count += 1

    # 4. 获取更新后的统计
    print("\n" + "=" * 50)
    print("验证UI数字同步:")
    print("=" * 50)
    updated_stats = get_stats(token)

    # 5. 获取文档列表
    print("\n" + "=" * 50)
    print("验证文档列表同步:")
    print("=" * 50)
    documents = list_documents(token)

    # 6. 验证结果
    print("\n" + "=" * 50)
    print("测试结果汇总:")
    print("=" * 50)
    print(f"✓ 入库成功: {success_count}/{len(test_docs)}")
    print(f"✓ 向量总数: {initial_stats.get('total_vectors', 0)} → {updated_stats.get('total_vectors', 0)}")
    print(f"✓ 文档数量: {len(documents)}")

    # 验证向量总数是否正确增加
    vector_diff = updated_stats.get('total_vectors', 0) - initial_stats.get('total_vectors', 0)
    if vector_diff > 0:
        print(f"✓ 向量数据同步正常: 增加 {vector_diff} 个向量")
    else:
        print(f"✗ 向量数据同步失败: 未检测到新增向量")

    # 验证文档列表是否包含新文档
    doc_titles = [d.get('title') for d in documents]
    new_doc_found = any(doc["title"] in doc_titles for doc in test_docs)
    if new_doc_found:
        print(f"✓ 文档列表同步正常: 找到新入库的文档")
    else:
        print(f"✗ 文档列表同步失败: 未找到新入库的文档")

if __name__ == "__main__":
    main()