import streamlit as st
import matplotlib.pyplot as plt
import numpy as np

# 設定網頁標題與寬度
st.set_page_config(page_title="便當店損益平衡分析系統", layout="wide")
st.title("📊 餐飲門店損益平衡分析工具")
st.write("請在左側輸入營運數據，系統將自動即時計算並導出分析圖表。")

# --- 側邊欄：讓夥伴輸入數據 ---
st.sidebar.header("🛠️ 營運數據輸入")
price = st.sidebar.number_input("便當零售價 (元)", min_value=1, value=169)
cost_rate = st.sidebar.slider("食材成本率 (%)", min_value=10, max_value=90, value=45) / 100
rent = st.sidebar.number_input("每月房租 (元)", min_value=0, value=60000)
labor = st.sidebar.number_input("每月人事費用 (元)", min_value=0, value=180000)
other_fixed = st.sidebar.number_input("其他固定成本 (水電折舊等)", min_value=0, value=0)
target_profit_rate = st.sidebar.slider("目標淨利候選 (%)", min_value=0, max_value=50, value=10) / 100

# --- 核心邏輯計算 ---
fixed_cost = rent + labor + other_fixed  # 總固定成本
contribution_margin_rate = 1 - cost_rate # 邊際貢獻率
unit_contribution_margin = price * contribution_margin_rate # 單個便當貢獻額

# 1. 損益平衡點 (Break-even Point)
be_revenue = fixed_cost / contribution_margin_rate
be_volume = be_revenue / price

# 2. 目標淨利點
# 公式：營業額 = 固定成本 / (邊際貢獻率 - 目標淨利率)
if contribution_margin_rate > target_profit_rate:
    target_revenue = fixed_cost / (contribution_margin_rate - target_profit_rate)
    target_profit = target_revenue * target_profit_rate
    target_volume = target_revenue / price
else:
    target_revenue, target_profit, target_volume = 0, 0, 0

# --- 右側主畫面：數據看板 ---
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("損益平衡營業額", f"${be_revenue:,.0f} 元")
    st.caption(f"每月需賣出 {be_volume:,.0f} 個便當 (日均 {be_volume/26:.0f} 個，以26天計)")
with col2:
    st.metric(f"淨利 {target_profit_rate*100:.0f}% 所需營業額", f"${target_revenue:,.0f} 元")
    st.caption(f"每月需賣出 {target_volume:,.0f} 個便當 (日均 {target_volume/26:.0f} 個)")
with col3:
    st.metric(f"目標淨利金額", f"${target_profit:,.0f} 元")

st.markdown("---")

# --- 繪製圖表 ---
# 設定營業額 X 軸範圍 (上限抓目標營業額的 1.3 倍)
max_x = int(max(be_revenue, target_revenue) * 1.3) if max(be_revenue, target_revenue) > 0 else 500000
x_rev = np.linspace(0, max_x, 1000)

# 營運線：Y = X
y_rev = x_rev
# 固定成本線
y_fixed = np.full_like(x_rev, fixed_cost)
# 總成本線：Y = 固定成本 + X * 變動成本率
y_total_cost = fixed_cost + x_rev * cost_rate

# 開始畫圖 (支援中文設定)
plt.rcParams['font.sans-serif'] = ['Noto Sans TC', 'Arial Unicode MS', 'Arial'] # 針對 Windows 微軟正黑體
plt.rcParams['axes.unicode_minus'] = False

fig, ax = plt.subplots(figsize=(10, 6))
ax.plot(x_rev, y_rev, label="營業額線 (收入)", color="#0C59CF", linewidth=2)
ax.plot(x_rev, y_total_cost, label="總支出成本線 (固定+變動)", color="#D62728", linewidth=2)
ax.axhline(y=fixed_cost, color="purple", linestyle="--", label=f"固定成本線 ({fixed_cost:,.0f}元)")

# 標記打平點
if be_revenue <= max_x:
    ax.plot(be_revenue, be_revenue, 'ko')
    ax.axvline(x=be_revenue, color='gray', linestyle=':', alpha=0.7)
    ax.text(be_revenue, be_revenue * 1.05, f'損益平衡點\n${be_revenue:,.0f}', ha='center', color='black')

# 標記目標利潤點
if target_revenue <= max_x and target_revenue > 0:
    ax.plot(target_revenue, target_revenue, 'ko')
    ax.axvline(x=target_revenue, color='gray', linestyle=':', alpha=0.7)
    ax.text(target_revenue, target_revenue * 0.9, f'目標利潤點\n${target_revenue:,.0f}', ha='center', color='green')

# 區域著色 (賠錢 vs 賺錢)
ax.fill_between(x_rev, y_rev, y_total_cost, where=(x_rev < be_revenue), color='red', alpha=0.1, label='賠錢區域')
ax.fill_between(x_rev, y_rev, y_total_cost, where=(x_rev >= be_revenue), color='green', alpha=0.1, label='賺錢區域')

# 圖表細節設定
ax.set_title("損益平衡分析圖", fontsize=16, fontweight='bold')
ax.set_xlabel("營業額 (元)", fontsize=12)
ax.set_ylabel("支出成本 / 收入 (元)", fontsize=12)
ax.grid(True, linestyle=':', alpha=0.6)
ax.legend(loc="upper left")

# 在 Streamlit 網頁上渲染圖表
st.pyplot(fig)
