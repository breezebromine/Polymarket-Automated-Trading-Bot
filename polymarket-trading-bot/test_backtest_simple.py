"""简化的回测演示 - 特朗普竞选市场"""
import sys
from datetime import datetime, timedelta
import random

print("=" * 60)
print("🔬 Polymarket套利策略回测")
print("=" * 60)
print("市场: 特朗普2024竞选是否成功")
print("时间: 2024-01-01 至 2024-11-05 (选举日)")
print("策略: YES/NO价格不平衡套利")
print("=" * 60)

# 生成模拟数据
start = datetime(2024, 1, 1)
end = datetime(2024, 11, 5)
data_points = []

current = start
base_yes = 0.50  # 初始50%概率

while current <= end:
    # 模拟价格波动
    base_yes += random.uniform(-0.05, 0.05)
    base_yes = max(0.2, min(0.8, base_yes))
    
    # 15%概率出现套利机会
    if random.random() < 0.15:
        yes_price = base_yes + random.uniform(-0.03, 0.03)
        no_price = (1.0 - base_yes) + random.uniform(-0.03, 0.03)
        yes_price = max(0.01, min(0.99, yes_price))
        no_price = max(0.01, min(0.99, no_price))
    else:
        yes_price = base_yes
        no_price = 1.0 - base_yes
    
    data_points.append({
        'timestamp': current,
        'yes_price': yes_price,
        'no_price': no_price,
        'total': yes_price + no_price
    })
    
    current += timedelta(hours=1)

print(f"✓ 生成了 {len(data_points)} 个数据点")
print("-" * 60)

# 统计套利机会
arb_opportunities = sum(1 for d in data_points if abs(d['total'] - 1.0) > 0.02)
print(f"潜在套利机会: {arb_opportunities} 次 ({arb_opportunities/len(data_points)*100:.1f}%)")
print("-" * 60)

# 回测
initial_balance = 10000
balance = initial_balance
trades = 0
winning_trades = 0
total_pnl = 0

print("开始回测...")
print(f"初始资金: ${initial_balance:,.2f}")
print("-" * 60)

for data in data_points:
    yes_price = data['yes_price']
    no_price = data['no_price']
    total_price = data['total']
    spread = abs(1.0 - total_price)
    
    # 检测套利机会 (价差>2%且考虑0.1%手续费后仍有利润)
    fee_rate = 0.001
    net_spread = spread - (fee_rate * 2)
    
    if net_spread > 0.02 and balance > 200:  # 最小价差2%
        # 执行套利交易
        trade_size = min(100, balance * 0.1)
        
        # 成本计算
        yes_cost = (trade_size / 2) * yes_price
        no_cost = (trade_size / 2) * no_price
        total_cost = yes_cost + no_cost
        fee = total_cost * fee_rate * 2
        
        # 利润(假设收敛到1.0)
        profit = trade_size - total_cost - fee
        
        if profit > 0:
            balance += profit
            total_pnl += profit
            trades += 1
            winning_trades += 1
            
            if trades <= 5:
                print(f"交易 #{trades}: YES={yes_price:.3f} NO={no_price:.3f} "
                      f"价差={spread:.3f} 利润=${profit:.2f} 余额=${balance:.2f}")

# 结果
print("-" * 60)
print("=" * 60)
print("回测结果")
print("=" * 60)
print(f"初始资金:     ${initial_balance:,.2f}")
print(f"最终资金:     ${balance:,.2f}")
print(f"总收益:       ${total_pnl:,.2f}")
print(f"收益率:       {(balance-initial_balance)/initial_balance*100:.2f}%")
print("-" * 60)
print(f"总交易次数:   {trades}")
print(f"盈利次数:     {winning_trades}")
print(f"胜率:         {winning_trades/trades*100 if trades>0 else 0:.2f}%")
print(f"平均盈利:     ${total_pnl/trades if trades>0 else 0:.2f}")
print("=" * 60)
