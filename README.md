# stock_market_analysis

A UI to present stock data of listed market

### schedule

1. cashflow table
   - [x] crawl
   - [x] visualize
2. profit loss
   - [x] crawl
   - [x] visualize
3. asset debt
   - [x] crawl
   - [x] visualize
4. dividend
   - [x] crawl
   - [ ] visualize
5. stock price
   - [x] crawl history
   - [x] crawl real time
   - [x] visualize
6. recommandation
7. cascade django

### data

1. profit loss:

- 一般公司：
  - 營業收入 = 營業成本 + 營業毛利
  - 營業利益 = 營業收入 - 營業成本 - 營業費用
  - (稅前)淨利 = 營業收入 - 營業成本 - 營業費用 + 營業外收入及支出
  - 本期淨利 = 稅後淨利
  - 毛利率 ＝營業毛利/營業收入
- 銀行：
  - 營業收入 = 利息淨收益＋利息以外淨損益
  - 淨損 ＝營業收入 - 呆帳費用 - 營業費用
  - 沒有毛利
- 金控：
  - 營業收入＝淨收益 ＝利息淨收益＋利息以外淨收益
  - 沒有毛利
- 壽險:
  - 營業利益＝營業收入 - 營業成本 - 營業費用
  - 毛利率 ＝（營業收入-營業成本）/營業收入
- 其他：（可放棄）
  - 淨損 ＝ 收入 - 支出

2. cashflow table:

- 自由現金流: 營業淨現金流-資本支出（取得不動產）
- 淨現金流: 營業淨現金流-投資淨現金流+籌資淨現金流

3. asset debt:
- 權益總額 = 資產總額 - 負債總額

4. ROE (股東權益報酬）= 稅後淨利/權益總額
