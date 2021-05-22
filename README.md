# stock_market_analysis

A UI to present stock data of listed market

### schedule

1. cashflow table
   - [ ] crawl
   - [x] visualize
2. profit loss
   - [ ] crawl
   - [ ] visualize
3. asset debt
   - [ ] crawl
   - [ ] visualize
4. dividend
   - [x] crawl
   - [ ] visualize
5. stock price
   - [ ] crawl history
   - [ ] crawl real time
   - [ ] visualize
6. recommandation
7. cascade django

### data

1. profit_loss:

- 一般公司：
  - 營業收入 = 營業成本 + 營業毛利
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
