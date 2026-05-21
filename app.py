import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import urllib.request
import os

# 自動下載中文字型
font_path = "/tmp/NotoSansTC.ttf"
if not os.path.exists(font_path):
    urllib.request.urlretrieve(
        "https://github.com/googlefonts/noto-cjk/raw/main/Sans/OTF/TraditionalChinese/NotoSansCJKtc-Regular.otf",
        font_path
    )

from matplotlib import font_manager
font_manager.fontManager.addfont(font_path)
plt.rcParams['font.sans-serif'] = ['Noto Sans CJK TC', 'Arial']
plt.rcParams['axes.unicode_minus'] = False

# 設定網頁標題與寬度
st.set_page_config(page_title="便當店損益平衡分析系統", layout="wide")
st.title("📊 餐飲門店損益平衡分析工具")
st.write("請在左側輸入營運數據，系統將自動即時計算並導出分析圖表。")

# --- 側邊欄 ---
st.sidebar.header("🛠️ 營運數據輸入")

price = st.sidebar.number_input("便當零售價 (元)", min_value=1, value=169)
cost_rate = st.sidebar.slider("食材成本率 (%)", min_value=10, max_value=90, value=45) / 100
hq_fee_rate = st.sidebar.slider("總部費用率 (%)", min_value=0.0, max_value=10.0, value=0.0, step=0.5) / 100
delivery_fee_rate = st.sidebar.slider("外送費用率 (%)", min_value=0, max_value=20, value=0, step=1) / 100

st.sidebar.markdown("---")

rent = st.sidebar.number_input("每月房租 (元)", min_value=0, value=60000)
labor = st.sidebar.number_input("每月人事費用 (元)", min_value=0, value=180000)

st.sidebar.markdown("---")

# 水電費
utility = st.sidebar.number_input("每月水電費 (元)", min_value=0, value=0)

# 其他成本（可新增多筆）
st.sidebar.markdown("**其他成本**")
other_count = st.sidebar.number_input("其他成本筆數", min_value=0, max_value=5, value=1, step=1)
other_items = []
for i in range(int(other_count)):
    col_name, col_val = st.sidebar.columns([2, 1])
    with col_name:
        item_name = st.text_input(f"名稱 {i+1}", value=f"其他成本{i+1}", key=f"name_{i}")
    with col_val:
        item_val = st.number_input(f"金額", min_value=0, value=0, key=f"val_{i}")
    other_items.append((item_name, item_val))

st.sidebar.markdown("---")
target_profit_rate = st.sidebar.slider("目標淨利率 (%)", min_value=0, max_value=50, value=10) / 100

# --- 核心計算 ---
# 變動成本率 = 食材 + 總部費用 + 外送費用
variable_cost_rate = cost_rate + hq_fee_rate + delivery_fee_rate
contribution_margin_rate = 1 - variable_cost_rate

# 固定成本
other_fixed_total = sum(v for _, v in other_items)
fixed_cost = rent + labor + utility + other_fixed_total

# 損益平衡點
if contribution_margin_rate > 0:
    be_revenue = fixed_cost / contribution_margin_rate
    be_volume = be_revenue / price
else:
    be_revenue = 0
    be_volume = 0

# 目標淨利點
if contribution_margin_rate > target_profit_rate > 0 or (target_profit_rate == 0 and contribution_margin_rate > 0):
    if contribution_margin_rate > target_profit_rate:
        target_revenue = fixed_cost / (contribution_margin_rate - target_profit_rate)
        target_profit = target_revenue * target_profit_rate
        target_volume = target_revenue / price
    else:
        target_revenue, target_profit, target_volume = 0, 0, 0
else:
    target_revenue, target_profit, target_volume = 0, 0, 0

# --- 數據看板 ---
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("損益平衡營業額", f"${be_revenue:,.0f} 元")
    st.caption(f"每月需賣出 {be_volume:,.0f} 個便當（日均 {be_volume/26:.0f} 個，以26天計）")
with col2:
    st.metric(f"淨利 {target_profit_rate*100:.0f}% 所需營業額", f"${target_revenue:,.0f} 元")
    st.caption(f"每月需賣出 {target_volume:,.0f} 個便當（日均 {target_volume/26:.0f} 個）")
with col3:
    st.metric("目標淨利金額", f"${target_profit:,.0f} 元")

st.markdown("---")

# --- 成本結構明細 ---
st.subheader("📋 成本結構明細")

ref_revenue = target_revenue if target_revenue > 0 else be_revenue

detail_col1, detail_col2 = st.columns(2)

with detail_col1:
    st.markdown("**變動成本（佔營業額比例）**")
    st.write(f"- 食材成本率：{cost_rate*100:.1f}%")
    st.write(f"- 總部費用率：{hq_fee_rate*100:.1f}%")
    st.write(f"- 外送費用率：{delivery_fee_rate*100:.1f}%")
    st.write(f"- **合計變動成本率：{variable_cost_rate*100:.1f}%**")
    st.write(f"- **邊際貢獻率：{contribution_margin_rate*100:.1f}%**")

with detail_col2:
    st.markdown("**固定成本（每月）**")
    st.write(f"- 房租：${rent:,.0f} 元")
    st.write(f"- 人事費用：${labor:,.0f} 元")
    if ref_revenue > 0:
        utility_rate = (utility / ref_revenue * 100) if ref_revenue > 0 else 0
        st.write(f"- 水電費：${utility:,.0f} 元　（佔目標營收 {utility_rate:.1f}%）")
    else:
        st.write(f"- 水電費：${utility:,.0f} 元")
    for name, val in other_items:
        if val > 0:
            val_rate = (val / ref_revenue * 100) if ref_revenue > 0 else 0
            st.write(f"- {name}：${val:,.0f} 元　（佔目標營收 {val_rate:.1f}%）")
    st.write(f"- **固定成本合計：${fixed_cost:,.0f} 元**")

st.markdown("---")

# --- 圖表 ---
max_x = int(max(be_revenue, target_revenue) * 1.3) if max(be_revenue, target_revenue) > 0 else 500000
x_rev = np.linspace(0, max_x, 1000)

y_rev = x_rev
y_total_cost = fixed_cost + x_rev * variable_cost_rate

fig, ax = plt.subplots(figsize=(10, 6))
ax.plot(x_rev, y_rev, label="營業額線 (收入)", color="#0C59CF", linewidth=2)
ax.plot(x_rev, y_total_cost, label=f"總支出成本線 (固定+變動 {variable_cost_rate*100:.1f}%)", color="#D62728", linewidth=2)
ax.axhline(y=fixed_cost, color="purple", linestyle="--", label=f"固定成本線 ({fixed_cost:,.0f}元)")

if be_revenue > 0 and be_revenue <= max_x:
    ax.plot(be_revenue, be_revenue, 'ko')
    ax.axvline(x=be_revenue, color='gray', linestyle=':', alpha=0.7)
    ax.text(be_revenue, be_revenue * 1.05, f'損益平衡點\n${be_revenue:,.0f}', ha='center', color='black')

if target_revenue > 0 and target_revenue <= max_x:
    ax.plot(target_revenue, target_revenue, 'ko')
    ax.axvline(x=target_revenue, color='gray', linestyle=':', alpha=0.7)
    ax.text(target_revenue, target_revenue * 0.9, f'目標利潤點\n${target_revenue:,.0f}', ha='center', color='green')

ax.fill_between(x_rev, y_rev, y_total_cost, where=(x_rev < be_revenue), color='red', alpha=0.1, label='賠錢區域')
ax.fill_between(x_rev, y_rev, y_total_cost, where=(x_rev >= be_revenue), color='green', alpha=0.1, label='賺錢區域')

ax.set_title("損益平衡分析圖", fontsize=16, fontweight='bold')
ax.set_xlabel("營業額 (元)", fontsize=12)
ax.set_ylabel("支出成本 / 收入 (元)", fontsize=12)
ax.grid(True, linestyle=':', alpha=0.6)
ax.legend(loc="upper left")

st.pyplot(fig)
