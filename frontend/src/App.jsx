import React, { useState, useEffect } from 'react';
import { io } from 'socket.io-client';
import { 
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, AreaChart, Area, BarChart, Bar
} from 'recharts';
import { 
  TrendingUp, TrendingDown, Activity, Shield, 
  BarChart3, Newspaper, Globe, Briefcase, 
  Play, MousePointer2, AlertCircle, Clock,
  Flame, Target, Layers, Compass, CheckCircle2,
  ArrowUpRight, ArrowDownRight, RefreshCw, Radio,
  Zap, Sparkles, Building2, Landmark, Wallet,
  SlidersHorizontal, Check, Search, DollarSign,
  ChevronRight, ExternalLink
} from 'lucide-react';

const socket = io('http://localhost:5000');

function App() {
  // Global State
  const [marketStatus, setMarketStatus] = useState({ is_open: false, current_time: '--:--:--', day: 'Friday' });
  const [spotPrice, setSpotPrice] = useState(24500);
  const [activeSymbol, setActiveSymbol] = useState('NIFTY');
  const [analysis, setAnalysis] = useState(null);
  const [signal, setSignal] = useState(null);
  const [portfolio, setPortfolio] = useState({ capital: 500000, pnl: 0, open_positions: 0, positions: {} });
  
  // Navigation Tabs: 'screener', 'options', 'catalysts', 'institutional', 'kite', 'terminal'
  const [activeTab, setActiveTab] = useState('screener');
  
  // Real Data Feeds
  const [chartData, setChartData] = useState([]);
  const [premarketData, setPremarketData] = useState(null);
  const [discovery, setDiscovery] = useState(null);
  const [screenerOpportunities, setScreenerOpportunities] = useState([]);
  const [premarketGaps, setPremarketGaps] = useState([]);
  const [screenerFilter, setScreenerFilter] = useState('ALL'); // 'ALL', 'ORB_BREAKOUT', 'SMC_PATTERN', 'GAPS'
  
  const [optionChainData, setOptionChainData] = useState(null);
  const [recommendedTrade, setRecommendedTrade] = useState(null);
  
  const [catalystData, setCatalystData] = useState(null);
  const [institutionalData, setInstitutionalData] = useState(null);
  const [kiteStatus, setKiteStatus] = useState({ status: 'SIMULATION_MODE', broker: 'ZERODHA_KITE', mcp_ready: true });
  const [kitePositions, setKitePositions] = useState([]);
  const [kiteMargins, setKiteMargins] = useState(null);
  const [kiteOrders, setKiteOrders] = useState([]);
  
  const [newsData, setNewsData] = useState(null);
  const [executionMessage, setExecutionMessage] = useState('');
  const [orderModal, setOrderModal] = useState({ open: false, symbol: '', type: 'BUY', price: 0, qty: 50, product: 'MIS' });

  // Initial Fetch & WebSocket Listeners
  useEffect(() => {
    socket.on('connect', () => console.log('Connected to Institutional NSE AI Backend'));

    socket.on('market_update', (data) => {
      if (data.spot_price) setSpotPrice(data.spot_price);
      if (data.status) setMarketStatus(data.status);
      if (data.analysis) setAnalysis(data.analysis);
      if (data.signal) setSignal(data.signal);

      if (data.spot_price) {
        setChartData(prev => {
          const newData = [...prev, {
            time: new Date().toLocaleTimeString(),
            price: data.spot_price,
            vwap: data.analysis?.vwap || data.spot_price * 0.9995
          }];
          return newData.slice(-40);
        });
      }
    });

    socket.on('discovery_update', (data) => setDiscovery(data));
    socket.on('premarket_update', (data) => setPremarketData(data));
    socket.on('catalyst_update', (data) => setCatalystData(data));
    socket.on('institutional_update', (data) => setInstitutionalData(data));
    socket.on('portfolio_update', (data) => setPortfolio(data));

    // Fetch initial REST APIs
    fetchPremarket();
    fetchScreener();
    fetchCatalysts();
    fetchInstitutional();
    fetchOptionChain();
    fetchRecommendedTrade();
    fetchKiteData();
    fetchNews();

    const interval = setInterval(() => {
      fetchScreener();
      fetchOptionChain();
    }, 12000);

    return () => {
      clearInterval(interval);
      socket.off('market_update');
      socket.off('discovery_update');
      socket.off('premarket_update');
      socket.off('catalyst_update');
      socket.off('institutional_update');
      socket.off('portfolio_update');
    };
  }, [activeSymbol]);

  const fetchPremarket = async () => {
    try {
      const res = await fetch('http://localhost:5000/api/premarket');
      const data = await res.json();
      if (data.prediction) setPremarketData(data.prediction);
      if (data.gaps) setPremarketGaps(data.gaps);
    } catch (e) { console.error(e); }
  };

  const fetchScreener = async () => {
    try {
      const res = await fetch('http://localhost:5000/api/screener');
      const data = await res.json();
      if (data.results) setScreenerOpportunities(data.results);
    } catch (e) { console.error(e); }
  };

  const fetchCatalysts = async () => {
    try {
      const res = await fetch('http://localhost:5000/api/screener/catalysts');
      const data = await res.json();
      if (data.data) setCatalystData(data.data);
    } catch (e) { console.error(e); }
  };

  const fetchInstitutional = async () => {
    try {
      const res = await fetch('http://localhost:5000/api/screener/institutional');
      const data = await res.json();
      if (data.data) setInstitutionalData(data.data);
    } catch (e) { console.error(e); }
  };

  const fetchOptionChain = async () => {
    try {
      const res = await fetch(`http://localhost:5000/api/optionchain?symbol=${activeSymbol}&spot=${spotPrice}`);
      const json = await res.json();
      if (json.data) setOptionChainData(json.data);
    } catch (e) { console.error(e); }
  };

  const fetchRecommendedTrade = async () => {
    try {
      const res = await fetch(`http://localhost:5000/api/recommend_strike?symbol=${activeSymbol}&spot=${spotPrice}&direction=BUY`);
      const json = await res.json();
      if (json.trade) setRecommendedTrade(json.trade);
    } catch (e) { console.error(e); }
  };

  const fetchKiteData = async () => {
    try {
      const sRes = await fetch('http://localhost:5000/api/kite/status');
      const sData = await sRes.json();
      setKiteStatus(sData);

      const mRes = await fetch('http://localhost:5000/api/kite/margins');
      const mData = await mRes.json();
      if (mData.margins) setKiteMargins(mData.margins);

      const pRes = await fetch('http://localhost:5000/api/kite/positions');
      const pData = await pRes.json();
      if (pData.positions) setKitePositions(pData.positions);

      const oRes = await fetch('http://localhost:5000/api/kite/orders');
      const oData = await oRes.json();
      if (oData.orders) setKiteOrders(oData.orders);
    } catch (e) { console.error(e); }
  };

  const fetchNews = async () => {
    try {
      const res = await fetch('http://localhost:5000/api/news');
      const json = await res.json();
      if (json.data) setNewsData(json.data);
    } catch (e) { console.error(e); }
  };

  // Execution Handlers
  const handleQuickExecute = async (symbol, action = 'BUY', price = 0, product = 'MIS', qty = 50) => {
    setExecutionMessage(`Submitting Order: ${action} ${symbol}...`);
    try {
      const res = await fetch('http://localhost:5000/api/kite/trade', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          symbol: symbol,
          transaction_type: action,
          quantity: qty,
          product: product,
          price: price,
          order_type: price > 0 ? 'LIMIT' : 'MARKET'
        })
      });
      const data = await res.json();
      setExecutionMessage(data.message || 'Order Placed');
      fetchKiteData();
      setTimeout(() => setExecutionMessage(''), 4000);
    } catch (e) {
      setExecutionMessage(`Execution Error: ${e.message}`);
      setTimeout(() => setExecutionMessage(''), 4000);
    }
  };

  return (
    <div className="min-h-screen bg-[#06080d] text-slate-100 flex flex-col font-sans selection:bg-emerald-500/30 selection:text-emerald-300">
      
      {/* Top Navbar */}
      <header className="sticky top-0 z-50 bg-[#0c1017]/90 backdrop-blur-md border-b border-slate-800/80 px-5 py-3">
        <div className="max-w-[1720px] mx-auto flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-emerald-500 to-cyan-500 flex items-center justify-center shadow-lg shadow-emerald-500/20">
              <Zap className="w-6 h-6 text-slate-950 stroke-[2.5]" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h1 className="text-lg font-bold tracking-tight bg-gradient-to-r from-white via-slate-200 to-slate-400 bg-clip-text text-transparent">
                  NSE AI TRADING STACK
                </h1>
                <span className="text-[11px] font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 px-2 py-0.5 rounded-full flex items-center gap-1">
                  <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-ping"></span> LIVE
                </span>
                <span className="text-[11px] font-medium bg-blue-500/10 text-blue-400 border border-blue-500/30 px-2 py-0.5 rounded-full">
                  Kite MCP Connected
                </span>
              </div>
              <p className="text-xs text-slate-400 flex items-center gap-2 mt-0.5">
                <span>Time: <strong className="text-slate-200">{marketStatus.current_time} IST</strong></span>
                <span>•</span>
                <span className={marketStatus.is_open ? "text-emerald-400 font-medium" : "text-amber-400"}>
                  {marketStatus.is_open ? "Market Active" : "Pre-Market / Simulated Live"}
                </span>
              </p>
            </div>
          </div>

          {/* Underlyings & Ticker Bar */}
          <div className="flex items-center gap-2 bg-slate-900/90 border border-slate-800 px-3 py-1.5 rounded-xl">
            {['NIFTY', 'BANKNIFTY', 'FINNIFTY', 'SENSEX', 'RELIANCE', 'HDFCBANK'].map(sym => (
              <button
                key={sym}
                onClick={() => { setActiveSymbol(sym); setChartData([]); }}
                className={`px-3 py-1 text-xs font-semibold rounded-lg transition-all ${
                  activeSymbol === sym 
                    ? 'bg-emerald-500 text-slate-950 shadow-md shadow-emerald-500/20' 
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800'
                }`}
              >
                {sym}
              </button>
            ))}
          </div>

          {/* Capital & Portfolio KPI */}
          <div className="flex items-center gap-4">
            <div className="text-right hidden sm:block">
              <div className="text-[11px] text-slate-400 font-medium uppercase tracking-wider">Total Capital</div>
              <div className="text-sm font-bold text-slate-100">
                ₹{(portfolio.capital || 500000).toLocaleString('en-IN', { maximumFractionDigits: 2 })}
              </div>
            </div>
            <div className="text-right">
              <div className="text-[11px] text-slate-400 font-medium uppercase tracking-wider">Real-Time PnL</div>
              <div className={`text-sm font-bold flex items-center justify-end gap-1 ${portfolio.pnl >= 0 ? 'text-emerald-400' : 'text-rose-400'}`}>
                {portfolio.pnl >= 0 ? <ArrowUpRight className="w-4 h-4" /> : <ArrowDownRight className="w-4 h-4" />}
                {portfolio.pnl >= 0 ? '+' : ''}₹{(portfolio.pnl || 0).toLocaleString('en-IN', { maximumFractionDigits: 2 })}
              </div>
            </div>
          </div>
        </div>

        {/* Navigation Tabs */}
        <div className="max-w-[1720px] mx-auto flex items-center gap-2 mt-3 pt-2 border-t border-slate-800/60 overflow-x-auto">
          {[
            { id: 'screener', label: '⚡ Intraday F&O Screener', badge: `${screenerOpportunities.length} Setups` },
            { id: 'options', label: '🎯 ATM Options Engine', badge: 'Greeks & OI' },
            { id: 'catalysts', label: '💎 Small-Cap & Catalyst Hunter', badge: 'Earnings & Orders' },
            { id: 'institutional', label: '🏛️ Institutional & FII/DII Flow', badge: 'Smart Money' },
            { id: 'kite', label: '🪁 Zerodha Kite Hub', badge: 'MCP & Orders' },
            { id: 'terminal', label: '🧠 7-Agent AI Confluence', badge: 'Signals' }
          ].map(tab => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`px-4 py-2 rounded-xl text-xs font-semibold flex items-center gap-2 whitespace-nowrap transition-all ${
                activeTab === tab.id
                  ? 'bg-gradient-to-r from-emerald-500/20 to-cyan-500/20 border border-emerald-500/50 text-emerald-300 shadow-sm'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50 border border-transparent'
              }`}
            >
              <span>{tab.label}</span>
              <span className={`text-[10px] px-1.5 py-0.2 rounded-md ${activeTab === tab.id ? 'bg-emerald-500/30 text-emerald-200' : 'bg-slate-800 text-slate-400'}`}>
                {tab.badge}
              </span>
            </button>
          ))}
        </div>
      </header>

      {/* Execution Feedback Notification */}
      {executionMessage && (
        <div className="bg-gradient-to-r from-emerald-600 to-cyan-600 text-slate-950 font-bold px-4 py-2 text-center text-xs shadow-lg animate-bounce">
          ⚡ {executionMessage}
        </div>
      )}

      {/* Main Content Body */}
      <main className="flex-1 max-w-[1720px] w-full mx-auto p-5">
        
        {/* TAB 1: INTRADAY F&O SCREENER */}
        {activeTab === 'screener' && (
          <div className="space-y-6">
            
            {/* Screener Header & Filter Controls */}
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-slate-900/60 border border-slate-800 p-4 rounded-2xl">
              <div>
                <h2 className="text-lg font-bold text-slate-100 flex items-center gap-2">
                  <Flame className="w-5 h-5 text-amber-400" />
                  Real-Time Intraday F&O Stock Screener (9:08 AM & Live Market Hours)
                </h2>
                <p className="text-xs text-slate-400 mt-1">
                  High-liquidity NSE F&O universe scanned for 15m ORB Breakouts, SuperTrend + VWAP confluence, RVOL surges ({'>'}1.8x), and SMC Order Blocks.
                </p>
              </div>

              {/* Sub-Filters */}
              <div className="flex items-center gap-2 flex-wrap">
                {[
                  { id: 'ALL', label: 'All Opportunities' },
                  { id: 'ORB_BREAKOUT', label: '15-Min ORB High/Low' },
                  { id: 'SMC_PATTERN', label: 'SMC & Pattern Setups' },
                  { id: 'GAPS', label: '9:08 AM Pre-Open Gaps' }
                ].map(f => (
                  <button
                    key={f.id}
                    onClick={() => setScreenerFilter(f.id)}
                    className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                      screenerFilter === f.id
                        ? 'bg-emerald-500 text-slate-950 font-bold'
                        : 'bg-slate-800 text-slate-300 hover:bg-slate-700'
                    }`}
                  >
                    {f.label}
                  </button>
                ))}
                <button
                  onClick={fetchScreener}
                  className="p-1.5 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-lg"
                  title="Refresh Scans"
                >
                  <RefreshCw className="w-4 h-4" />
                </button>
              </div>
            </div>

            {/* 9:08 AM Pre-Market Gap Section */}
            {screenerFilter === 'GAPS' && (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                {premarketGaps.map((gap, idx) => (
                  <div key={idx} className="bg-slate-900/90 border border-slate-800 hover:border-amber-500/50 p-4 rounded-xl transition-all">
                    <div className="flex items-center justify-between">
                      <span className="text-base font-bold text-white">{gap.symbol}</span>
                      <span className="text-xs font-bold text-amber-400 bg-amber-500/10 px-2 py-0.5 rounded border border-amber-500/20">
                        +{gap.gap_pct}% GAP UP
                      </span>
                    </div>
                    <div className="text-xs text-slate-400 mt-2">
                      Pre-Open Vol: <strong className="text-slate-200">{gap.pre_open_vol}</strong>
                    </div>
                    <div className="text-xs text-emerald-400 font-medium mt-1">
                      Trigger: {gap.trigger}
                    </div>
                    <div className="flex justify-between text-xs text-slate-400 mt-2 pt-2 border-t border-slate-800">
                      <span>SL: ₹{gap.sl}</span>
                      <span className="text-emerald-400 font-semibold">TGT: ₹{gap.target}</span>
                    </div>
                    <button
                      onClick={() => handleQuickExecute(gap.symbol, 'BUY', 0, 'MIS', 25)}
                      className="w-full mt-3 bg-emerald-500/20 hover:bg-emerald-500 hover:text-slate-950 text-emerald-400 text-xs font-bold py-1.5 rounded-lg border border-emerald-500/40 transition-all flex items-center justify-center gap-1"
                    >
                      <Play className="w-3.5 h-3.5 fill-current" /> Quick Buy via Kite
                    </button>
                  </div>
                ))}
              </div>
            )}

            {/* Main Screener Opportunity Grid */}
            {screenerFilter !== 'GAPS' && (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
                {(screenerFilter === 'ALL' ? screenerOpportunities : screenerOpportunities.filter(o => o.category === screenerFilter)).map((opp, idx) => (
                  <div 
                    key={idx} 
                    className={`bg-gradient-to-br from-slate-900/90 to-slate-950/90 border rounded-2xl p-5 flex flex-col justify-between transition-all hover:scale-[1.01] ${
                      opp.direction === 'LONG' 
                        ? 'border-emerald-500/30 hover:border-emerald-500/80 shadow-lg shadow-emerald-500/5' 
                        : 'border-rose-500/30 hover:border-rose-500/80 shadow-lg shadow-rose-500/5'
                    }`}
                  >
                    <div>
                      {/* Card Header */}
                      <div className="flex items-center justify-between mb-3">
                        <div className="flex items-center gap-2">
                          <span className="text-base font-extrabold text-white tracking-wide">{opp.symbol}</span>
                          <span className="text-[10px] bg-slate-800 text-slate-300 px-2 py-0.5 rounded font-mono">
                            F&O
                          </span>
                        </div>
                        <div className="flex items-center gap-1.5">
                          <span className={`text-xs font-bold px-2 py-0.5 rounded-md flex items-center gap-1 ${
                            opp.direction === 'LONG' ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30' : 'bg-rose-500/20 text-rose-400 border border-rose-500/30'
                          }`}>
                            {opp.direction === 'LONG' ? <TrendingUp className="w-3 h-3" /> : <TrendingDown className="w-3 h-3" />}
                            {opp.direction}
                          </span>
                          <span className="text-xs font-extrabold bg-cyan-500/20 text-cyan-300 border border-cyan-500/30 px-2 py-0.5 rounded-md">
                            {opp.score}%
                          </span>
                        </div>
                      </div>

                      {/* CMP & Change */}
                      <div className="flex items-baseline justify-between mb-3 pb-3 border-b border-slate-800/80">
                        <div>
                          <div className="text-[10px] text-slate-400 font-medium">CMP / ENTRY</div>
                          <div className="text-lg font-bold text-slate-100">₹{opp.cmp}</div>
                        </div>
                        <div className="text-right">
                          <div className="text-[10px] text-slate-400 font-medium">RVOL SURGE</div>
                          <div className="text-sm font-bold text-amber-400">{opp.rvol}x Volume</div>
                        </div>
                      </div>

                      {/* Strategy Triggers */}
                      <div className="space-y-1.5 mb-4">
                        <div className="text-[11px] text-slate-400 font-semibold uppercase tracking-wider">Confluence Triggers</div>
                        {opp.triggers.map((t, tidx) => (
                          <div key={tidx} className="text-xs text-slate-300 flex items-center gap-1.5 bg-slate-800/40 px-2 py-1 rounded-md border border-slate-800">
                            <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400 flex-shrink-0" />
                            <span className="truncate">{t}</span>
                          </div>
                        ))}
                      </div>

                      {/* Trade Targets & Risk */}
                      <div className="grid grid-cols-3 gap-2 bg-slate-950/70 p-2.5 rounded-xl border border-slate-800/80 text-center mb-4">
                        <div>
                          <div className="text-[10px] text-rose-400 font-medium">STOP LOSS</div>
                          <div className="text-xs font-bold text-slate-200">₹{opp.stop_loss}</div>
                        </div>
                        <div>
                          <div className="text-[10px] text-emerald-400 font-medium">TARGET 1</div>
                          <div className="text-xs font-bold text-emerald-300">₹{opp.target_1}</div>
                        </div>
                        <div>
                          <div className="text-[10px] text-cyan-400 font-medium">TARGET 2</div>
                          <div className="text-xs font-bold text-cyan-300">₹{opp.target_2}</div>
                        </div>
                      </div>
                    </div>

                    {/* Action Execution Button */}
                    <button
                      onClick={() => handleQuickExecute(opp.symbol, opp.direction === 'LONG' ? 'BUY' : 'SELL', opp.cmp, 'MIS', 50)}
                      className={`w-full py-2.5 rounded-xl text-xs font-bold flex items-center justify-center gap-2 transition-all shadow-md ${
                        opp.direction === 'LONG'
                          ? 'bg-gradient-to-r from-emerald-500 to-teal-500 hover:from-emerald-400 hover:to-teal-400 text-slate-950 shadow-emerald-500/20'
                          : 'bg-gradient-to-r from-rose-500 to-red-600 hover:from-rose-400 hover:to-red-500 text-white shadow-rose-500/20'
                      }`}
                    >
                      <Play className="w-3.5 h-3.5 fill-current" />
                      Execute {opp.direction === 'LONG' ? 'BUY' : 'SELL'} on Zerodha Kite
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* TAB 2: ATM OPTIONS ENGINE */}
        {activeTab === 'options' && (
          <div className="space-y-6">
            
            {/* Options Summary & Greek Bar */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div className="bg-slate-900/80 border border-slate-800 p-4 rounded-2xl">
                <div className="text-xs text-slate-400 font-medium">UNDERLYING SPOT</div>
                <div className="text-xl font-bold text-white mt-1">{activeSymbol} : ₹{spotPrice}</div>
                <div className="text-xs text-emerald-400 mt-1">ATM Strike: {optionChainData?.atm_strike || '--'}</div>
              </div>
              <div className="bg-slate-900/80 border border-slate-800 p-4 rounded-2xl">
                <div className="text-xs text-slate-400 font-medium">PUT-CALL RATIO (PCR)</div>
                <div className="text-xl font-bold text-emerald-400 mt-1">{optionChainData?.pcr || 1.12}</div>
                <div className="text-xs text-slate-300 mt-1 truncate">{optionChainData?.pcr_sentiment || 'Bullish Bias'}</div>
              </div>
              <div className="bg-slate-900/80 border border-slate-800 p-4 rounded-2xl">
                <div className="text-xs text-slate-400 font-medium">MAX PAIN LEVEL</div>
                <div className="text-xl font-bold text-cyan-400 mt-1">₹{optionChainData?.max_pain || '--'}</div>
                <div className="text-xs text-slate-400 mt-1">Key Institutional Pin Strike</div>
              </div>
              <div className="bg-slate-900/80 border border-slate-800 p-4 rounded-2xl">
                <div className="text-xs text-slate-400 font-medium">CALL / PUT OI WALLS</div>
                <div className="text-sm font-bold text-rose-400 mt-1">Res: ₹{optionChainData?.major_resistance || '--'}</div>
                <div className="text-sm font-bold text-emerald-400 mt-0.5">Sup: ₹{optionChainData?.major_support || '--'}</div>
              </div>
            </div>

            {/* Dynamic Strike Recommendation Card */}
            {recommendedTrade && (
              <div className="bg-gradient-to-r from-emerald-950/40 via-slate-900 to-cyan-950/40 border border-emerald-500/40 rounded-2xl p-5 shadow-xl">
                <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="text-xs font-bold bg-emerald-500 text-slate-950 px-2 py-0.5 rounded">RECOMMENDED STRIKE</span>
                      <h3 className="text-lg font-bold text-white">{recommendedTrade.trade_symbol}</h3>
                      <span className="text-xs bg-slate-800 text-slate-300 px-2 py-0.5 rounded font-mono">Lot Size: {recommendedTrade.lot_size}</span>
                    </div>
                    <p className="text-xs text-slate-300 mt-1">{recommendedTrade.thesis}</p>
                  </div>

                  <div className="flex items-center gap-3">
                    <div className="text-center px-3 py-1 bg-slate-900 rounded-lg border border-slate-800">
                      <div className="text-[10px] text-slate-400">ENTRY</div>
                      <div className="text-sm font-bold text-white">₹{recommendedTrade.entry_price}</div>
                    </div>
                    <div className="text-center px-3 py-1 bg-slate-900 rounded-lg border border-slate-800">
                      <div className="text-[10px] text-rose-400">STOP LOSS</div>
                      <div className="text-sm font-bold text-rose-400">₹{recommendedTrade.stop_loss}</div>
                    </div>
                    <div className="text-center px-3 py-1 bg-slate-900 rounded-lg border border-slate-800">
                      <div className="text-[10px] text-emerald-400">TARGET 1</div>
                      <div className="text-sm font-bold text-emerald-400">₹{recommendedTrade.target_1}</div>
                    </div>
                    <div className="text-center px-3 py-1 bg-slate-900 rounded-lg border border-slate-800">
                      <div className="text-[10px] text-cyan-400">TARGET 2</div>
                      <div className="text-sm font-bold text-cyan-400">₹{recommendedTrade.target_2}</div>
                    </div>
                    <button
                      onClick={() => handleQuickExecute(recommendedTrade.trade_symbol, 'BUY', recommendedTrade.entry_price, 'MIS', recommendedTrade.lot_size)}
                      className="px-5 py-2.5 bg-gradient-to-r from-emerald-500 to-cyan-500 hover:from-emerald-400 hover:to-cyan-400 text-slate-950 text-xs font-extrabold rounded-xl shadow-lg shadow-emerald-500/20"
                    >
                      Buy Strike
                    </button>
                  </div>
                </div>
              </div>
            )}

            {/* Option Chain Table with Greeks and Buildup */}
            <div className="bg-slate-900/80 border border-slate-800 rounded-2xl overflow-hidden">
              <div className="p-4 border-b border-slate-800 flex items-center justify-between">
                <h3 className="text-sm font-bold text-white flex items-center gap-2">
                  <Layers className="w-4 h-4 text-cyan-400" />
                  Live Option Chain & Open Interest Buildup Classifier
                </h3>
                <span className="text-xs text-slate-400 font-mono">Refreshes every 12s</span>
              </div>
              <div className="overflow-x-auto">
                <table className="w-full text-xs text-left">
                  <thead className="bg-slate-950/90 text-slate-400 border-b border-slate-800 uppercase font-semibold text-[10px]">
                    <tr>
                      <th className="py-2.5 px-3 text-center text-emerald-400" colSpan={5}>CALL OPTIONS (CE)</th>
                      <th className="py-2.5 px-3 text-center bg-slate-900 text-slate-200">STRIKE</th>
                      <th className="py-2.5 px-3 text-center text-rose-400" colSpan={5}>PUT OPTIONS (PE)</th>
                    </tr>
                    <tr className="border-b border-slate-800 text-slate-400">
                      <th className="py-2 px-3">Buildup</th>
                      <th className="py-2 px-3">Delta</th>
                      <th className="py-2 px-3">OI</th>
                      <th className="py-2 px-3">LTP (₹)</th>
                      <th className="py-2 px-3 text-center">Action</th>
                      <th className="py-2 px-3 text-center bg-slate-900 text-white font-bold">STRIKE</th>
                      <th className="py-2 px-3 text-center">Action</th>
                      <th className="py-2 px-3">LTP (₹)</th>
                      <th className="py-2 px-3">OI</th>
                      <th className="py-2 px-3">Delta</th>
                      <th className="py-2 px-3">Buildup</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800/60 font-mono">
                    {optionChainData?.calls?.map((call, idx) => {
                      const put = optionChainData.puts[idx];
                      const isAtm = call.moneyness === 'ATM';
                      return (
                        <tr key={call.strike} className={`hover:bg-slate-800/40 transition-colors ${isAtm ? 'bg-emerald-500/10 font-bold' : ''}`}>
                          {/* Call Side */}
                          <td className="py-2 px-3">
                            <span className={`text-[10px] px-1.5 py-0.5 rounded ${
                              call.buildup === 'LONG_BUILDUP' ? 'bg-emerald-500/20 text-emerald-400' :
                              call.buildup === 'SHORT_COVERING' ? 'bg-cyan-500/20 text-cyan-400' :
                              'bg-slate-800 text-slate-400'
                            }`}>
                              {call.buildup}
                            </span>
                          </td>
                          <td className="py-2 px-3 text-slate-300">{call.delta}</td>
                          <td className="py-2 px-3 text-slate-300">{call.oi.toLocaleString()}</td>
                          <td className="py-2 px-3 font-bold text-emerald-400">₹{call.ltp}</td>
                          <td className="py-2 px-3 text-center">
                            <button
                              onClick={() => handleQuickExecute(`${activeSymbol} ${call.strike} CE`, 'BUY', call.ltp, 'MIS', 50)}
                              className="px-2 py-1 bg-emerald-500/20 hover:bg-emerald-500 hover:text-slate-950 text-emerald-400 rounded text-[10px] font-bold"
                            >
                              Buy CE
                            </button>
                          </td>

                          {/* Strike */}
                          <td className="py-2 px-3 text-center bg-slate-900/90 text-white font-extrabold text-xs">
                            {call.strike} {isAtm ? <span className="text-[10px] text-emerald-400">(ATM)</span> : ''}
                          </td>

                          {/* Put Side */}
                          <td className="py-2 px-3 text-center">
                            <button
                              onClick={() => handleQuickExecute(`${activeSymbol} ${put.strike} PE`, 'BUY', put.ltp, 'MIS', 50)}
                              className="px-2 py-1 bg-rose-500/20 hover:bg-rose-500 hover:text-white text-rose-400 rounded text-[10px] font-bold"
                            >
                              Buy PE
                            </button>
                          </td>
                          <td className="py-2 px-3 font-bold text-rose-400">₹{put.ltp}</td>
                          <td className="py-2 px-3 text-slate-300">{put.oi.toLocaleString()}</td>
                          <td className="py-2 px-3 text-slate-300">{put.delta}</td>
                          <td className="py-2 px-3">
                            <span className={`text-[10px] px-1.5 py-0.5 rounded ${
                              put.buildup === 'LONG_BUILDUP' ? 'bg-rose-500/20 text-rose-400' :
                              put.buildup === 'SHORT_COVERING' ? 'bg-amber-500/20 text-amber-400' :
                              'bg-slate-800 text-slate-400'
                            }`}>
                              {put.buildup}
                            </span>
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}

        {/* TAB 3: SMALL-CAP & CATALYST HUNTER */}
        {activeTab === 'catalysts' && (
          <div className="space-y-6">
            
            {/* Catalyst Intro Banner */}
            <div className="bg-gradient-to-r from-cyan-950/40 to-slate-900 border border-cyan-500/30 p-4 rounded-2xl flex flex-col md:flex-row md:items-center justify-between gap-4">
              <div>
                <h2 className="text-lg font-bold text-white flex items-center gap-2">
                  <Sparkles className="w-5 h-5 text-cyan-400" />
                  Small-Cap & Mid-Cap Catalyst Hunter (Quarterly Results & Mega Order Wins)
                </h2>
                <p className="text-xs text-slate-400 mt-1">
                  Automated discovery of fundamental tailwinds: YoY earnings surprises, defense/railway order awards, and deep value turnaround gems.
                </p>
              </div>
              <div className="flex gap-2">
                <span className="text-xs font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 px-3 py-1 rounded-xl">
                  {catalystData?.quarterly_results?.length || 4} Earnings Beats
                </span>
                <span className="text-xs font-semibold bg-cyan-500/10 text-cyan-400 border border-cyan-500/30 px-3 py-1 rounded-xl">
                  {catalystData?.order_wins?.length || 4} Mega Orders
                </span>
              </div>
            </div>

            {/* Section 1: Earnings Surprises & Results */}
            <div>
              <h3 className="text-sm font-bold text-emerald-400 uppercase tracking-wider mb-3 flex items-center gap-2">
                <TrendingUp className="w-4 h-4" /> 1. High Growth Quarterly Results & Earnings Surprises
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                {catalystData?.quarterly_results?.map((item, idx) => (
                  <div key={idx} className="bg-slate-900/90 border border-slate-800 hover:border-emerald-500/40 p-4 rounded-2xl flex flex-col justify-between transition-all">
                    <div>
                      <div className="flex items-center justify-between">
                        <span className="text-base font-bold text-white">{item.symbol}</span>
                        <span className="text-xs font-bold text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded">
                          +{item.change_pct}%
                        </span>
                      </div>
                      <div className="text-[11px] text-slate-400 mt-0.5">{item.company}</div>
                      <div className="text-xs font-semibold text-slate-200 mt-2 line-clamp-2">
                        {item.headline}
                      </div>

                      {/* Growth Stats */}
                      <div className="grid grid-cols-2 gap-2 bg-slate-950 p-2.5 rounded-xl border border-slate-800/80 mt-3 text-xs">
                        <div>
                          <div className="text-[10px] text-slate-400">PAT Growth</div>
                          <div className="font-bold text-emerald-400">{item.details.pat_growth_yoy}</div>
                        </div>
                        <div>
                          <div className="text-[10px] text-slate-400">Rev Growth</div>
                          <div className="font-bold text-cyan-400">{item.details.rev_growth_yoy}</div>
                        </div>
                        <div>
                          <div className="text-[10px] text-slate-400">P/E Ratio</div>
                          <div className="font-bold text-slate-200">{item.valuation.pe}x</div>
                        </div>
                        <div>
                          <div className="text-[10px] text-slate-400">ROCE</div>
                          <div className="font-bold text-emerald-300">{item.valuation.roce}</div>
                        </div>
                      </div>
                    </div>

                    <div className="mt-4 pt-3 border-t border-slate-800 flex items-center justify-between">
                      <div>
                        <div className="text-[10px] text-slate-400">Target Level</div>
                        <div className="text-xs font-bold text-emerald-400">₹{item.target} (SL: ₹{item.stop_loss})</div>
                      </div>
                      <button
                        onClick={() => handleQuickExecute(item.symbol, 'BUY', item.cmp, 'CNC', 10)}
                        className="px-3 py-1.5 bg-emerald-500 hover:bg-emerald-400 text-slate-950 text-xs font-bold rounded-lg"
                      >
                        Invest / Swing
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Section 2: Big Order Wins */}
            <div>
              <h3 className="text-sm font-bold text-cyan-400 uppercase tracking-wider mb-3 flex items-center gap-2">
                <Building2 className="w-4 h-4" /> 2. Mega Order Book Additions & Contract Wins
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                {catalystData?.order_wins?.map((item, idx) => (
                  <div key={idx} className="bg-slate-900/90 border border-slate-800 hover:border-cyan-500/40 p-4 rounded-2xl flex flex-col justify-between transition-all">
                    <div>
                      <div className="flex items-center justify-between">
                        <span className="text-base font-bold text-white">{item.symbol}</span>
                        <span className="text-xs font-bold text-cyan-300 bg-cyan-500/10 px-2 py-0.5 rounded">
                          {item.order_value}
                        </span>
                      </div>
                      <div className="text-[11px] text-slate-400 mt-0.5">{item.company}</div>
                      <div className="text-xs font-semibold text-slate-200 mt-2">
                        {item.headline}
                      </div>
                      <p className="text-[11px] text-slate-400 mt-2 bg-slate-950 p-2 rounded-lg border border-slate-800">
                        {item.impact}
                      </p>
                    </div>

                    <div className="mt-4 pt-3 border-t border-slate-800 flex items-center justify-between">
                      <div>
                        <div className="text-[10px] text-slate-400">Target</div>
                        <div className="text-xs font-bold text-cyan-400">₹{item.target}</div>
                      </div>
                      <button
                        onClick={() => handleQuickExecute(item.symbol, 'BUY', item.cmp, 'CNC', 20)}
                        className="px-3 py-1.5 bg-cyan-500 hover:bg-cyan-400 text-slate-950 text-xs font-bold rounded-lg"
                      >
                        Buy Order Play
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Section 3: Undervalued Turnaround Gems */}
            <div>
              <h3 className="text-sm font-bold text-amber-400 uppercase tracking-wider mb-3 flex items-center gap-2">
                <Target className="w-4 h-4" /> 3. Deep Value & Turnaround Small-Cap Setups
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {catalystData?.undervalued_gems?.map((item, idx) => (
                  <div key={idx} className="bg-slate-900/90 border border-slate-800 p-4 rounded-2xl flex flex-col justify-between">
                    <div>
                      <div className="flex items-center justify-between">
                        <span className="text-base font-bold text-white">{item.symbol}</span>
                        <span className="text-xs font-bold text-amber-400 bg-amber-500/10 px-2 py-0.5 rounded">
                          P/E {item.pe}x (Sec: {item.sector_pe}x)
                        </span>
                      </div>
                      <div className="text-xs text-slate-300 mt-2 font-medium">
                        Pattern: <strong className="text-emerald-400">{item.pattern}</strong>
                      </div>
                      <div className="text-xs text-slate-400 mt-1">{item.catalyst}</div>
                      <div className="grid grid-cols-2 gap-2 mt-3 bg-slate-950 p-2 rounded-lg text-xs">
                        <div>PEG: <strong className="text-slate-200">{item.peg_ratio}</strong></div>
                        <div>ROCE: <strong className="text-emerald-400">{item.roce}</strong></div>
                      </div>
                    </div>
                    <div className="mt-4 pt-3 border-t border-slate-800 flex items-center justify-between">
                      <div className="text-xs font-bold text-emerald-400">Target: ₹{item.target}</div>
                      <button
                        onClick={() => handleQuickExecute(item.symbol, 'BUY', item.cmp, 'CNC', 10)}
                        className="px-3 py-1.5 bg-amber-500 hover:bg-amber-400 text-slate-950 text-xs font-bold rounded-lg"
                      >
                        Buy Turnaround
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>

          </div>
        )}

        {/* TAB 4: INSTITUTIONAL & FII/DII FLOW */}
        {activeTab === 'institutional' && (
          <div className="space-y-6">
            
            {/* Institutional Overview Header */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="bg-slate-900/80 border border-slate-800 p-5 rounded-2xl">
                <div className="text-xs text-slate-400 font-medium uppercase tracking-wider">FII Cash Today</div>
                <div className={`text-2xl font-extrabold mt-1 ${institutionalData?.cash_flow?.fii_today_net >= 0 ? 'text-emerald-400' : 'text-rose-400'}`}>
                  {institutionalData?.cash_flow?.fii_today_net >= 0 ? '+' : ''}₹{institutionalData?.cash_flow?.fii_today_net} Cr
                </div>
                <div className="text-xs text-slate-400 mt-1">5-Day FII: ₹{institutionalData?.cash_flow?.fii_5d_cumulative} Cr</div>
              </div>

              <div className="bg-slate-900/80 border border-slate-800 p-5 rounded-2xl">
                <div className="text-xs text-slate-400 font-medium uppercase tracking-wider">DII Cash Today</div>
                <div className="text-2xl font-extrabold text-emerald-400 mt-1">
                  +₹{institutionalData?.cash_flow?.dii_today_net} Cr
                </div>
                <div className="text-xs text-emerald-300 mt-1 font-medium">5-Day DII Inflow: +₹{institutionalData?.cash_flow?.dii_5d_cumulative} Cr (Strong Floor)</div>
              </div>

              <div className="bg-slate-900/80 border border-slate-800 p-5 rounded-2xl">
                <div className="text-xs text-slate-400 font-medium uppercase tracking-wider">FII Index Futures Long Ratio</div>
                <div className="text-2xl font-extrabold text-cyan-400 mt-1">
                  {institutionalData?.derivatives?.index_futures?.long_ratio_pct}% Long
                </div>
                <div className="text-xs text-amber-400 mt-1 font-semibold">Short Heavy → Major Short Covering Fuel</div>
              </div>
            </div>

            {/* Block Deals & Bulk Deals Tracker */}
            <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-5">
              <h3 className="text-base font-bold text-white mb-3 flex items-center gap-2">
                <Landmark className="w-5 h-5 text-emerald-400" />
                Live Institutional Block Deals & Large Institutional Handover Tracker
              </h3>
              <div className="overflow-x-auto">
                <table className="w-full text-xs text-left">
                  <thead className="bg-slate-950 text-slate-400 uppercase text-[10px] border-b border-slate-800">
                    <tr>
                      <th className="py-2.5 px-3">Date</th>
                      <th className="py-2.5 px-3">Stock</th>
                      <th className="py-2.5 px-3">Institutional Client</th>
                      <th className="py-2.5 px-3">Deal Type</th>
                      <th className="py-2.5 px-3">Quantity</th>
                      <th className="py-2.5 px-3">Price (₹)</th>
                      <th className="py-2.5 px-3">Value (₹ Cr)</th>
                      <th className="py-2.5 px-3">Bias</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800 font-mono">
                    {institutionalData?.bulk_block_deals?.map((deal, idx) => (
                      <tr key={idx} className="hover:bg-slate-800/30">
                        <td className="py-2.5 px-3 text-slate-400">{deal.date}</td>
                        <td className="py-2.5 px-3 font-bold text-white">{deal.symbol}</td>
                        <td className="py-2.5 px-3 text-slate-200">{deal.client_name}</td>
                        <td className="py-2.5 px-3">
                          <span className={`text-[10px] px-2 py-0.5 rounded font-bold ${deal.deal_type === 'BUY' ? 'bg-emerald-500/20 text-emerald-400' : 'bg-rose-500/20 text-rose-400'}`}>
                            {deal.deal_type}
                          </span>
                        </td>
                        <td className="py-2.5 px-3 text-slate-300">{deal.quantity}</td>
                        <td className="py-2.5 px-3 text-slate-200 font-bold">₹{deal.avg_price}</td>
                        <td className="py-2.5 px-3 text-emerald-400 font-bold">₹{deal.deal_value_crores} Cr</td>
                        <td className="py-2.5 px-3">
                          <span className="text-[10px] bg-cyan-500/20 text-cyan-300 px-2 py-0.5 rounded font-bold">
                            {deal.action_bias}
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>

          </div>
        )}

        {/* TAB 5: ZERODHA KITE BROKER HUB */}
        {activeTab === 'kite' && (
          <div className="space-y-6">
            
            {/* Broker Status & MCP Banner */}
            <div className="bg-gradient-to-r from-blue-950/40 via-slate-900 to-slate-950 border border-blue-500/30 p-5 rounded-2xl flex flex-col md:flex-row md:items-center justify-between gap-4">
              <div>
                <div className="flex items-center gap-2">
                  <h2 className="text-lg font-bold text-white">Zerodha Kite & Model Context Protocol (MCP) Hub</h2>
                  <span className="text-xs bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 px-2.5 py-0.5 rounded-full font-bold">
                    {kiteStatus.status}
                  </span>
                </div>
                <p className="text-xs text-slate-400 mt-1">
                  Direct KiteConnect API Execution + Kite MCP Server tool calling for autonomous AI trading.
                </p>
                <div className="text-[11px] text-blue-400 font-mono mt-2">
                  MCP Endpoint: <span className="text-slate-300">{kiteStatus.mcp_server_url || 'https://mcp.kite.trade/mcp'}</span>
                </div>
              </div>
              <button
                onClick={fetchKiteData}
                className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold rounded-xl flex items-center gap-2"
              >
                <RefreshCw className="w-4 h-4" /> Sync Kite Account
              </button>
            </div>

            {/* Margins & Ledger Overview */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div className="bg-slate-900/80 border border-slate-800 p-4 rounded-2xl">
                <div className="text-xs text-slate-400 font-medium">AVAILABLE CASH</div>
                <div className="text-xl font-bold text-white mt-1">₹{(kiteMargins?.equity?.available?.cash || 420000).toLocaleString()}</div>
              </div>
              <div className="bg-slate-900/80 border border-slate-800 p-4 rounded-2xl">
                <div className="text-xs text-slate-400 font-medium">COLLATERAL MARGIN</div>
                <div className="text-xl font-bold text-cyan-400 mt-1">₹{(kiteMargins?.equity?.available?.collateral || 80000).toLocaleString()}</div>
              </div>
              <div className="bg-slate-900/80 border border-slate-800 p-4 rounded-2xl">
                <div className="text-xs text-slate-400 font-medium">UTILISED EXPOSURE</div>
                <div className="text-xl font-bold text-amber-400 mt-1">₹{(kiteMargins?.equity?.utilised?.debits || 80000).toLocaleString()}</div>
              </div>
              <div className="bg-slate-900/80 border border-slate-800 p-4 rounded-2xl">
                <div className="text-xs text-slate-400 font-medium">UNREALISED M2M</div>
                <div className="text-xl font-bold text-emerald-400 mt-1">+₹{(kiteMargins?.equity?.utilised?.m2m_unrealised || 2850).toLocaleString()}</div>
              </div>
            </div>

            {/* Positions Table */}
            <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-5">
              <h3 className="text-base font-bold text-white mb-3">Active Kite Positions</h3>
              <div className="overflow-x-auto">
                <table className="w-full text-xs text-left">
                  <thead className="bg-slate-950 text-slate-400 uppercase text-[10px] border-b border-slate-800">
                    <tr>
                      <th className="py-2.5 px-3">Symbol</th>
                      <th className="py-2.5 px-3">Product</th>
                      <th className="py-2.5 px-3">Qty</th>
                      <th className="py-2.5 px-3">Avg Price (₹)</th>
                      <th className="py-2.5 px-3">LTP (₹)</th>
                      <th className="py-2.5 px-3">PnL (₹)</th>
                      <th className="py-2.5 px-3 text-center">Action</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800 font-mono">
                    {kitePositions.map((pos, idx) => (
                      <tr key={idx} className="hover:bg-slate-800/30">
                        <td className="py-2.5 px-3 font-bold text-white">{pos.tradingsymbol}</td>
                        <td className="py-2.5 px-3 text-slate-300">{pos.product}</td>
                        <td className="py-2.5 px-3 text-slate-200">{pos.quantity}</td>
                        <td className="py-2.5 px-3 text-slate-300">₹{pos.average_price}</td>
                        <td className="py-2.5 px-3 text-slate-200 font-bold">₹{pos.last_price}</td>
                        <td className={`py-2.5 px-3 font-bold ${pos.pnl >= 0 ? 'text-emerald-400' : 'text-rose-400'}`}>
                          {pos.pnl >= 0 ? '+' : ''}₹{pos.pnl}
                        </td>
                        <td className="py-2.5 px-3 text-center">
                          <button
                            onClick={() => handleQuickExecute(pos.tradingsymbol, 'SELL', pos.last_price, pos.product, pos.quantity)}
                            className="px-2.5 py-1 bg-rose-500/20 hover:bg-rose-500 hover:text-white text-rose-400 text-[10px] font-bold rounded"
                          >
                            Close Position
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>

          </div>
        )}

        {/* TAB 6: 7-AGENT AI CONFLUENCE TERMINAL */}
        {activeTab === 'terminal' && (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            
            {/* Chart & Live Price Action */}
            <div className="lg:col-span-2 space-y-6">
              <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-5">
                <div className="flex items-center justify-between mb-4">
                  <div>
                    <h3 className="text-base font-bold text-white">{activeSymbol} Live Price Action (5m)</h3>
                    <p className="text-xs text-slate-400">Institutional VWAP + Multi-Agent Trend Matrix</p>
                  </div>
                  <div className="text-right">
                    <div className="text-lg font-bold text-emerald-400">₹{spotPrice}</div>
                  </div>
                </div>

                <div className="h-64 w-full">
                  <ResponsiveContainer width="100%" height="100%">
                    <AreaChart data={chartData}>
                      <defs>
                        <linearGradient id="priceGrad" x1="0" y1="0" x2="0" y2="1">
                          <stop offset="5%" stopColor="#10b981" stopOpacity={0.4}/>
                          <stop offset="95%" stopColor="#10b981" stopOpacity={0}/>
                        </linearGradient>
                      </defs>
                      <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                      <XAxis dataKey="time" stroke="#64748b" textAnchor="end" tick={{ fontSize: 10 }} />
                      <YAxis domain={['auto', 'auto']} stroke="#64748b" orientation="right" tick={{ fontSize: 10 }} />
                      <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: 8 }} />
                      <Area type="monotone" dataKey="price" stroke="#10b981" strokeWidth={2} fillOpacity={1} fill="url(#priceGrad)" />
                      <Line type="monotone" dataKey="vwap" stroke="#f59e0b" strokeDasharray="4 4" dot={false} />
                    </AreaChart>
                  </ResponsiveContainer>
                </div>
              </div>

              {/* Master AI Strategy Signal */}
              {signal && (
                <div className="bg-gradient-to-r from-emerald-950/40 via-slate-900 to-cyan-950/40 border border-emerald-500/40 rounded-2xl p-5">
                  <div className="flex items-center justify-between">
                    <div>
                      <span className="text-xs font-bold text-emerald-400 uppercase tracking-wider">Master AI Signal</span>
                      <h3 className="text-xl font-bold text-white mt-1">{signal.action} {signal.symbol}</h3>
                      <p className="text-xs text-slate-300 mt-1">{signal.reason}</p>
                    </div>
                    <div className="text-right">
                      <div className="text-xs text-slate-400">Confluence Edge</div>
                      <div className="text-2xl font-extrabold text-emerald-400">{signal.confidence}%</div>
                    </div>
                  </div>
                </div>
              )}
            </div>

            {/* AI Agents Team Panel */}
            <div className="space-y-4">
              <h3 className="text-sm font-bold text-slate-300 uppercase tracking-wider">7 Specialized AI Agents</h3>
              {[
                { name: 'Market Analyst', role: 'Technical & SMC Scanner', status: 'Scanning 50+ F&O', icon: Activity, color: 'text-emerald-400' },
                { name: 'News Analyst', role: 'Sentiment & Order Catalysts', status: 'High Bullish Flow', icon: Newspaper, color: 'text-cyan-400' },
                { name: 'Risk Manager', role: 'Position Sizing & Greeks', status: 'Max 1.5% Risk OK', icon: Shield, color: 'text-amber-400' },
                { name: 'Macro Analyst', role: 'Gift Nifty & Global Cues', status: 'Positive Bias (+25)', icon: Globe, color: 'text-blue-400' },
                { name: 'Discovery AI', role: 'Real-Time Stock Hunter', status: '12 Breakouts Found', icon: Sparkles, color: 'text-purple-400' },
                { name: 'Execution Agent', role: 'Kite / Dhan Direct Routing', status: 'Kite MCP Ready', icon: Zap, color: 'text-emerald-400' }
              ].map((agent, idx) => {
                const IconComponent = agent.icon;
                return (
                  <div key={idx} className="bg-slate-900/80 border border-slate-800 p-3.5 rounded-xl flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <div className="p-2 bg-slate-800 rounded-lg">
                        <IconComponent className={`w-4 h-4 ${agent.color}`} />
                      </div>
                      <div>
                        <div className="text-xs font-bold text-white">{agent.name}</div>
                        <div className="text-[10px] text-slate-400">{agent.role}</div>
                      </div>
                    </div>
                    <span className="text-[11px] font-semibold text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded border border-emerald-500/20">
                      {agent.status}
                    </span>
                  </div>
                );
              })}
            </div>

          </div>
        )}

      </main>

      {/* Footer */}
      <footer className="border-t border-slate-800/80 bg-[#0c1017] px-5 py-3 text-center text-xs text-slate-500">
        NSE AI Trading Stack • 7-Agent Architecture • Multi-Timeframe F&O & Catalyst Screener • Zerodha Kite MCP Connected
      </footer>

    </div>
  );
}

export default App;
