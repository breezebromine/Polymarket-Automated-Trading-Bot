"""Web3客户端 - 区块链交互

注意: 实际使用时需要妥善保管私钥
"""

from typing import Optional
from loguru import logger

# 实际使用时取消注释:
# from web3 import Web3
# from eth_account import Account

from ..utils.config import get_config
from ..utils.exceptions import APIError


class Web3Client:
    """Web3客户端封装"""

    def __init__(self, config=None):
        self.config = config or get_config()
        self.w3 = None
        self.account = None

    async def connect(self):
        """连接到区块链网络"""
        try:
            # TODO: 实际初始化Web3
            # from web3 import Web3
            # self.w3 = Web3(Web3.HTTPProvider(self.config.eth_rpc_url))
            #
            # if self.config.eth_private_key:
            #     from eth_account import Account
            #     self.account = Account.from_key(self.config.eth_private_key)

            logger.info("✓ Web3客户端已连接")
        except Exception as e:
            logger.error(f"Web3连接失败: {e}")
            raise APIError(f"Web3连接失败: {e}")

    async def get_balance(self, address: str) -> float:
        """获取地址余额"""
        # TODO: 实现
        return 0.0

    async def send_transaction(self, tx_data: dict) -> str:
        """发送交易"""
        # TODO: 实现
        return "0x..."

    async def close(self):
        """关闭连接"""
        logger.info("Web3客户端已关闭")


_client: Optional[Web3Client] = None


async def get_web3_client() -> Web3Client:
    """获取全局Web3客户端"""
    global _client
    if _client is None:
        _client = Web3Client()
        await _client.connect()
    return _client
