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
  ChevronRight
} from 'lucide-react'
import { portfolioApi, walletApi } from '../services/api'
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
  const [performance, setPerformance] = useState(null)
  const [walletBalance, setWalletBalance] = useState(0)

  useEffect(() => {
    fetchPortfolios()
  }, [id])

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
        }
      } else if (portfoliosData.length > 0) {
        setSelectedPortfolio(portfoliosData[0])
        fetchPerformance(portfoliosData[0].id)
      }
    } catch (error) {
      console.error('Error fetching portfolios:', error)
      toast.error('Failed to load portfolios')
    } finally {
      setIsLoading(false)
    }
  }

  const fetchPerformance = async (portfolioId) => {
    try {
      const perfRes = await portfolioApi.getPerformance(portfolioId)
      setPerformance(perfRes.data)
    } catch {
      console.log('Performance data not available')
      setPerformance(null)
    }
  }

  const handleSelectPortfolio = (portfolio) => {
    setSelectedPortfolio(portfolio)
    navigate(`/portfolio/${portfolio.id}`)
    fetchPerformance(portfolio.id)
  }

  const totalValue = selectedPortfolio?.total_value || 0
  const holdings = selectedPortfolio?.holdings || []
  const totalReturn = performance?.total_return || 0
  const totalReturnPct = performance?.total_return_pct || 0
  
  const dayChange = holdings.reduce((sum, h) => {
    if (h.symbol === 'CASH') return sum
    const priceChange = (h.current_price - h.avg_price) * h.quantity
    return sum + priceChange
  }, 0)
  const dayChangePct = totalValue > 0 ? (dayChange / totalValue) * 100 : 0

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
                  <div className="flex items-center gap-3 mb-2">
                    <h2 className="text-2xl font-bold font-display">{selectedPortfolio.name}</h2>
                    <span className="flex items-center gap-1 text-xs px-2 py-1 bg-primary/20 text-primary rounded-full">
                      <Brain className="w-3 h-3" />
                      AI Optimized
                    </span>
                  </div>
                  <div className="flex items-center gap-4 text-sm text-gray-400">
                    <span>{holdings.length} holdings</span>
                    <span>•</span>
                    <span className="capitalize">{selectedPortfolio.model_type?.replace('_', ' ') || 'Standard'}</span>
                  </div>
                </div>

                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
                  <div className="glass-card p-4">
                    <div className="text-gray-400 text-xs mb-1">Total Value</div>
                    <div className="text-xl font-bold font-display">
                      ${totalValue.toLocaleString()}
                    </div>
                  </div>
                  <div className="glass-card p-4">
                    <div className="text-gray-400 text-xs mb-1">Total Return</div>
                    <div className={`text-xl font-bold font-display ${totalReturn >= 0 ? 'text-success' : 'text-danger'}`}>
                      {totalReturn >= 0 ? '+' : ''}${totalReturn.toLocaleString()}
                    </div>
                    <div className={`text-xs ${totalReturn >= 0 ? 'text-success' : 'text-danger'}`}>
                      {totalReturn >= 0 ? '+' : ''}{totalReturnPct.toFixed(2)}%
                    </div>
                  </div>
                  <div className="glass-card p-4">
                    <div className="text-gray-400 text-xs mb-1">Day Change</div>
                    <div className={`text-xl font-bold font-display ${dayChange >= 0 ? 'text-success' : 'text-danger'}`}>
                      {dayChange >= 0 ? '+' : ''}${dayChange.toLocaleString()}
                    </div>
                    <div className={`text-xs ${dayChange >= 0 ? 'text-success' : 'text-danger'}`}>
                      {dayChange >= 0 ? '+' : ''}{dayChangePct.toFixed(2)}%
                    </div>
                  </div>
                  <div className="glass-card p-4">
                    <div className="text-gray-400 text-xs mb-1">Expected Return</div>
                    <div className="text-xl font-bold font-display text-primary">
                      +{((selectedPortfolio.expected_return || 0) * 100).toFixed(1)}%
                    </div>
                    <div className="text-xs text-gray-400">Annual</div>
                  </div>
                </div>

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
                        <h3 className="text-lg font-semibold mb-4">Performance</h3>
                        <PortfolioChart portfolio={selectedPortfolio} />
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
                        <table className="w-full">
                          <thead className="bg-dark-lighter">
                            <tr>
                              <th className="text-left p-4 text-gray-400 font-medium">Asset</th>
                              <th className="text-right p-4 text-gray-400 font-medium">Weight</th>
                              <th className="text-right p-4 text-gray-400 font-medium">Quantity</th>
                              <th className="text-right p-4 text-gray-400 font-medium">Price</th>
                              <th className="text-right p-4 text-gray-400 font-medium">Value</th>
                              <th className="text-right p-4 text-gray-400 font-medium">AI Signal</th>
                            </tr>
                          </thead>
                          <tbody>
                            {holdings.map((holding, index) => {
                              const signal = getSignalDisplay(holding)
                              return (
                                <tr key={index} className="border-t border-gray-800 hover:bg-dark-lighter/50">
                                  <td className="p-4">
                                    <div className="flex items-center gap-3">
                                      <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${
                                        holding.asset_type === 'cash' ? 'bg-gray-700' : 'bg-primary/10'
                                      }`}>
                                        <span className={`font-bold ${holding.asset_type === 'cash' ? 'text-gray-400' : 'text-primary'}`}>
                                          {holding.symbol[0]}
                                        </span>
                                      </div>
                                      <div>
                                        <div className="font-medium">{holding.symbol}</div>
                                        <div className="text-sm text-gray-400 capitalize">{holding.asset_type}</div>
                                      </div>
                                    </div>
                                  </td>
                                  <td className="p-4 text-right">{(holding.weight * 100).toFixed(1)}%</td>
                                  <td className="p-4 text-right">{holding.quantity?.toFixed(2)}</td>
                                  <td className="p-4 text-right">${holding.current_price?.toFixed(2)}</td>
                                  <td className="p-4 text-right">${holding.market_value?.toLocaleString()}</td>
                                  <td className="p-4 text-right">
                                    <span className={`px-2 py-1 rounded-full text-xs ${signal.color}`}>
                                      {signal.text}
                                    </span>
                                  </td>
                                </tr>
                              )
                            })}
                          </tbody>
                        </table>
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
                      {aiInsights.length > 0 ? (
                        aiInsights.map((insight, index) => (
                          <div
                            key={index}
                            className="glass-card p-6 flex items-start gap-4"
                          >
                            <div className={`w-12 h-12 rounded-xl flex items-center justify-center ${
                              insight.type === 'buy' ? 'bg-success/20' :
                              insight.type === 'hold' ? 'bg-primary/20' :
                              'bg-warning/20'
                            }`}>
                              {insight.type === 'buy' ? <TrendingUp className="w-6 h-6 text-success" /> :
                               insight.type === 'hold' ? <CheckCircle className="w-6 h-6 text-primary" /> :
                               <AlertCircle className="w-6 h-6 text-warning" />}
                            </div>
                            <div className="flex-1">
                              <div className="flex items-center gap-3 mb-2">
                                <h3 className="text-lg font-semibold">{insight.symbol}</h3>
                                <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                                  insight.type === 'buy' ? 'bg-success/20 text-success' :
                                  insight.type === 'hold' ? 'bg-primary/20 text-primary' :
                                  'bg-warning/20 text-warning'
                                }`}>
                                  {insight.type.toUpperCase()}
                                </span>
                                <span className="text-sm text-gray-400">
                                  {insight.confidence}% confidence
                                </span>
                              </div>
                              <p className="text-gray-400">{insight.reason}</p>
                            </div>
                          </div>
                        ))
                      ) : (
                        <div className="glass-card p-12 text-center">
                          <Brain className="w-12 h-12 mx-auto mb-4 text-gray-600" />
                          <p className="text-gray-400">No AI insights available yet</p>
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
                          <p className="text-gray-400 text-sm leading-relaxed">
                            {selectedPortfolio.ai_explanation || 'AI analysis in progress...'}
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
    </div>
  )
}
