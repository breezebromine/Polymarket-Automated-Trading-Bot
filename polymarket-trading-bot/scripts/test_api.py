"""测试Polymarket API连接"""
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from py_clob_client.client import ClobClient

def test_api():
    """测试API连接"""
    try:
        print("=" * 60)
        print("测试Polymarket API连接")
        print("=" * 60)

        # 创建客户端
        client = ClobClient("https://clob.polymarket.com")
        print("✓ 客户端创建成功")

        # 测试获取市场
        print("\n尝试获取市场列表...")
        try:
            markets = client.get_markets()
            print(f"✓ 成功获取 {len(markets) if markets else 0} 个市场")

            if markets and len(markets) > 0:
                print("\n前3个市场:")
                for i, market in enumerate(markets[:3], 1):
                    print(f"{i}. {market.get('question', 'N/A')}")
                    print(f"   ID: {market.get('condition_id', 'N/A')}")

        except Exception as e:
            print(f"✗ 获取市场失败: {type(e).__name__}: {e}")
            print(f"错误详情: {repr(e)}")

        print("\n" + "=" * 60)

    except Exception as e:
        print(f"✗ 客户端创建失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_api()
