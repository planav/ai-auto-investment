import { useState, useEffect } from 'react'
import { useParams, Link, useNavigate } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import {
  Plus,
  TrendingUp,
  TrendingDown,
  PieChart,
  Activity,
  Brain,
  ArrowRight,
  AlertCircle,
  CheckCircle,
  Loader2,
  Sparkles,
  Wallet,
  Target,
  BarChart3,
  RefreshCw,
  Layers,
  ChevronRight,
  X,
  DollarSign,
  Hash,
  Trash2
} from 'lucide-react'
import { portfolioApi, walletApi, portfolioExtApi } from '../services/api'
import PortfolioChart from '../components/PortfolioChart'
import AssetAllocation from '../components/AssetAllocation'
import toast from 'react-hot-toast'

export default function Portfolio() {
  const { id } = useParams()
  const navigate = useNavigate()
  
  const [portfolios, setPortfolios] = useState([])
  const [selectedPortfolio, setSelectedPortfolio] = useState(null)
  const [activeTab, setActiveTab] = useState('overview')
  const [isLoading, setIsLoading] = useState(true)
  const [isRefreshing, setIsRefreshing] = useState(false)
  const [performance, setPerformance] = useState(null)
  const [walletBalance, setWalletBalance] = useState(0)
  const [chartData, setChartData] = useState([])
  const [reasoning, setReasoning] = useState(null)
  const [lastRefreshed, setLastRefreshed] = useState(null)
  // Sell modal state
  const [sellModal, setSellModal]     = useState(null)   // { holding }
  const [sellType, setSellType]       = useState('all')  // 'all' | 'quantity' | 'amount'
  const [sellValue, setSellValue]     = useState('')
  const [isSelling, setIsSelling]     = useState(false)

  // On mount and whenever the portfolio id changes: load portfolios, then
  // silently refresh live prices in the background.
  useEffect(() => {
    fetchPortfolios()
  }, [id])

  // Auto-refresh prices every 5 minutes while the page is open
  useEffect(() => {
    const FIVE_MIN = 5 * 60 * 1000
    const interval = setInterval(() => {
      silentRefreshPrices()
    }, FIVE_MIN)
    return () => clearInterval(interval)
  }, [selectedPortfolio])

  const fetchPortfolios = async () => {
    try {
      setIsLoading(true)
      
      const [portfoliosRes, walletRes] = await Promise.all([
        portfolioApi.getAll(),
        walletApi.getBalance()
      ])
      
      const portfoliosData = portfoliosRes.data || []
      setPortfolios(portfoliosData)
      setWalletBalance(walletRes.data?.balance || 0)
      
      if (id && portfoliosData.length > 0) {
        const found = portfoliosData.find(p => p.id === parseInt(id))
        if (found) {
          setSelectedPortfolio(found)
          fetchPerformance(found.id)
          fetchChartAndReasoning(found.id)
          // Auto-refresh prices in background so user sees latest market values
          silentRefreshPrices(found.id)
        }
      } else if (portfoliosData.length > 0) {
        setSelectedPortfolio(portfoliosData[0])
        fetchPerformance(portfoliosData[0].id)
        fetchChartAndReasoning(portfoliosData[0].id)
        // Auto-refresh prices in background
        silentRefreshPrices(portfoliosData[0].id)
      }
    } catch (error) {
      console.error('Error fetching portfolios:', error)
      toast.error('Failed to load portfolios')
    } finally {
      setIsLoading(false)
    }
  }

  // Silent background refresh — no toast, no loading spinner
  const silentRefreshPrices = async (portfolioId) => {
    const pid = portfolioId || selectedPortfolio?.id
    if (!pid) return
    try {
      const res = await portfolioExtApi.refreshPrices(pid)
      if (res.data?.portfolio) {
        setSelectedPortfolio(res.data.portfolio)
        setLastRefreshed(new Date())
      }
      // Refresh chart data too (new snapshot was written)
      const chartRes = await portfolioExtApi.getChart(pid).catch(() => null)
      if (chartRes?.data?.chart_data) setChartData(chartRes.data.chart_data)
    } catch {
      // Silently ignore — user still sees last known values
    }
  }

  const fetchPerformance = async (portfolioId) => {
    try {
      const perfRes = await portfolioApi.getPerformance(portfolioId)
      setPerformance(perfRes.data)
    } catch {
      setPerformance(null)
    }
  }

  const fetchChartAndReasoning = async (portfolioId) => {
    try {
      const [chartRes, reasonRes] = await Promise.all([
        portfolioExtApi.getChart(portfolioId).catch(() => null),
        portfolioExtApi.getReasoning(portfolioId).catch(() => null),
      ])
      if (chartRes?.data?.chart_data) setChartData(chartRes.data.chart_data)
      if (reasonRes?.data) setReasoning(reasonRes.data)
    } catch (e) {
      console.log('Chart/reasoning not available', e)
    }
  }

  const handleRefreshPrices = async () => {
    if (!selectedPortfolio) return
    setIsRefreshing(true)
    try {
      const res = await portfolioExtApi.refreshPrices(selectedPortfolio.id)
      if (res.data?.portfolio) {
        setSelectedPortfolio(res.data.portfolio)
        toast.success(`Prices refreshed — portfolio value: $${res.data.new_total_value?.toLocaleString()}`)
      }
      await fetchPortfolios()
    } catch (e) {
      toast.error('Failed to refresh prices')
    } finally {
      setIsRefreshing(false)
    }
  }

  const openSellModal = (holding) => {
    setSellModal(holding)
    setSellType('all')
    setSellValue('')
  }

  const computeSellProceeds = () => {
    if (!sellModal) return 0
    const price = sellModal.current_price
    if (sellType === 'all')      return sellModal.market_value
    if (sellType === 'quantity') return (parseFloat(sellValue) || 0) * price
    if (sellType === 'amount')   return parseFloat(sellValue) || 0
    return 0
  }

  const handleSell = async () => {
    if (!sellModal || !selectedPortfolio) return
    setIsSelling(true)
    try {
      const body = { symbol: sellModal.symbol }
      if (sellType === 'all')      body.sell_all  = true
      else if (sellType === 'quantity') body.quantity = parseFloat(sellValue)
      else if (sellType === 'amount')   body.amount   = parseFloat(sellValue)

      const res = await portfolioExtApi.sell(selectedPortfolio.id, body)
      setSelectedPortfolio(res.data)
      setSellModal(null)
      const proceeds = computeSellProceeds()
      toast.success(`Sold ${sellModal.symbol} — $${proceeds.toFixed(2)} added to wallet`)
      await fetchPortfolios()
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Sell failed. Please try again.')
    } finally {
      setIsSelling(false)
    }
  }

  const handleSelectPortfolio = (portfolio) => {
    setSelectedPortfolio(portfolio)
    navigate(`/portfolio/${portfolio.id}`)
    fetchPerformance(portfolio.id)
    fetchChartAndReasoning(portfolio.id)
    silentRefreshPrices(portfolio.id)
  }

  const holdings = selectedPortfolio?.holdings || []

  // Current portfolio value — authoritative from DB, updated on every price refresh
  const totalValue = selectedPortfolio?.total_value || 0
  const invested   = selectedPortfolio?.invested_amount || 0

  // P&L = how much the $invested has grown (or shrunk) in total
  // This is the only metric that's always consistent regardless of how/when
  // the portfolio was created.
  const totalReturn    = totalValue - invested
  const totalReturnPct = invested > 0 ? (totalReturn / invested) * 100 : 0

  const getSignalDisplay = (holding) => {
    if (holding.signal_strength === 'strong_buy') return { text: 'Strong Buy', color: 'bg-success/20 text-success' }
    if (holding.signal_strength === 'buy') return { text: 'Buy', color: 'bg-primary/20 text-primary' }
    if (holding.signal_strength === 'sell') return { text: 'Sell', color: 'bg-danger/20 text-danger' }
    if (holding.signal_strength === 'strong_sell') return { text: 'Strong Sell', color: 'bg-danger/20 text-danger' }
    return { text: 'Hold', color: 'bg-gray-700 text-gray-400' }
  }

  const generateAiInsights = () => {
    if (!holdings || holdings.length === 0) return []
    
    return holdings
      .filter(h => h.symbol !== 'CASH' && h.confidence_score > 0.7)
      .map(holding => ({
        type: holding.predicted_return > 0.05 ? 'buy' : holding.predicted_return < -0.05 ? 'reduce' : 'hold',
        symbol: holding.symbol,
        confidence: Math.round((holding.confidence_score || 0.5) * 100),
        reason: holding.predicted_return > 0.05 
          ? `Strong predicted return of ${(holding.predicted_return * 100).toFixed(1)}%`
          : holding.predicted_return < -0.05
          ? `Negative outlook with ${(holding.predicted_return * 100).toFixed(1)}% predicted return`
          : 'Stable performance expected',
      }))
      .slice(0, 5)
  }

  const aiInsights = generateAiInsights()

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center pt-20">
        <div className="flex items-center gap-2">
          <Loader2 className="w-6 h-6 text-primary animate-spin" />
          <span className="text-gray-400">Loading portfolios...</span>
        </div>
      </div>
    )
  }

  if (portfolios.length === 0) {
    return (
      <div className="pt-24 pb-12 px-4">
        <div className="max-w-7xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-center"
          >
            <div className="w-24 h-24 rounded-full bg-primary/10 flex items-center justify-center mx-auto mb-6">
              <Sparkles className="w-12 h-12 text-primary" />
            </div>
            <h1 className="text-3xl font-bold font-display mb-4">No Portfolios Yet</h1>
            <p className="text-gray-400 mb-8 max-w-md mx-auto">
              Create your first AI-powered portfolio to start investing. Our ML models will optimize your allocation.
            </p>
            <div className="flex items-center justify-center gap-4">
              {walletBalance > 0 ? (
                <Link to="/invest" className="btn-primary inline-flex items-center gap-2">
                  <Brain className="w-5 h-5" />
                  Create Portfolio
                </Link>
              ) : (
                <Link to="/deposit-withdraw" className="btn-secondary inline-flex items-center gap-2">
                  <Wallet className="w-5 h-5" />
                  Deposit Funds First
                </Link>
              )}
            </div>
            {walletBalance === 0 && (
              <p className="text-sm text-gray-500 mt-4">
                You need to add funds to your wallet before creating a portfolio
              </p>
            )}
          </motion.div>
        </div>
      </div>
    )
  }

  return (
    <div className="pt-24 pb-12 px-4">
      <div className="max-w-7xl mx-auto">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-6"
        >
          <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
            <div>
              <h1 className="text-3xl font-bold font-display mb-1">Portfolios</h1>
              <p className="text-gray-400 text-sm">
                {portfolios.length} portfolio{portfolios.length !== 1 ? 's' : ''} • Total Value: ${portfolios.reduce((sum, p) => sum + (p.total_value || 0), 0).toLocaleString()}
              </p>
            </div>
            <div className="flex items-center gap-3">
              <div className="flex flex-col items-end">
                <button
                  onClick={handleRefreshPrices}
                  disabled={isRefreshing}
                  title="Refresh live prices from Finnhub"
                  className="flex items-center gap-2 px-3 py-2 bg-dark-lighter rounded-lg hover:bg-primary/10 hover:text-primary transition-colors text-sm disabled:opacity-50"
                >
                  <RefreshCw className={`w-4 h-4 ${isRefreshing ? 'animate-spin' : ''}`} />
                  {isRefreshing ? 'Refreshing…' : 'Refresh Prices'}
                </button>
                {lastRefreshed && (
                  <span className="text-xs text-gray-500 mt-0.5 pr-1">
                    Updated {lastRefreshed.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                  </span>
                )}
              </div>
              <button
                onClick={fetchPortfolios}
                className="p-2 bg-dark-lighter rounded-lg hover:bg-gray-800 transition-colors"
              >
                <RefreshCw className="w-4 h-4" />
              </button>
              <Link to="/invest" className="btn-primary">
                <Plus className="w-4 h-4 inline-block mr-2" />
                New Portfolio
              </Link>
            </div>
          </div>
        </motion.div>

        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="lg:col-span-1"
          >
            <div className="glass-card p-4">
              <h2 className="text-sm font-medium text-gray-400 mb-3">Your Portfolios</h2>
              <div className="space-y-2">
                {portfolios.map((portfolio) => (
                  <button
                    key={portfolio.id}
                    onClick={() => handleSelectPortfolio(portfolio)}
                    className={`w-full p-3 rounded-lg text-left transition-all ${
                      selectedPortfolio?.id === portfolio.id
                        ? 'bg-primary/20 border border-primary/50'
                        : 'bg-dark-lighter hover:bg-gray-800 border border-transparent'
                    }`}
                  >
                    <div className="flex items-center justify-between">
                      <div>
                        <div className="font-medium text-sm">{portfolio.name}</div>
                        <div className="text-xs text-gray-400">
                          ${(portfolio.total_value || 0).toLocaleString()}
                        </div>
                      </div>
                      <ChevronRight className={`w-4 h-4 ${
                        selectedPortfolio?.id === portfolio.id ? 'text-primary' : 'text-gray-600'
                      }`} />
                    </div>
                  </button>
                ))}
              </div>
            </div>

            <div className="glass-card p-4 mt-4">
              <h2 className="text-sm font-medium text-gray-400 mb-3">Quick Actions</h2>
              <div className="space-y-2">
                <Link
                  to="/deposit-withdraw"
                  className="flex items-center gap-3 p-3 bg-dark-lighter rounded-lg hover:bg-gray-800 transition-colors"
                >
                  <Wallet className="w-5 h-5 text-success" />
                  <div>
                    <div className="text-sm font-medium">Add Funds</div>
                    <div className="text-xs text-gray-500">${walletBalance.toLocaleString()} available</div>
                  </div>
                </Link>
                <Link
                  to="/analysis"
                  className="flex items-center gap-3 p-3 bg-dark-lighter rounded-lg hover:bg-gray-800 transition-colors"
                >
                  <Brain className="w-5 h-5 text-primary" />
                  <div>
                    <div className="text-sm font-medium">AI Analysis</div>
                    <div className="text-xs text-gray-500">Analyze stocks</div>
                  </div>
                </Link>
                <Link
                  to="/dashboard"
                  className="flex items-center gap-3 p-3 bg-dark-lighter rounded-lg hover:bg-gray-800 transition-colors"
                >
                  <BarChart3 className="w-5 h-5 text-secondary" />
                  <div>
                    <div className="text-sm font-medium">Dashboard</div>
                    <div className="text-xs text-gray-500">Overview</div>
                  </div>
                </Link>
              </div>
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="lg:col-span-3"
          >
            {selectedPortfolio && (
              <>
                <div className="mb-6">
                  <div className="flex items-center gap-3 mb-2 flex-wrap">
                    <h2 className="text-2xl font-bold font-display">{selectedPortfolio.name}</h2>
                    <span className="flex items-center gap-1 text-xs px-2 py-1 bg-primary/20 text-primary rounded-full">
                      <Brain className="w-3 h-3" />
                      Claude Sonnet AI
                    </span>
                    <span className="text-xs px-2 py-1 bg-emerald-500/10 text-emerald-400 rounded-full capitalize">
                      {selectedPortfolio.risk_profile} risk
                    </span>
                  </div>
                  {/* Show market context from when Claude analysed — proves real AI ran */}
                  {selectedPortfolio.market_context && (
                    <div className="mt-2 p-3 bg-primary/5 border border-primary/10 rounded-xl text-xs text-gray-400 leading-relaxed">
                      <span className="text-primary font-medium">Claude's market analysis at creation: </span>
                      {selectedPortfolio.market_context}
                    </div>
                  )}
                  <div className="flex items-center gap-4 text-sm text-gray-400 mt-2">
                    <span>{holdings.length} holdings</span>
                    <span>•</span>
                    <span className="capitalize">{selectedPortfolio.model_type?.replace(/_/g, ' ') || 'Standard'}</span>
                  </div>
                </div>

                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">

                  {/* Current Value — always total_value from DB */}
                  <div className="glass-card p-4 border border-primary/10">
                    <div className="text-gray-400 text-xs mb-1">Current Value</div>
                    <div className="text-xl font-bold font-display">
                      ${Number(totalValue).toLocaleString(undefined,{minimumFractionDigits:2,maximumFractionDigits:2})}
                    </div>
                    <div className="text-xs text-gray-500 mt-0.5">
                      Invested: ${Number(invested).toLocaleString(undefined,{minimumFractionDigits:2,maximumFractionDigits:2})}
                    </div>
                  </div>

                  {/* Total Return = current_value − invested (the only consistent metric) */}
                  <div className={`glass-card p-4 border ${totalReturn >= 0 ? 'border-emerald-500/20' : 'border-red-500/20'}`}>
                    <div className="text-gray-400 text-xs mb-1">Total Return</div>
                    <div className={`text-xl font-bold font-display ${totalReturn >= 0 ? 'text-emerald-400' : 'text-red-400'}`}>
                      {totalReturn >= 0 ? '+' : ''}{Number(totalReturn).toLocaleString(undefined,{minimumFractionDigits:2,maximumFractionDigits:2})}
                    </div>
                    <div className={`text-xs ${totalReturn >= 0 ? 'text-emerald-500' : 'text-red-500'}`}>
                      {totalReturn >= 0 ? '+' : ''}{Number(totalReturnPct).toFixed(2)}% on invested
                    </div>
                  </div>

                  {/* Day / since-last-refresh change per stock (sum of price moves) */}
                  {(() => {
                    const priceMove = holdings.reduce((s, h) =>
                      h.asset_type === 'cash' ? s : s + (h.current_price - h.avg_price) * h.quantity, 0)
                    const pos = priceMove >= 0
                    return (
                      <div className="glass-card p-4">
                        <div className="text-gray-400 text-xs mb-1">Price Gain on Shares</div>
                        <div className={`text-xl font-bold font-display ${pos ? 'text-emerald-400' : 'text-red-400'}`}>
                          {pos ? '+' : ''}{Number(priceMove).toLocaleString(undefined,{minimumFractionDigits:2,maximumFractionDigits:2})}
                        </div>
                        <div className={`text-xs ${pos ? 'text-emerald-500' : 'text-red-500'}`}>
                          Since purchase (each stock)
                        </div>
                      </div>
                    )
                  })()}

                  {/* AI Expected Return */}
                  <div className="glass-card p-4">
                    <div className="text-gray-400 text-xs mb-1">AI Expected Return</div>
                    <div className="text-xl font-bold font-display text-primary">
                      +{((selectedPortfolio?.expected_return || 0) * 100).toFixed(1)}%
                    </div>
                    <div className="text-xs text-gray-400">Annualised forecast</div>
                  </div>

                </div>

                {/* Explain any gap between "Total Return" and "Price Gain on Shares" for old portfolios */}
                {Math.abs((totalValue - invested) - holdings.reduce((s,h)=>h.asset_type==='cash'?s:s+(h.current_price-h.avg_price)*h.quantity,0)) > 1 && (
                  <div className="mb-4 px-4 py-2 bg-yellow-500/5 border border-yellow-500/20 rounded-lg text-xs text-gray-500">
                    ℹ️ "Total Return" reflects your $
                    {Number(invested).toLocaleString(undefined,{minimumFractionDigits:2})} investment.
                    "Price Gain on Shares" shows price appreciation of individual stocks since purchase.
                    These differ slightly for this portfolio — create a new portfolio to see them in sync.
                  </div>
                )}

                <div className="flex gap-2 mb-6">
                  {['overview', 'holdings', 'ai-insights', 'performance'].map((tab) => (
                    <button
                      key={tab}
                      onClick={() => setActiveTab(tab)}
                      className={`px-4 py-2 rounded-lg capitalize text-sm transition-colors ${
                        activeTab === tab
                          ? 'bg-primary text-dark font-medium'
                          : 'text-gray-400 hover:text-white hover:bg-dark-lighter'
                      }`}
                    >
                      {tab.replace('-', ' ')}
                    </button>
                  ))}
                </div>

                <AnimatePresence mode="wait">
                  {activeTab === 'overview' && (
                    <motion.div
                      key="overview"
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      exit={{ opacity: 0, y: -20 }}
                      className="grid grid-cols-1 lg:grid-cols-3 gap-6"
                    >
                      <div className="lg:col-span-2 glass-card p-6">
                        <div className="flex items-center justify-between mb-4">
                          <h3 className="text-lg font-semibold">Portfolio Performance</h3>
                          <span className="text-xs text-gray-500">
                            Click "Refresh Prices" to update live values
                          </span>
                        </div>
                        <PortfolioChart
                          chartData={chartData}
                          invested={selectedPortfolio?.invested_amount || 0}
                        />
                      </div>
                      <div className="glass-card p-6">
                        <h3 className="text-lg font-semibold mb-4">Allocation</h3>
                        <AssetAllocation holdings={holdings} />
                      </div>
                    </motion.div>
                  )}

                  {activeTab === 'holdings' && (
                    <motion.div
                      key="holdings"
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      exit={{ opacity: 0, y: -20 }}
                      className="glass-card overflow-hidden"
                    >
                      {holdings.length > 0 ? (
                        <div className="overflow-x-auto">
                        <table className="w-full min-w-[900px]">
                          <thead className="bg-dark-lighter">
                            <tr>
                              <th className="text-left p-4 text-gray-400 font-medium">Asset</th>
                              <th className="text-right p-4 text-gray-400 font-medium">Weight</th>
                              <th className="text-right p-4 text-gray-400 font-medium">Qty</th>
                              <th className="text-right p-4 text-gray-400 font-medium">Avg Cost</th>
                              <th className="text-right p-4 text-gray-400 font-medium">Current</th>
                              <th className="text-right p-4 text-gray-400 font-medium">Value</th>
                              <th className="text-right p-4 text-gray-400 font-medium">P&L</th>
                              <th className="text-right p-4 text-gray-400 font-medium">Signal</th>
                              <th className="text-right p-4 text-gray-400 font-medium">Action</th>
                            </tr>
                          </thead>
                          <tbody>
                            {holdings.map((holding, index) => {
                              const signal = getSignalDisplay(holding)
                              const isCash = holding.asset_type === 'cash'
                              const pnlDollar = isCash ? 0 : (holding.current_price - holding.avg_price) * holding.quantity
                              const pnlPct    = isCash || holding.avg_price === 0 ? 0
                                : ((holding.current_price - holding.avg_price) / holding.avg_price) * 100
                              const pnlPos    = pnlDollar >= 0
                              return (
                                <tr key={index} className="border-t border-gray-800 hover:bg-dark-lighter/50 transition-colors">
                                  <td className="p-4">
                                    <div className="flex items-center gap-3">
                                      <div className={`w-9 h-9 rounded-lg flex items-center justify-center text-sm font-bold ${
                                        isCash ? 'bg-gray-700 text-gray-400' : 'bg-primary/10 text-primary'
                                      }`}>
                                        {holding.symbol[0]}
                                      </div>
                                      <div>
                                        <div className="font-medium text-sm">{holding.symbol}</div>
                                        <div className="text-xs text-gray-500 capitalize">{holding.asset_type}</div>
                                      </div>
                                    </div>
                                  </td>
                                  <td className="p-4 text-right text-sm">{(holding.weight * 100).toFixed(1)}%</td>
                                  <td className="p-4 text-right text-sm">{holding.quantity?.toFixed(4)}</td>
                                  <td className="p-4 text-right text-sm text-gray-400">${holding.avg_price?.toFixed(2)}</td>
                                  <td className="p-4 text-right text-sm">${holding.current_price?.toFixed(2)}</td>
                                  <td className="p-4 text-right text-sm font-medium">${holding.market_value?.toLocaleString(undefined,{maximumFractionDigits:2})}</td>
                                  <td className="p-4 text-right">
                                    {isCash ? (
                                      <span className="text-gray-500 text-xs">—</span>
                                    ) : (
                                      <div>
                                        <div className={`text-sm font-medium ${pnlPos ? 'text-emerald-400' : 'text-red-400'}`}>
                                          {pnlPos ? '+' : ''}{pnlDollar.toFixed(2)}
                                        </div>
                                        <div className={`text-xs ${pnlPos ? 'text-emerald-500' : 'text-red-500'}`}>
                                          {pnlPos ? '+' : ''}{pnlPct.toFixed(2)}%
                                        </div>
                                      </div>
                                    )}
                                  </td>
                                  <td className="p-4 text-right">
                                    <span className={`px-2 py-1 rounded-full text-xs ${signal.color}`}>
                                      {signal.text}
                                    </span>
                                  </td>
                                  <td className="p-4 text-right">
                                    {!isCash && (
                                      <button
                                        onClick={() => openSellModal(holding)}
                                        className="px-3 py-1.5 text-xs font-medium bg-red-500/10 text-red-400 hover:bg-red-500/20 rounded-lg transition-colors"
                                      >
                                        Sell
                                      </button>
                                    )}
                                  </td>
                                </tr>
                              )
                            })}
                          </tbody>
                        </table>
                        </div>
                      ) : (
                        <div className="text-center py-12">
                          <Sparkles className="w-12 h-12 mx-auto mb-4 text-primary/50" />
                          <p className="text-gray-400 mb-4">No holdings yet</p>
                          <Link to="/invest" className="btn-primary inline-block">
                            Generate AI Portfolio
                          </Link>
                        </div>
                      )}
                    </motion.div>
                  )}

                  {activeTab === 'ai-insights' && (
                    <motion.div
                      key="ai-insights"
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      exit={{ opacity: 0, y: -20 }}
                      className="space-y-4"
                    >
                      {/* Market Context */}
                      {(reasoning?.market_context || selectedPortfolio?.market_context) && (
                        <div className="glass-card p-5 border border-primary/20">
                          <div className="flex items-center gap-2 mb-3">
                            <Activity className="w-4 h-4 text-primary" />
                            <h3 className="font-semibold text-primary">Market Context (at time of creation)</h3>
                          </div>
                          <p className="text-gray-300 text-sm leading-relaxed">
                            {reasoning?.market_context || selectedPortfolio?.market_context}
                          </p>
                        </div>
                      )}

                      {/* Per-stock Claude reasoning */}
                      {(reasoning?.stock_reasoning || selectedPortfolio?.stock_reasoning) && (
                        <div className="glass-card p-5 border border-secondary/20">
                          <div className="flex items-center gap-2 mb-3">
                            <Brain className="w-4 h-4 text-secondary" />
                            <h3 className="font-semibold text-secondary">Claude AI — Why Each Stock Was Chosen</h3>
                          </div>
                          <div className="space-y-3">
                            {(reasoning?.stock_reasoning || selectedPortfolio?.stock_reasoning || '')
                              .split('\n')
                              .filter(line => line.trim())
                              .map((line, i) => {
                                // Parse "SYMBOL: reason text" → bold symbol + plain reason
                                const match = line.match(/^([A-Z0-9]+):\s*(.*)/)
                                return (
                                  <div key={i} className="flex items-start gap-2 text-sm p-2 rounded-lg bg-dark hover:bg-white/5 transition-colors">
                                    <span className="text-primary mt-0.5 flex-shrink-0">▸</span>
                                    <span className="leading-relaxed">
                                      {match ? (
                                        <>
                                          <span className="font-semibold text-white">{match[1]}: </span>
                                          <span className="text-gray-300">{match[2]}</span>
                                        </>
                                      ) : (
                                        <span className="text-gray-300">{line}</span>
                                      )}
                                    </span>
                                  </div>
                                )
                              })}
                          </div>
                        </div>
                      )}

                      {/* ML signals per holding */}
                      {aiInsights.length > 0 && (
                        <div className="glass-card p-5">
                          <div className="flex items-center gap-2 mb-3">
                            <TrendingUp className="w-4 h-4 text-accent" />
                            <h3 className="font-semibold text-accent">ML Model Signals</h3>
                          </div>
                          <div className="space-y-3">
                            {aiInsights.map((insight, i) => (
                              <div key={i} className="flex items-start gap-3 p-3 bg-dark-lighter rounded-lg">
                                <span className={`text-xs px-2 py-1 rounded-full font-medium ${
                                  insight.type === 'buy' ? 'bg-success/20 text-success' :
                                  insight.type === 'reduce' ? 'bg-warning/20 text-warning' :
                                  'bg-primary/20 text-primary'
                                }`}>{insight.type.toUpperCase()}</span>
                                <div>
                                  <span className="font-semibold mr-2">{insight.symbol}</span>
                                  <span className="text-gray-400 text-sm">{insight.reason}</span>
                                  <span className="text-xs text-gray-500 ml-2">({insight.confidence}% confidence)</span>
                                </div>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}

                      {!reasoning?.stock_reasoning && !selectedPortfolio?.stock_reasoning && aiInsights.length === 0 && (
                        <div className="glass-card p-12 text-center">
                          <Brain className="w-12 h-12 mx-auto mb-4 text-gray-600" />
                          <p className="text-gray-400">AI insights will appear here after portfolio creation</p>
                        </div>
                      )}
                    </motion.div>
                  )}

                  {activeTab === 'performance' && (
                    <motion.div
                      key="performance"
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      exit={{ opacity: 0, y: -20 }}
                      className="grid grid-cols-1 md:grid-cols-2 gap-6"
                    >
                      <div className="glass-card p-6">
                        <h3 className="text-lg font-semibold mb-4">Risk Metrics</h3>
                        <div className="space-y-4">
                          {[
                            { 
                              label: 'Volatility', 
                              value: selectedPortfolio.volatility ? `${(selectedPortfolio.volatility * 100).toFixed(1)}%` : 'N/A', 
                              color: selectedPortfolio.volatility && selectedPortfolio.volatility > 0.2 ? 'text-warning' : 'text-primary' 
                            },
                            { 
                              label: 'Sharpe Ratio', 
                              value: selectedPortfolio.sharpe_ratio ? selectedPortfolio.sharpe_ratio.toFixed(2) : 'N/A', 
                              color: selectedPortfolio.sharpe_ratio && selectedPortfolio.sharpe_ratio > 1 ? 'text-success' : 'text-primary' 
                            },
                            { 
                              label: 'Max Drawdown', 
                              value: selectedPortfolio.max_drawdown ? `${(selectedPortfolio.max_drawdown * 100).toFixed(1)}%` : 'N/A', 
                              color: 'text-warning' 
                            },
                            { 
                              label: 'VaR (95%)', 
                              value: selectedPortfolio.var_95 ? `${(selectedPortfolio.var_95 * 100).toFixed(1)}%` : 'N/A', 
                              color: 'text-danger' 
                            },
                            { 
                              label: 'CVaR (95%)', 
                              value: selectedPortfolio.cvar_95 ? `${(selectedPortfolio.cvar_95 * 100).toFixed(1)}%` : 'N/A', 
                              color: 'text-danger' 
                            },
                          ].map((metric, index) => (
                            <div key={index} className="flex items-center justify-between p-3 bg-dark-lighter rounded-lg">
                              <span className="text-gray-400">{metric.label}</span>
                              <span className={`font-bold ${metric.color}`}>{metric.value}</span>
                            </div>
                          ))}
                        </div>
                      </div>

                      <div className="glass-card p-6">
                        <h3 className="text-lg font-semibold mb-4">AI Portfolio Explanation</h3>
                        <div className="space-y-4">
                          <p className="text-gray-300 text-sm leading-relaxed">
                            {selectedPortfolio.ai_explanation || 'Claude AI analysis will appear after portfolio creation.'}
                          </p>
                          {selectedPortfolio.expected_return && (
                            <div className="p-4 bg-dark-lighter rounded-lg">
                              <div className="flex items-center justify-between mb-2">
                                <span className="text-gray-400">Expected Annual Return</span>
                                <span className="text-success font-bold">
                                  +{(selectedPortfolio.expected_return * 100).toFixed(1)}%
                                </span>
                              </div>
                              <div className="w-full bg-gray-800 rounded-full h-2">
                                <div 
                                  className="bg-success h-2 rounded-full" 
                                  style={{ width: `${Math.min(100, Math.max(0, selectedPortfolio.expected_return * 100 * 2))}%` }}
                                />
                              </div>
                            </div>
                          )}
                        </div>
                      </div>
                    </motion.div>
                  )}
                </AnimatePresence>
              </>
            )}
          </motion.div>
        </div>
      </div>
      {/* ── Sell Modal ─────────────────────────────────────────────────────── */}
      <AnimatePresence>
        {sellModal && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/70 z-50 flex items-center justify-center p-4"
            onClick={(e) => { if (e.target === e.currentTarget) setSellModal(null) }}
          >
            <motion.div
              initial={{ scale: 0.95, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.95, opacity: 0 }}
              className="glass-card p-6 w-full max-w-md border border-red-500/30"
            >
              {/* Header */}
              <div className="flex items-center justify-between mb-5">
                <div>
                  <h3 className="text-xl font-bold">Sell {sellModal.symbol}</h3>
                  <p className="text-gray-400 text-sm capitalize">{sellModal.asset_type} · {sellModal.sector || 'N/A'}</p>
                </div>
                <button onClick={() => setSellModal(null)} className="text-gray-500 hover:text-white transition-colors">
                  <X className="w-6 h-6" />
                </button>
              </div>

              {/* Price info */}
              <div className="grid grid-cols-3 gap-3 mb-5">
                <div className="bg-dark-lighter p-3 rounded-xl text-center">
                  <div className="text-xs text-gray-500 mb-1">Current Price</div>
                  <div className="font-bold">${sellModal.current_price?.toFixed(2)}</div>
                </div>
                <div className="bg-dark-lighter p-3 rounded-xl text-center">
                  <div className="text-xs text-gray-500 mb-1">You Own</div>
                  <div className="font-bold">{sellModal.quantity?.toFixed(4)} sh</div>
                </div>
                <div className="bg-dark-lighter p-3 rounded-xl text-center">
                  <div className="text-xs text-gray-500 mb-1">Market Value</div>
                  <div className="font-bold">${sellModal.market_value?.toFixed(2)}</div>
                </div>
              </div>

              {/* Sell type selector */}
              <div className="mb-4">
                <div className="text-sm text-gray-400 mb-2">Sell by</div>
                <div className="flex gap-2">
                  {[
                    { id: 'all',      label: 'All',      icon: Trash2 },
                    { id: 'quantity', label: 'Quantity',  icon: Hash },
                    { id: 'amount',   label: 'Amount $',  icon: DollarSign },
                  ].map(({ id, label, icon: Icon }) => (
                    <button
                      key={id}
                      onClick={() => { setSellType(id); setSellValue('') }}
                      className={`flex-1 py-2 px-3 rounded-lg text-sm font-medium flex items-center justify-center gap-1.5 transition-colors ${
                        sellType === id
                          ? 'bg-red-500/20 text-red-400 border border-red-500/40'
                          : 'bg-dark-lighter text-gray-400 hover:text-white'
                      }`}
                    >
                      <Icon className="w-3.5 h-3.5" />
                      {label}
                    </button>
                  ))}
                </div>
              </div>

              {/* Input */}
              {sellType !== 'all' && (
                <div className="mb-4">
                  <div className="relative">
                    {sellType === 'amount' && (
                      <span className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500">$</span>
                    )}
                    <input
                      type="number"
                      value={sellValue}
                      onChange={(e) => setSellValue(e.target.value)}
                      placeholder={sellType === 'quantity' ? `Max ${sellModal.quantity?.toFixed(4)}` : `Max $${sellModal.market_value?.toFixed(2)}`}
                      min="0"
                      step={sellType === 'quantity' ? '0.0001' : '0.01'}
                      max={sellType === 'quantity' ? sellModal.quantity : sellModal.market_value}
                      className={`w-full py-3 bg-dark-lighter border border-gray-700 rounded-xl focus:outline-none focus:border-red-400 transition-colors ${sellType === 'amount' ? 'pl-7 pr-4' : 'px-4'}`}
                    />
                  </div>
                  <div className="flex justify-between mt-1.5 text-xs text-gray-500">
                    <span>Min: {sellType === 'quantity' ? '0.0001 sh' : '$0.01'}</span>
                    <button
                      onClick={() => setSellValue(sellType === 'quantity' ? sellModal.quantity?.toFixed(4) : sellModal.market_value?.toFixed(2))}
                      className="text-red-400 hover:text-red-300"
                    >
                      Use max
                    </button>
                  </div>
                </div>
              )}

              {/* Proceeds preview */}
              <div className="bg-dark-lighter rounded-xl p-4 mb-5 flex items-center justify-between">
                <span className="text-gray-400 text-sm">You will receive</span>
                <span className="text-xl font-bold text-emerald-400">
                  ${computeSellProceeds().toFixed(2)}
                </span>
              </div>

              {/* P&L at sell price */}
              {(() => {
                const pnlAtSell = (sellModal.current_price - sellModal.avg_price) *
                  (sellType === 'all' ? sellModal.quantity : sellType === 'quantity' ? (parseFloat(sellValue) || 0) : (parseFloat(sellValue) || 0) / sellModal.current_price)
                const pos = pnlAtSell >= 0
                return (
                  <div className={`text-center text-xs mb-4 ${pos ? 'text-emerald-400' : 'text-red-400'}`}>
                    {pos ? 'Realised gain' : 'Realised loss'}: {pos ? '+' : ''}${Math.abs(pnlAtSell).toFixed(2)} vs cost basis
                  </div>
                )
              })()}

              {/* Buttons */}
              <div className="flex gap-3">
                <button
                  onClick={() => setSellModal(null)}
                  className="flex-1 py-3 bg-dark-lighter rounded-xl text-gray-400 hover:text-white transition-colors"
                >
                  Cancel
                </button>
                <button
                  onClick={handleSell}
                  disabled={isSelling || (sellType !== 'all' && (!sellValue || parseFloat(sellValue) <= 0))}
                  className="flex-1 py-3 bg-red-500 hover:bg-red-600 text-white rounded-xl font-semibold transition-colors disabled:opacity-50 flex items-center justify-center gap-2"
                >
                  {isSelling ? <Loader2 className="w-4 h-4 animate-spin" /> : null}
                  {isSelling ? 'Selling…' : `Confirm Sell`}
                </button>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}
