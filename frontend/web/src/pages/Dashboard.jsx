import { useEffect, useState } from 'react'
import { useGeminiStream } from "../hooks/useGeminiStream";
import MarketDataPanel from "../components/MarketDataPanel";
import InsightsPanel from "../components/InsightsPanel";
import { useNavigate, Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import { 
  TrendingUp, 
  TrendingDown,
  PieChart, 
  Activity, 
  DollarSign,
  ArrowUpRight,
  ArrowDownRight,
  Brain,
  Zap,
  Loader2,
  Globe,
  Wallet,
  AlertCircle,
  Sparkles,
  RefreshCw,
  BarChart3,
  Target,
  Layers
} from 'lucide-react'
import { useAuthStore } from '../store/authStore'
import { marketApi, dashboardApi, portfolioApi, portfolioExtApi } from '../services/api'
import PortfolioChart from '../components/PortfolioChart'
import AssetAllocation from '../components/AssetAllocation'

export default function Dashboard() {
  const { isAuthenticated, user } = useAuthStore()
  const navigate = useNavigate()
  
  // Market data state
  const [marketData, setMarketData] = useState({
    GSPC: { price: 0, change: 0 },
    IXIC: { price: 0, change: 0 },
    DJI: { price: 0, change: 0 }
  })
  
  // Loading states
  const [isLoading, setIsLoading] = useState(true)
  const [isRefreshing, setIsRefreshing] = useState(false)
  
  // Portfolio data
  const [portfolios, setPortfolios] = useState([])
  const [selectedPortfolio, setSelectedPortfolio] = useState(null)  // full portfolio with holdings
  const [chartData, setChartData] = useState([])
  const [totalValue, setTotalValue] = useState(0)
  const [totalInvested, setTotalInvested] = useState(0)
  const [totalReturn, setTotalReturn] = useState(0)
  const [totalReturnPct, setTotalReturnPct] = useState(0)
  
  // Wallet data
  const [walletBalance, setWalletBalance] = useState({
    balance: 0,
    total_deposited: 0,
    total_withdrawn: 0,
    total_invested: 0
  })
  
  // AI insights
  const [aiInsights, setAiInsights] = useState([])

  useEffect(() => {
    if (!isAuthenticated) {
      navigate('/login')
    }
  }, [isAuthenticated, navigate])

  useEffect(() => {
    if (isAuthenticated) {
      fetchAllData()
      // Refresh every 5 minutes — each refresh calls Finnhub for live prices
      const interval = setInterval(fetchAllData, 5 * 60 * 1000)
      return () => clearInterval(interval)
    }
  }, [isAuthenticated])

  const fetchAllData = async () => {
    try {
      if (!isRefreshing) setIsLoading(true)
      
      await Promise.all([
        fetchMarketData(),
        fetchDashboardData()
      ])
    } catch (error) {
      console.error('Error fetching data:', error)
    } finally {
      setIsLoading(false)
      setIsRefreshing(false)
    }
  }

  const handleRefresh = () => {
    setIsRefreshing(true)
    fetchAllData()
  }

  const fetchMarketData = async () => {
    try {
      const overviewRes = await marketApi.getMarketOverview()
      if (overviewRes.data?.indices) {
        const indices = overviewRes.data.indices
        setMarketData({
          GSPC: { 
            price: indices.GSPC?.price || 0, 
            change: indices.GSPC?.change_percent || 0 
          },
          IXIC: { 
            price: indices.IXIC?.price || 0, 
            change: indices.IXIC?.change_percent || 0 
          },
          DJI: { 
            price: indices.DJI?.price || 0, 
            change: indices.DJI?.change_percent || 0 
          }
        })
      }
    } catch (error) {
      console.error('Error fetching market data:', error)
    }
  }

  const fetchDashboardData = async () => {
    try {
      const dashboardRes = await dashboardApi.getDashboard()
      const data = dashboardRes.data

      // Set portfolios (summaries)
      const userPortfolios = data.portfolios || []
      setPortfolios(userPortfolios)

      // Fetch FULL portfolio data (with holdings) for the selected/first portfolio.
      // Also silently refresh live prices from Finnhub so returning users
      // always see current market values, not stale creation-time prices.
      if (userPortfolios.length > 0) {
        const targetId = selectedPortfolio?.id || userPortfolios[0].id
        try {
          // Fire price refresh concurrently — it updates holdings & total_value in DB
          const [fullRes, chartRes] = await Promise.all([
            portfolioExtApi.refreshPrices(targetId)
              .then(() => portfolioApi.getById(targetId))  // re-fetch after refresh
              .catch(() => portfolioApi.getById(targetId)), // fallback: fetch without refresh
            portfolioExtApi.getChart(targetId).catch(() => null),
          ])
          if (fullRes?.data) setSelectedPortfolio(fullRes.data)
          if (chartRes?.data?.chart_data) setChartData(chartRes.data.chart_data)
        } catch (e) {
          setSelectedPortfolio(userPortfolios[0])
        }
      }
      
      // Set wallet
      setWalletBalance(data.wallet || {
        balance: 0,
        total_deposited: 0,
        total_withdrawn: 0,
        total_invested: 0
      })
      
      // Calculate totals
      const portfolioValue = data.total_portfolio_value || 0
      const invested = data.total_invested || 0
      
      setTotalValue(portfolioValue)
      setTotalInvested(invested)
      
      // Calculate return
      const returns = portfolioValue - invested
      setTotalReturn(returns)
      setTotalReturnPct(invested > 0 ? (returns / invested) * 100 : 0)
      
      // Generate insights
      generateAiInsights(userPortfolios)
      
    } catch (error) {
      console.error('Error fetching dashboard data:', error)
    }
  }

  const generateAiInsights = (portfoliosData) => {
    const insights = []
    
    // Welcome insight for new users
    if (!portfoliosData || portfoliosData.length === 0) {
      insights.push({
        title: 'Welcome to AutoInvest!',
        description: 'Start by depositing funds and creating your first AI-optimized portfolio.',
        type: 'info',
        confidence: 100
      })
      setAiInsights(insights)
      return
    }
    
    // Portfolio-specific insights
    portfoliosData.forEach(portfolio => {
      // Check for rebalancing
      if (portfolio.holdings?.length > 0) {
        const totalWeight = portfolio.holdings.reduce((sum, h) => sum + (h.weight || 0), 0)
        const drift = Math.abs(totalWeight - 1.0)
        
        if (drift > 0.05) {
          insights.push({
            title: 'Rebalancing Needed',
            description: `${portfolio.name} has drifted ${(drift * 100).toFixed(1)}% from target allocation.`,
            type: 'action',
            confidence: Math.min(95, 70 + drift * 100)
          })
        }
        
        // Check holdings for signals
        portfolio.holdings.forEach(holding => {
          if (holding.signal_strength === 'strong_buy' && holding.confidence_score > 0.8) {
            insights.push({
              title: `Strong Signal: ${holding.symbol}`,
              description: `High confidence buy signal with ${(holding.predicted_return * 100).toFixed(1)}% predicted return.`,
              type: 'opportunity',
              confidence: holding.confidence_score * 100
            })
          }
        })
      }
      
      // Risk warning
      if (portfolio.volatility && portfolio.volatility > 0.25) {
        insights.push({
          title: 'High Volatility Alert',
          description: `${portfolio.name} has elevated volatility (${(portfolio.volatility * 100).toFixed(1)}%). Consider defensive positioning.`,
          type: 'warning',
          confidence: 80
        })
      }
    })
    
    // Market context
    const marketChange = marketData.GSPC?.change || 0
    if (marketChange < -2) {
      insights.push({
        title: 'Market Dip Opportunity',
        description: 'Market is down significantly. This could be a good entry point for new investments.',
        type: 'opportunity',
        confidence: 65
      })
    }
    
    setAiInsights(insights.slice(0, 4))
  }

  // Stats for display
  const stats = [
    {
      title: 'Total Portfolio Value',
      value: totalValue,
      format: 'currency',
      subValue: totalReturnPct,
      subLabel: 'all time',
      positive: totalReturn >= 0,
      icon: DollarSign,
      color: 'primary'
    },
    {
      title: 'Total Invested',
      value: totalInvested,
      format: 'currency',
      subValue: null,
      positive: true,
      icon: Layers,
      color: 'secondary'
    },
    {
      title: 'Total Return',
      value: totalReturn,
      format: 'currency',
      subValue: totalReturnPct,
      subLabel: 'return',
      positive: totalReturn >= 0,
      icon: totalReturn >= 0 ? TrendingUp : TrendingDown,
      color: totalReturn >= 0 ? 'success' : 'danger'
    },
    {
      title: 'Available Cash',
      value: walletBalance.balance,
      format: 'currency',
      subValue: null,
      positive: true,
      icon: Wallet,
      color: 'accent'
    }
  ]

  if (!isAuthenticated) {
    return null
  }

  return (
    <div className="pt-24 pb-12 px-4">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-6 flex items-center justify-between"
        >
          <div>
            <h1 className="text-3xl font-bold font-display mb-1">
              Dashboard
            </h1>
            <p className="text-gray-400 text-sm">
              Welcome back, <span className="text-gradient">{user?.full_name?.split(' ')[0] || 'Investor'}</span>
            </p>
          </div>
          <button
            onClick={handleRefresh}
            disabled={isRefreshing}
            className="flex items-center gap-2 px-4 py-2 bg-dark-lighter rounded-lg hover:bg-gray-800 transition-colors"
          >
            <RefreshCw className={`w-4 h-4 ${isRefreshing ? 'animate-spin' : ''}`} />
            Refresh
          </button>
        </motion.div>

        {/* Market Overview */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="mb-6"
        >
          <div className="glass-card p-4">
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center gap-2">
                <Globe className="w-4 h-4 text-primary" />
                <span className="text-sm font-medium">Market Overview</span>
                <span className="flex w-2 h-2 bg-success rounded-full animate-pulse"></span>
              </div>
              <span className="text-xs text-gray-500">Live</span>
            </div>
            
            {isLoading ? (
              <div className="flex items-center justify-center py-4">
                <Loader2 className="w-5 h-5 text-primary animate-spin" />
              </div>
            ) : (
              <div className="grid grid-cols-3 gap-4">
                <div className="p-3 bg-dark-lighter rounded-lg">
                  <div className="text-xs text-gray-500 mb-1">S&P 500</div>
                  <div className="font-semibold">{marketData.GSPC.price?.toLocaleString() || '---'}</div>
                  <div className={`text-xs flex items-center gap-1 ${marketData.GSPC.change >= 0 ? 'text-success' : 'text-danger'}`}>
                    {marketData.GSPC.change >= 0 ? <ArrowUpRight className="w-3 h-3" /> : <ArrowDownRight className="w-3 h-3" />}
                    {marketData.GSPC.change >= 0 ? '+' : ''}{marketData.GSPC.change?.toFixed(2) || '0.00'}%
                  </div>
                </div>
                <div className="p-3 bg-dark-lighter rounded-lg">
                  <div className="text-xs text-gray-500 mb-1">NASDAQ</div>
                  <div className="font-semibold">{marketData.IXIC.price?.toLocaleString() || '---'}</div>
                  <div className={`text-xs flex items-center gap-1 ${marketData.IXIC.change >= 0 ? 'text-success' : 'text-danger'}`}>
                    {marketData.IXIC.change >= 0 ? <ArrowUpRight className="w-3 h-3" /> : <ArrowDownRight className="w-3 h-3" />}
                    {marketData.IXIC.change >= 0 ? '+' : ''}{marketData.IXIC.change?.toFixed(2) || '0.00'}%
                  </div>
                </div>
                <div className="p-3 bg-dark-lighter rounded-lg">
                  <div className="text-xs text-gray-500 mb-1">Dow Jones</div>
                  <div className="font-semibold">{marketData.DJI.price?.toLocaleString() || '---'}</div>
                  <div className={`text-xs flex items-center gap-1 ${marketData.DJI.change >= 0 ? 'text-success' : 'text-danger'}`}>
                    {marketData.DJI.change >= 0 ? <ArrowUpRight className="w-3 h-3" /> : <ArrowDownRight className="w-3 h-3" />}
                    {marketData.DJI.change >= 0 ? '+' : ''}{marketData.DJI.change?.toFixed(2) || '0.00'}%
                  </div>
                </div>
              </div>
            )}
          </div>
        </motion.div>

        {/* Stats Grid */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
          {stats.map((stat, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1 + index * 0.05 }}
              className="glass-card p-4"
            >
              <div className="flex items-center justify-between mb-2">
                <div className={`w-8 h-8 rounded-lg bg-${stat.color}/10 flex items-center justify-center`}>
                  <stat.icon className={`w-4 h-4 text-${stat.color}`} />
                </div>
              </div>
              <div className="text-xs text-gray-500 mb-1">{stat.title}</div>
              <div className="text-xl font-bold font-display">
                {stat.format === 'currency' ? '$' : ''}{stat.value?.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 }) || '0.00'}
              </div>
              {stat.subValue !== null && (
                <div className={`text-xs flex items-center gap-1 ${stat.positive ? 'text-success' : 'text-danger'}`}>
                  {stat.positive ? <ArrowUpRight className="w-3 h-3" /> : <ArrowDownRight className="w-3 h-3" />}
                  {stat.positive ? '+' : ''}{stat.subValue?.toFixed(2) || '0.00'}%
                </div>
              )}
            </motion.div>
          ))}
        </div>

        {/* No Portfolios State */}
        {portfolios.length === 0 && !isLoading ? (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="glass-card p-12 text-center"
          >
            <div className="w-20 h-20 rounded-full bg-primary/10 flex items-center justify-center mx-auto mb-4">
              <Sparkles className="w-10 h-10 text-primary" />
            </div>
            <h2 className="text-2xl font-bold font-display mb-2">Start Your Investment Journey</h2>
            <p className="text-gray-400 mb-6 max-w-md mx-auto">
              Deposit funds and let our AI create an optimized portfolio based on your risk tolerance and investment goals.
            </p>
            <div className="flex items-center justify-center gap-4">
              <Link
                to="/deposit-withdraw"
                className="btn-secondary flex items-center gap-2"
              >
                <Wallet className="w-4 h-4" />
                Deposit Funds
              </Link>
              {walletBalance.balance > 0 && (
                <Link
                  to="/invest"
                  className="btn-primary flex items-center gap-2"
                >
                  <Brain className="w-4 h-4" />
                  Create Portfolio
                </Link>
              )}
            </div>
            {walletBalance.balance === 0 && (
              <p className="text-sm text-gray-500 mt-4">
                You need to add funds before creating a portfolio
              </p>
            )}
          </motion.div>
        ) : (
          <>
            {/* Portfolio Selector (if multiple portfolios) */}
            {portfolios.length > 1 && (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="mb-4"
              >
                <div className="glass-card p-4">
                  <div className="flex items-center gap-2 mb-3">
                    <PieChart className="w-4 h-4 text-primary" />
                    <span className="text-sm font-medium">Your Portfolios</span>
                  </div>
                  <div className="flex flex-wrap gap-2">
                    {portfolios.map(portfolio => (
                      <button
                        key={portfolio.id}
                        onClick={async () => {
                          try {
                            const [fullRes, chartRes] = await Promise.all([
                              portfolioApi.getById(portfolio.id),
                              portfolioExtApi.getChart(portfolio.id).catch(() => null),
                            ])
                            if (fullRes?.data) setSelectedPortfolio(fullRes.data)
                            if (chartRes?.data?.chart_data) setChartData(chartRes.data.chart_data)
                          } catch {
                            setSelectedPortfolio(portfolio)
                          }
                        }}
                        className={`px-4 py-2 rounded-lg text-sm transition-colors ${
                          selectedPortfolio?.id === portfolio.id
                            ? 'bg-primary text-dark'
                            : 'bg-dark-lighter hover:bg-gray-800'
                        }`}
                      >
                        {portfolio.name}
                      </button>
                    ))}
                  </div>
                </div>
              </motion.div>
            )}

            {/* Main Content */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              {/* Portfolio Performance */}
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.3 }}
                className="lg:col-span-2 glass-card p-6"
              >
                <div className="flex items-center justify-between mb-4">
                  <div>
                    <h2 className="text-xl font-semibold">
                      {selectedPortfolio?.name || 'Portfolio Performance'}
                    </h2>
                    {selectedPortfolio && (
                      <p className="text-sm text-gray-400">
                        {selectedPortfolio.holdings_count || 0} holdings • {selectedPortfolio.risk_profile || 'moderate'} risk
                      </p>
                    )}
                  </div>
                  <div className="flex items-center gap-2">
                    <Brain className="w-4 h-4 text-primary" />
                    <span className="text-xs text-primary">AI Optimized</span>
                  </div>
                </div>

                {selectedPortfolio && selectedPortfolio.holdings?.length > 0 ? (
                  <>
                    <PortfolioChart
                      chartData={chartData}
                      invested={selectedPortfolio?.invested_amount || 0}
                    />
                    
                    {/* Holdings Table */}
                    <div className="mt-6">
                      <h3 className="text-sm font-medium mb-3">Holdings</h3>
                      <div className="overflow-x-auto">
                        <table className="w-full">
                          <thead>
                            <tr className="text-left text-xs text-gray-500 border-b border-gray-800">
                              <th className="pb-2">Symbol</th>
                              <th className="pb-2">Shares</th>
                              <th className="pb-2">Price</th>
                              <th className="pb-2">Value</th>
                              <th className="pb-2">Weight</th>
                              <th className="pb-2">AI Signal</th>
                            </tr>
                          </thead>
                          <tbody>
                            {selectedPortfolio.holdings.slice(0, 5).map((holding, idx) => (
                              <tr key={idx} className="border-b border-gray-800/50 text-sm">
                                <td className="py-3 font-medium">{holding.symbol}</td>
                                <td className="py-3 text-gray-400">{holding.quantity?.toFixed(2) || '0'}</td>
                                <td className="py-3">${holding.current_price?.toFixed(2) || '0.00'}</td>
                                <td className="py-3">${holding.market_value?.toFixed(2) || '0.00'}</td>
                                <td className="py-3">{((holding.weight || 0) * 100).toFixed(1)}%</td>
                                <td className="py-3">
                                  <span className={`text-xs px-2 py-1 rounded-full ${
                                    holding.signal_strength === 'buy' || holding.signal_strength === 'strong_buy'
                                      ? 'bg-success/20 text-success'
                                      : holding.signal_strength === 'sell' || holding.signal_strength === 'strong_sell'
                                      ? 'bg-danger/20 text-danger'
                                      : 'bg-gray-700 text-gray-400'
                                  }`}>
                                    {holding.signal_strength?.replace('_', ' ') || 'hold'}
                                  </span>
                                </td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                      {selectedPortfolio.holdings.length > 5 && (
                        <Link to={`/portfolio/${selectedPortfolio.id}`} className="text-sm text-primary hover:underline mt-2 inline-block">
                          View all {selectedPortfolio.holdings.length} holdings →
                        </Link>
                      )}
                    </div>
                  </>
                ) : (
                  <div className="text-center py-8">
                    <PieChart className="w-12 h-12 mx-auto mb-3 text-gray-600" />
                    <p className="text-gray-400">No holdings in this portfolio</p>
                    <Link to="/invest" className="btn-primary inline-block mt-4">
                      Add Investments
                    </Link>
                  </div>
                )}
              </motion.div>

              {/* Right Column */}
              <div className="space-y-6">
                {/* Asset Allocation */}
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.4 }}
                  className="glass-card p-6"
                >
                  <h2 className="text-lg font-semibold mb-4">Asset Allocation</h2>
                  {selectedPortfolio?.holdings?.length > 0 ? (
                    <AssetAllocation holdings={selectedPortfolio.holdings} />
                  ) : (
                    <div className="text-center py-4 text-gray-500">
                      <PieChart className="w-8 h-8 mx-auto mb-2 opacity-50" />
                      <p className="text-sm">No holdings yet</p>
                    </div>
                  )}
                </motion.div>

                {/* AI Insights */}
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.5 }}
                  className="glass-card p-6"
                >
                  <div className="flex items-center gap-2 mb-4">
                    <Brain className="w-5 h-5 text-primary" />
                    <h2 className="text-lg font-semibold">AI Insights</h2>
                  </div>
                  <div className="space-y-3">
                    {aiInsights.map((insight, idx) => (
                      <div
                        key={idx}
                        className="p-3 bg-dark-lighter rounded-lg"
                      >
                        <div className="flex items-start justify-between mb-1">
                          <h3 className="text-sm font-medium">{insight.title}</h3>
                          <span className={`text-xs px-2 py-0.5 rounded-full ${
                            insight.type === 'opportunity' ? 'bg-success/20 text-success' :
                            insight.type === 'action' ? 'bg-primary/20 text-primary' :
                            insight.type === 'warning' ? 'bg-warning/20 text-warning' :
                            'bg-gray-700 text-gray-400'
                          }`}>
                            {insight.confidence?.toFixed(0)}%
                          </span>
                        </div>
                        <p className="text-xs text-gray-400">{insight.description}</p>
                      </div>
                    ))}
                  </div>
                </motion.div>

                {/* Quick Actions */}
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.6 }}
                  className="glass-card p-6"
                >
                  <h2 className="text-lg font-semibold mb-4">Quick Actions</h2>
                  <div className="space-y-2">
                    <Link
                      to="/deposit-withdraw"
                      className="flex items-center gap-3 p-3 bg-dark-lighter rounded-lg hover:bg-gray-800 transition-colors"
                    >
                      <Wallet className="w-5 h-5 text-success" />
                      <div>
                        <div className="text-sm font-medium">Add Funds</div>
                        <div className="text-xs text-gray-500">Deposit simulated money</div>
                      </div>
                    </Link>
                    <Link
                      to="/invest"
                      className="flex items-center gap-3 p-3 bg-dark-lighter rounded-lg hover:bg-gray-800 transition-colors"
                    >
                      <Brain className="w-5 h-5 text-primary" />
                      <div>
                        <div className="text-sm font-medium">New Portfolio</div>
                        <div className="text-xs text-gray-500">Create AI-optimized portfolio</div>
                      </div>
                    </Link>
                    <Link
                      to="/analysis"
                      className="flex items-center gap-3 p-3 bg-dark-lighter rounded-lg hover:bg-gray-800 transition-colors"
                    >
                      <BarChart3 className="w-5 h-5 text-secondary" />
                      <div>
                        <div className="text-sm font-medium">AI Analysis</div>
                        <div className="text-xs text-gray-500">Analyze stocks with AI</div>
                      </div>
                    </Link>
                  </div>
                </motion.div>
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  )
}
