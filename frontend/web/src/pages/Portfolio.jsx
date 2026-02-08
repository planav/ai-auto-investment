import { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import { motion } from 'framer-motion'
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
  Wallet
} from 'lucide-react'
import { portfolioApi } from '../services/api'
import PortfolioChart from '../components/PortfolioChart'
import AssetAllocation from '../components/AssetAllocation'
import toast from 'react-hot-toast'

export default function Portfolio() {
  const { id } = useParams()
  const [activeTab, setActiveTab] = useState('overview')
  const [portfolio, setPortfolio] = useState(null)
  const [holdings, setHoldings] = useState([])
  const [isLoading, setIsLoading] = useState(true)
  const [performance, setPerformance] = useState(null)

  useEffect(() => {
    fetchPortfolioData()
  }, [id])

  const fetchPortfolioData = async () => {
    try {
      setIsLoading(true)
      
      if (id) {
        // Fetch specific portfolio
        const response = await portfolioApi.getById(id)
        if (response.data) {
          setPortfolio(response.data)
          setHoldings(response.data.holdings || [])
          
          // Fetch performance data
          try {
            const perfResponse = await portfolioApi.getPerformance(id)
            setPerformance(perfResponse.data)
          } catch (e) {
            console.log('Performance data not available')
          }
        }
      } else {
        // Fetch all portfolios and use the first one
        const response = await portfolioApi.getAll()
        if (response.data && response.data.length > 0) {
          const firstPortfolio = response.data[0]
          setPortfolio(firstPortfolio)
          setHoldings(firstPortfolio.holdings || [])
          
          // Fetch performance data
          try {
            const perfResponse = await portfolioApi.getPerformance(firstPortfolio.id)
            setPerformance(perfResponse.data)
          } catch (e) {
            console.log('Performance data not available')
          }
        }
      }
    } catch (error) {
      console.error('Error fetching portfolio:', error)
      toast.error('Failed to load portfolio data')
    } finally {
      setIsLoading(false)
    }
  }

  // Calculate real metrics from portfolio data
  const totalValue = portfolio?.total_value || 0
  const totalReturn = performance?.total_return || 0
  const totalReturnPct = performance?.total_return_pct || 0
  
  // Calculate day change from holdings
  const dayChange = holdings.reduce((sum, h) => {
    if (h.symbol === 'CASH') return sum
    const priceChange = (h.current_price - h.avg_price) * h.quantity
    return sum + priceChange
  }, 0)
  const dayChangePct = totalValue > 0 ? (dayChange / totalValue) * 100 : 0

  // Generate AI insights from real holding data
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

  // Get signal display for a holding
  const getSignalDisplay = (holding) => {
    if (holding.signal_strength === 'strong_buy') return { text: 'Strong Buy', color: 'bg-success/20 text-success' }
    if (holding.signal_strength === 'buy') return { text: 'Buy', color: 'bg-primary/20 text-primary' }
    if (holding.signal_strength === 'sell') return { text: 'Sell', color: 'bg-danger/20 text-danger' }
    if (holding.signal_strength === 'strong_sell') return { text: 'Strong Sell', color: 'bg-danger/20 text-danger' }
    return { text: 'Hold', color: 'bg-gray-700 text-gray-400' }
  }

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center pt-20">
        <div className="flex items-center gap-2">
          <Loader2 className="w-6 h-6 text-primary animate-spin" />
          <span className="text-gray-400">Loading portfolio...</span>
        </div>
      </div>
    )
  }

  if (!portfolio) {
    return (
      <div className="pt-24 pb-12 px-4">
        <div className="max-w-7xl mx-auto text-center">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
          >
            <Wallet className="w-16 h-16 mx-auto mb-4 text-gray-600" />
            <h1 className="text-3xl font-bold font-display mb-4">No Portfolio Found</h1>
            <p className="text-gray-400 mb-8">Create your first portfolio to start investing</p>
            <Link to="/onboarding" className="btn-primary inline-flex items-center gap-2">
              <Plus className="w-5 h-5" />
              Create Portfolio
            </Link>
          </motion.div>
        </div>
      </div>
    )
  }

  return (
    <div className="pt-24 pb-12 px-4">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8"
        >
          <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
            <div>
              <h1 className="text-3xl font-bold font-display mb-2">{portfolio.name}</h1>
              <div className="flex items-center gap-3 text-sm">
                <span className="flex items-center gap-1 text-primary">
                  <Brain className="w-4 h-4" />
                  {portfolio.model_type === 'temporal_fusion_transformer' ? 'Temporal Fusion Transformer' : portfolio.model_type}
                </span>
                <span className="text-gray-500">|</span>
                <span className="text-gray-400">{holdings.length} Holdings</span>
              </div>
            </div>
            <Link to="/deposit-withdraw" className="btn-primary">
              <Plus className="w-5 h-5 inline-block mr-2" />
              Add Funds
            </Link>
          </div>
        </motion.div>

        {/* Portfolio Stats */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="glass-card p-6"
          >
            <div className="text-gray-400 text-sm mb-1">Total Value</div>
            <div className="text-3xl font-bold font-display">
              ${totalValue.toLocaleString()}
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="glass-card p-6"
          >
            <div className="text-gray-400 text-sm mb-1">Total Return</div>
            <div className={`text-3xl font-bold font-display ${totalReturn >= 0 ? 'text-success' : 'text-danger'}`}>
              {totalReturn >= 0 ? '+' : ''}${totalReturn.toLocaleString()}
            </div>
            <div className={`text-sm ${totalReturn >= 0 ? 'text-success' : 'text-danger'}`}>
              {totalReturn >= 0 ? '+' : ''}{totalReturnPct.toFixed(2)}%
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
            className="glass-card p-6"
          >
            <div className="text-gray-400 text-sm mb-1">Day Change</div>
            <div className={`text-3xl font-bold font-display ${dayChange >= 0 ? 'text-success' : 'text-danger'}`}>
              {dayChange >= 0 ? '+' : ''}${dayChange.toLocaleString()}
            </div>
            <div className={`text-sm ${dayChange >= 0 ? 'text-success' : 'text-danger'}`}>
              {dayChange >= 0 ? '+' : ''}{dayChangePct.toFixed(2)}%
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 }}
            className="glass-card p-6"
          >
            <div className="text-gray-400 text-sm mb-1">Holdings</div>
            <div className="text-3xl font-bold font-display">{holdings.length}</div>
            <div className="text-gray-400 text-sm">Assets</div>
          </motion.div>
        </div>

        {/* Tabs */}
        <div className="flex gap-2 mb-6">
          {['overview', 'holdings', 'ai-insights', 'performance'].map((tab) => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`px-4 py-2 rounded-lg capitalize transition-colors ${
                activeTab === tab
                  ? 'bg-primary text-dark font-medium'
                  : 'text-gray-400 hover:text-white hover:bg-dark-lighter'
              }`}
            >
              {tab.replace('-', ' ')}
            </button>
          ))}
        </div>

        {/* Tab Content */}
        {activeTab === 'overview' && (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="lg:col-span-2 glass-card p-6"
            >
              <h2 className="text-xl font-semibold mb-6">Performance</h2>
              <PortfolioChart portfolio={portfolio} />
            </motion.div>

            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1 }}
              className="glass-card p-6"
            >
              <h2 className="text-xl font-semibold mb-6">Allocation</h2>
              <AssetAllocation holdings={holdings} />
            </motion.div>
          </div>
        )}

        {activeTab === 'holdings' && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
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
                    const returnPct = holding.avg_price > 0 
                      ? ((holding.current_price - holding.avg_price) / holding.avg_price) * 100 
                      : 0
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
                        <td className="p-4 text-right">{holding.quantity.toFixed(2)}</td>
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
                <Link to="/onboarding" className="btn-primary inline-block">
                  Generate AI Portfolio
                </Link>
              </div>
            )}
          </motion.div>
        )}

        {activeTab === 'ai-insights' && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
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
                  <button className="btn-secondary text-sm">
                    Details
                    <ArrowRight className="w-4 h-4 inline-block ml-1" />
                  </button>
                </div>
              ))
            ) : (
              <div className="text-center py-12">
                <Brain className="w-12 h-12 mx-auto mb-4 text-gray-600" />
                <p className="text-gray-400">No AI insights available yet</p>
              </div>
            )}
          </motion.div>
        )}

        {activeTab === 'performance' && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="grid grid-cols-1 md:grid-cols-2 gap-6"
          >
            <div className="glass-card p-6">
              <h3 className="text-lg font-semibold mb-4">Risk Metrics</h3>
              <div className="space-y-4">
                {[
                  { 
                    label: 'Volatility', 
                    value: portfolio.volatility ? `${(portfolio.volatility * 100).toFixed(1)}%` : 'Calculating...', 
                    color: portfolio.volatility && portfolio.volatility > 0.2 ? 'warning' : 'primary' 
                  },
                  { 
                    label: 'Sharpe Ratio', 
                    value: portfolio.sharpe_ratio ? portfolio.sharpe_ratio.toFixed(2) : 'Calculating...', 
                    color: portfolio.sharpe_ratio && portfolio.sharpe_ratio > 1 ? 'success' : 'primary' 
                  },
                  { 
                    label: 'Max Drawdown', 
                    value: portfolio.max_drawdown ? `${(portfolio.max_drawdown * 100).toFixed(1)}%` : 'Calculating...', 
                    color: 'warning' 
                  },
                  { 
                    label: 'VaR (95%)', 
                    value: portfolio.var_95 ? `${(portfolio.var_95 * 100).toFixed(1)}%` : 'Calculating...', 
                    color: 'danger' 
                  },
                ].map((metric, index) => (
                  <div key={index} className="flex items-center justify-between">
                    <span className="text-gray-400">{metric.label}</span>
                    <span className={`font-bold text-${metric.color}`}>{metric.value}</span>
                  </div>
                ))}
              </div>
            </div>

            <div className="glass-card p-6">
              <h3 className="text-lg font-semibold mb-4">AI Portfolio Explanation</h3>
              <div className="space-y-4">
                <p className="text-gray-400 text-sm leading-relaxed">
                  {portfolio.ai_explanation || 'AI analysis in progress...'}
                </p>
                {portfolio.expected_return && (
                  <div className="p-4 bg-dark-lighter rounded-lg">
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-gray-400">Expected Annual Return</span>
                      <span className="text-success font-bold">
                        +{(portfolio.expected_return * 100).toFixed(1)}%
                      </span>
                    </div>
                    <div className="w-full bg-gray-800 rounded-full h-2">
                      <div 
                        className="bg-success h-2 rounded-full" 
                        style={{ width: `${Math.min(100, Math.max(0, portfolio.expected_return * 100 * 2))}%` }}
                      />
                    </div>
                  </div>
                )}
              </div>
            </div>
          </motion.div>
        )}
      </div>
    </div>
  )
}
