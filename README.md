# NSE AI Trading Stack 🚀
### 7 AI Agents. Infinite Advantage.

A professional-grade automated trading system for the Indian Stock Market (NSE), powered by a multi-agent AI architecture.

![AI Trading Team](backend/docs/ai_trading_stack.png) <!-- Image reference placeholder -->

## 🤖 The AI Trading Team
Our system architecture is built around 7 specialized AI agents, as seen in the "AI Trading Stack" framework:

1.  **Agent 01: Market Analyst** - Scans markets for high-probability price action and technical setups.
2.  **Agent 02: News Analyst** - Real-time sentiment analysis from financial news and social media.
3.  **Agent 03: Risk Manager** - Intelligent position sizing and automated risk/reward validation.
4.  **Agent 04: Macro Analyst** - Monitors global economic indicators (CPI, Interest Rates, GDP).
5.  **Agent 05: Portfolio Manager** - Optimizes asset allocation and monitors real-time performance.
6.  **Agent 06: Execution Agent** - High-speed order execution via Dhan API with smart slippage control.
7.  **Agent 07: Strategy Agent** - The master "brain" that connects all insights to deliver the edge.

## 🌟 Key Features
- **NSE India Focus**: Optimized for Nifty, BankNifty, and liquid intraday stocks.
- **Intraday Intelligence**: Automated stock selection using real-time internet-sourced data.
- **Dhan Integration**: Native support for Dhan API for seamless execution.
- **Hybrid UI**: Combines a robust Flask backend with a modern Vite/React dashboard.
- **Paper & Live Trading**: Seamlessly switch between simulation and real-market execution.

## 🛠️ Project Structure
```
nse-ai-trading-stack/
├── backend/                # Flask Server & AI Logic
│   ├── agents/            # The 7 AI Agents
│   ├── modules/           # Core trading components (Dhan API, TA, Screener)
│   └── app.py             # Main entry point
├── frontend/               # React Dashboard (Vite)
├── scripts/                # Maintenance & Setup scripts
└── docs/                   # Documentation & Guides
```

## 🚀 Quick Start
1. **Setup Backend**:
   ```bash
   cd backend
   pip install -r requirements.txt
   python main.py
   ```
2. **Setup Frontend**:
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

## 📈 Roadmap
- [x] Consolidate legacy trading systems.
- [x] Implement Multi-Agent Architecture.
- [x] Add Web-based Stock Selection.
- [ ] Implement US Stock Market support (Phase 2).
- [ ] Deep reinforcement learning for the Strategy Agent.

---
*Disclaimer: Trading stocks involves significant risk. This tool is for educational purposes only. Always trade responsibly.*
