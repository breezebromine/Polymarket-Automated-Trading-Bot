"""订单管理器"""

from typing import Dict, List
from loguru import logger

from ..data.models import Order, OrderStatus
from ..utils.exceptions import OrderExecutionError


class OrderManager:
    """订单管理"""

    def __init__(self):
        self.orders: Dict[str, Dict] = {}

    async def track_order(self, order: Dict):
        """
        跟踪订单

        Args:
            order: 订单信息
        """
        order_id = order.get('order_id')
        self.orders[order_id] = order
        logger.debug(f"跟踪订单: {order_id}")

    async def get_order(self, order_id: str) -> Dict:
        """获取订单信息"""
        return self.orders.get(order_id, {})

    async def get_open_orders(self) -> List[Dict]:
        """获取未成交订单"""
        return [
            order for order in self.orders.values()
            if order.get('status') in ['pending', 'submitted', 'partially_filled']
        ]

    async def update_order_status(self, order_id: str, status: str):
        """更新订单状态"""
        if order_id in self.orders:
            self.orders[order_id]['status'] = status
            logger.info(f"订单状态更新: {order_id} -> {status}")

    async def cancel_all_orders(self) -> List[str]:
        """取消所有未成交订单"""
        cancelled = []
        open_orders = await self.get_open_orders()

        for order in open_orders:
            order_id = order.get('order_id')
            # TODO: 调用API取消订单
            await self.update_order_status(order_id, 'cancelled')
            cancelled.append(order_id)

        logger.info(f"已取消 {len(cancelled)} 个订单")
        return cancelled
