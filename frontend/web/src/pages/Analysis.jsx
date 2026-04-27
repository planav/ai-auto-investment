import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  Search, Brain, TrendingUp, TrendingDown, Activity,
  BarChart3, PieChart, ArrowRight, Sparkles, Loader2,
  AlertCircle, CheckCircle, Target, Shield, Zap, DollarSign,
  ChevronDown, ChevronUp, RefreshCw
} from 'lucide-react'
import { marketApi, analysisApi } from '../services/api'
import toast from 'react-hot-toast'

const SIGNAL_COLORS = {
  strong_buy:  { bg: 'bg-emerald-500/20', text: 'text-emerald-400', label: 'STRONG BUY' },
  buy:         { bg: 'bg-green-500/20',   text: 'text-green-400',   label: 'BUY' },
  hold:        { bg: 'bg-yellow-500/20',  text: 'text-yellow-400',  label: 'HOLD' },
  sell:        { bg: 'bg-orange-500/20',  text: 'text-orange-400',  label: 'SELL' },
  strong_sell: { bg: 'bg-red-500/20',     text: 'text-red-400',     label: 'STRONG SELL' },
}

function AnalysisSection({ title, content, icon: Icon, color = 'primary' }) {
  const [expanded, setExpanded] = useState(true)
  if (!content) return null
  return (
    <div className="bg-dark-lighter rounded-xl overflow-hidden">
      <button
        onClick={() => setExpanded(v => !v)}
        className="w-full flex items-center justify-between p-4 hover:bg-white/5 transition-colors"
      >
        <div className="flex items-center gap-3">
          {Icon && <Icon className={`w-5 h-5 text-${color}`} />}
          <span className="font-semibold">{title}</span>
        </div>
        {expanded ? <ChevronUp className="w-4 h-4 text-gray-500" /> : <ChevronDown className="w-4 h-4 text-gray-500" />}
      </button>
      {expanded && (
        <div className="px-4 pb-4 text-sm text-gray-300 leading-relaxed whitespace-pre-wrap">
          {content}
        </div>
      )}
    </div>
  )
}

export default function Analysis() {
  const [searchQuery, setSearchQuery]     = useState('')
  const [selectedSymbol, setSelectedSymbol] = useState(null)
  const [stockAnalysis, setStockAnalysis] = useState(null)
  const [isAnalyzing, setIsAnalyzing]     = useState(false)
  const [popularAssets, setPopularAssets] = useState([])
  const [marketOverview, setMarketOverview] = useState({})
  const [isLoading, setIsLoading]         = useState(true)
  const [searchResults, setSearchResults] = useState([])
  const [isSearching, setIsSearching]     = useState(false)

  const popularSymbols = ['AAPL', 'MSFT', 'GOOGL', 'NVDA', 'AMZN', 'META', 'TSLA', 'AMD']

  useEffect(() => {
    fetchMarketData()
    const interval = setInterval(fetchMarketData, 60000)
    return () => clearInterval(interval)
  }, [])

  const fetchMarketData = async () => {
    setIsLoading(true)
    try {
      const [overviewRes, popularRes] = await Promise.all([
        marketApi.getMarketOverview().catch(() => ({ data: null })),
        marketApi.getBatchQuotes(popularSymbols).catch(() => ({ data: null })),
      ])
      if (overviewRes.data?.indices) setMarketOverview(overviewRes.data.indices)
      if (popularRes.data) {
        const items = Array.isArray(popularRes.data) ? popularRes.data : Object.values(popularRes.data)
        setPopularAssets(items.slice(0, 8))
      }
    } catch (err) {
      console.error('Market data error:', err)
    } finally {
      setIsLoading(false)
    }
  }

  const fetchDeepAnalysis = async (symbol) => {
    if (!symbol) return
    const sym = symbol.toUpperCase().trim()
    setIsAnalyzing(true)
    setSelectedSymbol(sym)
    setStockAnalysis(null)
    try {
      const res = await analysisApi.getStockAnalysis(sym)
      setStockAnalysis(res.data)
      setSearchResults([])  // Clear dropdown only on success
    } catch (err) {
      console.error('Analysis error:', err)
      const msg = err.response?.data?.detail || `Could not analyse ${sym}`
      toast.error(msg)
      // Don't clear search results on failure so user can try another
    } finally {
      setIsAnalyzing(false)
    }
  }

  const handleSearch = async (e) => {
    e.preventDefault()
    if (!searchQuery.trim()) return
    const sym = searchQuery.trim().toUpperCase()
    setIsSearching(true)
    try {
      const res = await marketApi.searchStocks(searchQuery)
      const allResults = res.data || []
      // Filter to US-listed stocks only (no dots = no foreign exchanges)
      const usResults = allResults.filter(r => r.symbol && !r.symbol.includes('.') && !r.symbol.includes(':'))
      setSearchResults(usResults.slice(0, 8))
      // If the search term looks like an exact symbol, auto-analyse it
      if (usResults.length === 0 || usResults[0]?.symbol === sym) {
        await fetchDeepAnalysis(sym)
      }
    } catch {
      await fetchDeepAnalysis(sym)
    } finally {
      setIsSearching(false)
    }
  }

  const sig = stockAnalysis ? (SIGNAL_COLORS[stockAnalysis.signal] || SIGNAL_COLORS.hold) : null

  const aiModels = [
    { name: 'Claude Sonnet 4.6', status: 'active', description: 'Deep fundamental + technical analysis' },
    { name: 'RandomForest Ensemble', status: 'active', description: 'sklearn ML stock scoring engine' },
    { name: 'GradientBoosting', status: 'active', description: 'Momentum & analyst signal fusion' },
    { name: 'NewsAPI Sentiment', status: 'active', description: 'Real-time news sentiment analysis' },
  ]

  return (
    <div className="pt-24 pb-12 px-4">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="mb-8">
          <h1 className="text-3xl font-bold font-display mb-2">
            <span className="text-gradient">AI Stock Analysis</span>
          </h1>
          <p className="text-gray-400">
            Full fundamental + technical analysis powered by Claude Sonnet AI — search any stock
          </p>
        </motion.div>

        {/* Market Overview */}
        {Object.keys(marketOverview).length > 0 && (
          <motion.div
            initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}
            className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8"
          >
            {Object.entries(marketOverview).slice(0, 4).map(([key, data]) => (
              <div key={key} className="glass-card p-4">
                <div className="text-gray-400 text-xs mb-1 uppercase tracking-wide">{data.name || key}</div>
                <div className="text-xl font-bold">${(data.price || 0).toLocaleString(undefined, {maximumFractionDigits:2})}</div>
                <div className={`text-sm font-medium ${(data.change_percent || 0) >= 0 ? 'text-emerald-400' : 'text-red-400'}`}>
                  {(data.change_percent || 0) >= 0 ? '▲' : '▼'} {Math.abs(data.change_percent || 0).toFixed(2)}%
                </div>
              </div>
            ))}
          </motion.div>
        )}

        {/* Search Bar */}
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.15 }} className="mb-8">
          <form onSubmit={handleSearch} className="relative max-w-2xl">
            <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-500" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Enter stock symbol or company name (e.g. AAPL, NVDA, Tesla)..."
              className="w-full pl-12 pr-32 py-4 glass-card border border-gray-700 rounded-xl focus:outline-none focus:border-primary transition-colors text-lg"
            />
            <button
              type="submit"
              disabled={isSearching || isAnalyzing}
              className="absolute right-2 top-1/2 -translate-y-1/2 px-5 py-2 bg-primary text-dark rounded-lg font-semibold text-sm hover:bg-primary/90 transition-colors disabled:opacity-50"
            >
              {isSearching ? <Loader2 className="w-4 h-4 animate-spin" /> : 'Analyse'}
            </button>
          </form>

          {/* Quick picks */}
          <div className="flex flex-wrap gap-2 mt-3">
            {popularSymbols.map(sym => (
              <button
                key={sym}
                onClick={() => { setSearchQuery(sym); fetchDeepAnalysis(sym) }}
                className="px-3 py-1 text-xs bg-dark-lighter hover:bg-primary/20 hover:text-primary border border-gray-700 rounded-full transition-colors"
              >
                {sym}
              </button>
            ))}
          </div>

          {/* Search results dropdown */}
          {searchResults.length > 0 && (
            <div className="mt-3 glass-card p-3 max-w-2xl border border-gray-700 rounded-xl">
              {searchResults.map(r => (
                <button
                  key={r.symbol}
                  onClick={() => { setSearchQuery(r.symbol); fetchDeepAnalysis(r.symbol) }}
                  className="w-full flex items-center justify-between p-3 rounded-lg hover:bg-dark-lighter transition-colors"
                >
                  <div className="flex gap-3 items-center">
                    <span className="font-bold text-primary w-16 text-left">{r.symbol}</span>
                    <span className="text-gray-400 text-sm">{r.name}</span>
                  </div>
                  <ArrowRight className="w-4 h-4 text-gray-500" />
                </button>
              ))}
            </div>
          )}
        </motion.div>

        {/* AI Analysis Loading State */}
        {isAnalyzing && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className="mb-8 glass-card p-8 border border-primary/30"
          >
            <div className="flex items-center gap-4 mb-6">
              <div className="relative">
                <Brain className="w-12 h-12 text-primary animate-pulse" />
                <span className="absolute -top-1 -right-1 w-4 h-4 bg-primary rounded-full animate-ping" />
              </div>
              <div>
                <h3 className="text-xl font-semibold">AI System Analysing <span className="text-primary">{selectedSymbol}</span></h3>
                <p className="text-gray-400 text-sm">Claude Sonnet is processing real-time market data</p>
              </div>
            </div>

            <div className="space-y-3">
              {[
                { step: '1', label: 'Fetching Finnhub real-time quote, metrics & analyst data…', done: true },
                { step: '2', label: 'Pulling latest market news & company developments…', done: true },
                { step: '3', label: 'Claude AI performing fundamental + technical analysis…', done: false },
                { step: '4', label: 'Generating investment recommendation & price target…', done: false },
              ].map((s, i) => (
                <div key={i} className="flex items-center gap-3 text-sm">
                  {s.done ? (
                    <span className="w-6 h-6 rounded-full bg-emerald-500/20 text-emerald-400 flex items-center justify-center text-xs font-bold flex-shrink-0">✓</span>
                  ) : (
                    <Loader2 className="w-5 h-5 text-primary animate-spin flex-shrink-0" />
                  )}
                  <span className={s.done ? 'text-gray-400 line-through' : 'text-gray-200'}>{s.label}</span>
                </div>
              ))}
            </div>

            <p className="text-xs text-gray-500 mt-4">
              Full fundamental + technical analysis takes 15–30 seconds. This is powered by Claude Sonnet 4.6.
            </p>
          </motion.div>
        )}

        {/* Deep Analysis Result */}
        {stockAnalysis && !isAnalyzing && (
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="mb-8">
            {/* Header card */}
            <div className="glass-card p-6 border border-primary/30 mb-4">
              <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-6">
                <div className="flex items-center gap-4">
                  <div className="w-14 h-14 rounded-xl bg-primary/10 flex items-center justify-center">
                    <span className="text-2xl font-bold text-primary">{stockAnalysis.symbol[0]}</span>
                  </div>
                  <div>
                    <h2 className="text-2xl font-bold">{stockAnalysis.symbol}</h2>
                    <p className="text-gray-400">{stockAnalysis.company_name} · {stockAnalysis.sector}</p>
                  </div>
                </div>
                <div className="flex items-center gap-4">
                  <div className="text-right">
                    <div className="text-3xl font-bold">${(stockAnalysis.current_price || 0).toFixed(2)}</div>
                    <div className={`text-sm font-medium ${stockAnalysis.daily_change_pct >= 0 ? 'text-emerald-400' : 'text-red-400'}`}>
                      {stockAnalysis.daily_change_pct >= 0 ? '▲' : '▼'} {Math.abs(stockAnalysis.daily_change_pct || 0).toFixed(2)}% today
                    </div>
                  </div>
                  {sig && (
                    <span className={`px-5 py-2.5 rounded-full text-sm font-bold ${sig.bg} ${sig.text}`}>
                      {sig.label}
                    </span>
                  )}
                </div>
              </div>

              {/* Metrics row */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
                <div className="bg-dark-lighter p-4 rounded-xl text-center">
                  <div className="text-gray-400 text-xs mb-1">AI Confidence</div>
                  <div className="text-2xl font-bold text-primary">{Math.round((stockAnalysis.confidence || 0) * 100)}%</div>
                </div>
                <div className="bg-dark-lighter p-4 rounded-xl text-center">
                  <div className="text-gray-400 text-xs mb-1">Overall Score</div>
                  <div className={`text-2xl font-bold ${stockAnalysis.overall_score >= 70 ? 'text-emerald-400' : stockAnalysis.overall_score >= 50 ? 'text-yellow-400' : 'text-red-400'}`}>
                    {Math.round(stockAnalysis.overall_score || 0)}/100
                  </div>
                </div>
                <div className="bg-dark-lighter p-4 rounded-xl text-center">
                  <div className="text-gray-400 text-xs mb-1">Price Target (12M)</div>
                  <div className="text-2xl font-bold text-secondary">
                    {stockAnalysis.price_target ? `$${stockAnalysis.price_target.toFixed(0)}` : 'N/A'}
                  </div>
                </div>
                <div className="bg-dark-lighter p-4 rounded-xl text-center">
                  <div className="text-gray-400 text-xs mb-1">Sector</div>
                  <div className="text-sm font-semibold truncate">{stockAnalysis.sector || 'N/A'}</div>
                </div>
              </div>

              {/* Analyst consensus */}
              {stockAnalysis.analyst_consensus && (
                <div className="bg-dark-lighter p-4 rounded-xl flex items-start gap-3">
                  <CheckCircle className="w-5 h-5 text-primary flex-shrink-0 mt-0.5" />
                  <div>
                    <div className="text-xs text-gray-400 mb-1">Wall Street Analyst Consensus</div>
                    <p className="text-sm text-gray-200">{stockAnalysis.analyst_consensus}</p>
                  </div>
                </div>
              )}
            </div>

            {/* Analysis sections */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 mb-4">
              <AnalysisSection
                title="Fundamental Analysis"
                content={stockAnalysis.fundamental_analysis}
                icon={BarChart3} color="primary"
              />
              <AnalysisSection
                title="Technical Analysis"
                content={stockAnalysis.technical_analysis}
                icon={Activity} color="secondary"
              />
              <AnalysisSection
                title="Market Sentiment"
                content={stockAnalysis.market_sentiment}
                icon={Brain} color="accent"
              />
              <AnalysisSection
                title="Valuation Assessment"
                content={stockAnalysis.valuation_assessment}
                icon={DollarSign} color="primary"
              />
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
              <div className="glass-card p-4 border border-emerald-500/20">
                <div className="flex items-center gap-2 mb-3">
                  <Zap className="w-4 h-4 text-emerald-400" />
                  <h3 className="font-semibold text-emerald-400">Growth Catalysts</h3>
                </div>
                <p className="text-sm text-gray-300 leading-relaxed">{stockAnalysis.growth_catalysts}</p>
              </div>
              <div className="glass-card p-4 border border-red-500/20">
                <div className="flex items-center gap-2 mb-3">
                  <AlertCircle className="w-4 h-4 text-red-400" />
                  <h3 className="font-semibold text-red-400">Key Risks</h3>
                </div>
                <p className="text-sm text-gray-300 leading-relaxed">{stockAnalysis.key_risks}</p>
              </div>
            </div>

            {/* Recommendation */}
            <div className={`glass-card p-6 border ${sig?.text.replace('text-','border-')}/30`}>
              <div className="flex items-start gap-4">
                <div className={`w-12 h-12 rounded-xl ${sig?.bg} flex items-center justify-center flex-shrink-0`}>
                  <Target className={`w-6 h-6 ${sig?.text}`} />
                </div>
                <div>
                  <div className="text-xs text-gray-400 mb-1 uppercase tracking-wide">Investment Recommendation</div>
                  <p className="text-gray-200 leading-relaxed">{stockAnalysis.investment_recommendation}</p>
                </div>
              </div>
            </div>

            {/* Refresh button */}
            <div className="text-center mt-4">
              <button
                onClick={() => fetchDeepAnalysis(stockAnalysis.symbol)}
                className="flex items-center gap-2 mx-auto px-4 py-2 text-sm text-gray-400 hover:text-primary transition-colors"
              >
                <RefreshCw className="w-4 h-4" /> Refresh Analysis
              </button>
            </div>
          </motion.div>
        )}

        {/* Popular assets + sidebar */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Popular stocks */}
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }} className="lg:col-span-2">
            <div className="glass-card p-6">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-xl font-semibold">Popular Stocks</h2>
                <span className="flex items-center gap-2 text-xs text-primary">
                  <Sparkles className="w-3 h-3" /> Live · Click to analyse
                </span>
              </div>

              {isLoading ? (
                <div className="flex justify-center py-12"><Loader2 className="w-8 h-8 text-primary animate-spin" /></div>
              ) : popularAssets.length > 0 ? (
                <div className="space-y-3">
                  {popularAssets.map((asset, i) => {
                    const sym = asset.symbol || asset
                    const price = asset.price || asset.current_price || 0
                    const chg = asset.change_percent || asset.dp || 0
                    return (
                      <div
                        key={i}
                        onClick={() => fetchDeepAnalysis(sym)}
                        className="flex items-center justify-between p-4 rounded-xl bg-dark-lighter hover:bg-primary/10 cursor-pointer transition-colors group"
                      >
                        <div className="flex items-center gap-3">
                          <div className="w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center">
                            <span className="font-bold text-primary text-sm">{sym[0]}</span>
                          </div>
                          <div>
                            <div className="font-semibold">{sym}</div>
                            <div className="text-xs text-gray-500">Click to get AI analysis</div>
                          </div>
                        </div>
                        <div className="flex items-center gap-4">
                          <div className="text-right">
                            <div className="font-semibold">${Number(price).toFixed(2)}</div>
                            <div className={`text-xs ${Number(chg) >= 0 ? 'text-emerald-400' : 'text-red-400'}`}>
                              {Number(chg) >= 0 ? '+' : ''}{Number(chg).toFixed(2)}%
                            </div>
                          </div>
                          {Number(chg) >= 0
                            ? <TrendingUp className="w-4 h-4 text-emerald-400" />
                            : <TrendingDown className="w-4 h-4 text-red-400" />
                          }
                          <ArrowRight className="w-4 h-4 text-gray-600 group-hover:text-primary transition-colors" />
                        </div>
                      </div>
                    )
                  })}
                </div>
              ) : (
                <p className="text-center text-gray-500 py-8">Search a stock above to get started</p>
              )}
            </div>
          </motion.div>

          {/* Sidebar */}
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.4 }}>
            <div className="glass-card p-6 mb-6">
              <div className="flex items-center gap-2 mb-4">
                <Brain className="w-5 h-5 text-primary" />
                <h2 className="text-lg font-semibold">AI Engine Stack</h2>
              </div>
              <div className="space-y-3">
                {aiModels.map((model, i) => (
                  <div key={i} className="p-3 rounded-lg bg-dark-lighter">
                    <div className="flex items-center justify-between mb-1">
                      <span className="text-sm font-medium">{model.name}</span>
                      <span className="text-xs px-2 py-0.5 rounded-full bg-emerald-500/20 text-emerald-400">Active</span>
                    </div>
                    <p className="text-xs text-gray-500">{model.description}</p>
                  </div>
                ))}
              </div>
            </div>

            <div className="glass-card p-6">
              <h3 className="font-semibold mb-4 flex items-center gap-2">
                <Shield className="w-4 h-4 text-primary" />
                Data Sources
              </h3>
              <div className="space-y-2 text-sm">
                {[
                  ['Finnhub','Real-time quotes + news'],
                  ['NewsAPI','Market news sentiment'],
                  ['Claude Sonnet','Deep AI analysis'],
                  ['sklearn ML','Predictive scoring'],
                ].map(([src, desc]) => (
                  <div key={src} className="flex justify-between items-center py-1 border-b border-gray-800">
                    <span className="font-medium text-primary">{src}</span>
                    <span className="text-gray-500 text-xs">{desc}</span>
                  </div>
                ))}
              </div>
            </div>
          </motion.div>
        </div>
      </div>
    </div>
  )
}
