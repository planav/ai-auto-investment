import { useEffect, useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import { 
  TrendingUp, 
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
  Sparkles
} from 'lucide-react'
import { useAuthStore } from '../store/authStore'
import { marketApi, portfolioApi, userApi } from '../services/api'
import PortfolioChart from '../components/PortfolioChart'
import AssetAllocation from '../components/AssetAllocation'
import RecentActivity from '../components/RecentActivity'
import toast from 'react-hot-toast'

export default function Dashboard() {
  const { isAuthenticated, user } = useAuthStore()
  const navigate = useNavigate()
  
  const [marketData, setMarketData] = useState({
    spy: { price: 0, change: 0 },
    qqq: { price: 0, change: 0 },
    dia: { price: 0, change: 0 }
  })
  const [topMovers, setTopMovers] = useState([])
  const [isLoading, setIsLoading] = useState(true)
  
  // Real portfolio data from API
  const [portfolios, setPortfolios] = useState([])
  const [totalValue, setTotalValue] = useState(0)
  const [totalReturn, setTotalReturn] = useState(0)
  const [userPreferences, setUserPreferences] = useState(null)
  const [aiInsights, setAiInsights] = useState([])

  useEffect(() => {
    if (!isAuthenticated) {
      navigate('/login')
    }
  }, [isAuthenticated, navigate])

  // Fetch real data
  useEffect(() => {
    if (isAuthenticated) {
      fetchAllData()
      // Refresh every 60 seconds
      const interval = setInterval(fetchAllData, 60000)
      return () => clearInterval(interval)
    }
  }, [isAuthenticated])

  const fetchAllData = async () => {
    await Promise.all([
      fetchMarketData(),
      fetchPortfolioData(),
      fetchUserPreferences(),
    ])
  }

  const fetchMarketData = async () => {
    try {
      // Fetch market overview
      const overviewRes = await marketApi.getMarketOverview()
      if (overviewRes.data?.indices) {
        const indices = overviewRes.data.indices
        setMarketData({
          spy: { 
            price: indices.SPY?.price || 0, 
            change: indices.SPY?.change_percent || 0 
          },
          qqq: { 
            price: indices.QQQ?.price || 0, 
            change: indices.QQQ?.change_percent || 0 
          },
          dia: { 
            price: indices.DIA?.price || 0, 
            change: indices.DIA?.change_percent || 0 
          }
        })
      }
      
      // Fetch popular stocks for top movers
      const popularRes = await marketApi.getPopularStocks()
      if (popularRes.data) {
        const sorted = [...popularRes.data]
          .sort((a, b) => Math.abs(b.change_percent) - Math.abs(a.change_percent))
          .slice(0, 5)
        setTopMovers(sorted)
      }
    } catch (error) {
      console.error('Error fetching market data:', error)
    }
  }

  const fetchPortfolioData = async () => {
    try {
      setIsLoading(true)
      const response = await portfolioApi.getAll()
      if (response.data) {
        setPortfolios(response.data)
        
        // Calculate total value and return
        let value = 0
        let returnValue = 0
        
        response.data.forEach(portfolio => {
          value += portfolio.total_value || 0
          // Calculate return based on holdings
          portfolio.holdings?.forEach(holding => {
            const cost = holding.avg_price * holding.quantity
            const current = holding.current_price * holding.quantity
            returnValue += (current - cost)
          })
        })
        
        setTotalValue(value)
        setTotalReturn(returnValue)
        
        // Generate AI insights based on real portfolio data
        generateAiInsights(response.data)
      }
    } catch (error) {
      console.error('Error fetching portfolio data:', error)
      toast.error('Failed to load portfolio data')
    } finally {
      setIsLoading(false)
    }
  }

  const fetchUserPreferences = async () => {
    try {
      const response = await userApi.getPreferences()
      if (response.data) {
        setUserPreferences(response.data)
      }
    } catch (error) {
      console.error('Error fetching user preferences:', error)
    }
  }

  const generateAiInsights = (portfolios) => {
    if (!portfolios || portfolios.length === 0) {
      setAiInsights([{
        title: 'Welcome to AutoInvest',
        description: 'Create your first portfolio to get personalized AI insights.',
        confidence: 100,
        type: 'info',
      }])
      return
    }

    const insights = []
    
    // Check for rebalancing needs
    portfolios.forEach(portfolio => {
      if (portfolio.holdings && portfolio.holdings.length > 0) {
        const totalWeight = portfolio.holdings.reduce((sum, h) => sum + h.weight, 0)
        const drift = Math.abs(totalWeight - 1.0)
        
        if (drift > 0.05) {
          insights.push({
            title: `Rebalancing Recommended: ${portfolio.name}`,
            description: `Portfolio drift detected at ${(drift * 100).toFixed(1)}%. Rebalancing could improve risk-adjusted returns.`,
            confidence: Math.min(95, 70 + drift * 100),
            type: 'action',
          })
        }
        
        // Check for high confidence signals
        portfolio.holdings.forEach(holding => {
          if (holding.confidence_score > 0.8 && holding.predicted_return > 0.1) {
            insights.push({
              title: `Strong Buy Signal: ${holding.symbol}`,
              description: `AI predicts ${(holding.predicted_return * 100).toFixed(1)}% return with ${(holding.confidence_score * 100).toFixed(0)}% confidence.`,
              confidence: holding.confidence_score * 100,
              type: 'opportunity',
            })
          }
        })
      }
    })
    
    // Add market regime insight based on portfolio metrics
    const avgVolatility = portfolios.reduce((sum, p) => sum + (p.volatility || 0), 0) / portfolios.length
    if (avgVolatility > 0.2) {
      insights.push({
        title: 'Elevated Volatility Detected',
        description: 'Your portfolios are experiencing higher than normal volatility. Consider defensive positioning.',
        confidence: 75,
        type: 'warning',
      })
    }
    
    // Limit to top 3 insights
    setAiInsights(insights.slice(0, 3))
  }

  // Calculate portfolio stats from real data
  const portfolioStats = [
    {
      title: 'Total Portfolio Value',
      value: totalValue > 0 ? `$${totalValue.toLocaleString()}` : '$0',
      change: totalValue > 0 && userPreferences?.initial_investment 
        ? `${((totalValue - userPreferences.initial_investment) / userPreferences.initial_investment * 100).toFixed(1)}%`
        : '0%',
      isPositive: totalValue >= (userPreferences?.initial_investment || 0),
      icon: DollarSign,
      color: 'primary',
    },
    {
      title: 'Total Return',
      value: totalReturn >= 0 ? `$${totalReturn.toLocaleString()}` : `-$${Math.abs(totalReturn).toLocaleString()}`,
      change: totalValue > 0 ? `${(totalReturn / totalValue * 100).toFixed(1)}%` : '0%',
      isPositive: totalReturn >= 0,
      icon: TrendingUp,
      color: totalReturn >= 0 ? 'success' : 'danger',
    },
    {
      title: 'Active Portfolios',
      value: portfolios.length.toString(),
      change: portfolios.length > 0 ? 'Active' : 'None',
      isPositive: portfolios.length > 0,
      icon: PieChart,
      color: 'secondary',
    },
    {
      title: 'Available Balance',
      value: userPreferences?.initial_investment 
        ? `$${userPreferences.initial_investment.toLocaleString()}` 
        : '$0',
      change: 'Cash',
      isPositive: true,
      icon: Wallet,
      color: 'accent',
    },
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
          className="mb-8"
        >
          <h1 className="text-3xl font-bold font-display mb-2">
            Welcome back, <span className="text-gradient">{user?.full_name?.split(' ')[0] || 'Investor'}</span>
          </h1>
          <p className="text-gray-400">
            Here's an overview of your investment portfolio
          </p>
        </motion.div>

        {/* Live Market Ticker */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="mb-8"
        >
          <div className="glass-card p-4">
            <div className="flex items-center gap-2 mb-3">
              <Globe className="w-4 h-4 text-primary" />
              <span className="text-sm text-gray-400">Live Market</span>
              <span className="flex w-2 h-2 bg-success rounded-full animate-pulse"></span>
            </div>
            {isLoading ? (
              <div className="flex items-center gap-4">
                <Loader2 className="w-4 h-4 text-primary animate-spin" />
                <span className="text-sm text-gray-400">Loading market data...</span>
              </div>
            ) : (
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="flex items-center justify-between p-3 rounded-lg bg-dark-lighter">
                  <span className="text-sm text-gray-400">S&P 500</span>
                  <div className="text-right">
                    <div className="font-semibold">${marketData.spy.price?.toFixed(2) || '---'}</div>
                    <div className={`text-xs ${marketData.spy.change >= 0 ? 'text-success' : 'text-danger'}`}>
                      {marketData.spy.change >= 0 ? '+' : ''}{marketData.spy.change?.toFixed(2) || '0.00'}%
                    </div>
                  </div>
                </div>
                <div className="flex items-center justify-between p-3 rounded-lg bg-dark-lighter">
                  <span className="text-sm text-gray-400">NASDAQ</span>
                  <div className="text-right">
                    <div className="font-semibold">${marketData.qqq.price?.toFixed(2) || '---'}</div>
                    <div className={`text-xs ${marketData.qqq.change >= 0 ? 'text-success' : 'text-danger'}`}>
                      {marketData.qqq.change >= 0 ? '+' : ''}{marketData.qqq.change?.toFixed(2) || '0.00'}%
                    </div>
                  </div>
                </div>
                <div className="flex items-center justify-between p-3 rounded-lg bg-dark-lighter">
                  <span className="text-sm text-gray-400">Dow Jones</span>
                  <div className="text-right">
                    <div className="font-semibold">${marketData.dia.price?.toFixed(2) || '---'}</div>
                    <div className={`text-xs ${marketData.dia.change >= 0 ? 'text-success' : 'text-danger'}`}>
                      {marketData.dia.change >= 0 ? '+' : ''}{marketData.dia.change?.toFixed(2) || '0.00'}%
                    </div>
                  </div>
                </div>
                <div className="flex items-center justify-between p-3 rounded-lg bg-dark-lighter">
                  <span className="text-sm text-gray-400">Top Mover</span>
                  <div className="text-right">
                    {topMovers[0] ? (
                      <>
                        <div className="font-semibold">{topMovers[0].symbol}</div>
                        <div className={`text-xs ${topMovers[0].change_percent >= 0 ? 'text-success' : 'text-danger'}`}>
                          {topMovers[0].change_percent >= 0 ? '+' : ''}{topMovers[0].change_percent?.toFixed(2)}%
                        </div>
                      </>
                    ) : (
                      <div className="text-xs text-gray-400">---</div>
                    )}
                  </div>
                </div>
              </div>
            )}
          </div>
        </motion.div>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          {portfolioStats.map((stat, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
              className="glass-card p-6 card-hover"
            >
              <div className="flex items-start justify-between mb-4">
                <div className={`w-12 h-12 rounded-xl bg-${stat.color}/10 flex items-center justify-center`}>
                  <stat.icon className={`w-6 h-6 text-${stat.color}`} />
                </div>
                <div className={`flex items-center gap-1 text-sm ${stat.isPositive ? 'text-success' : 'text-danger'}`}>
                  {stat.isPositive ? <ArrowUpRight className="w-4 h-4" /> : <ArrowDownRight className="w-4 h-4" />}
                  {stat.change}
                </div>
              </div>
              <div className="text-2xl font-bold font-display number-display">{stat.value}</div>
              <div className="text-gray-400 text-sm">{stat.title}</div>
            </motion.div>
          ))}
        </div>

        {/* Main Content Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Portfolio Performance Chart */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 }}
            className="lg:col-span-2 glass-card p-6"
          >
            <div className="flex items-center justify-between mb-6">
              <div>
                <h2 className="text-xl font-semibold">Portfolio Performance</h2>
                <p className="text-gray-400 text-sm">
                  {portfolios.length > 0 ? `${portfolios.length} active portfolio${portfolios.length > 1 ? 's' : ''}` : 'No portfolios yet'}
                </p>
              </div>
              <div className="flex items-center gap-2">
                <span className="flex items-center gap-1 text-sm text-success">
                  <Zap className="w-4 h-4" />
                  AI Optimized
                </span>
              </div>
            </div>
            {portfolios.length > 0 ? (
              <PortfolioChart portfolios={portfolios} />
            ) : (
              <div className="text-center py-12">
                <Sparkles className="w-12 h-12 mx-auto mb-4 text-primary/50" />
                <p className="text-gray-400 mb-4">No portfolios yet</p>
                <Link to="/onboarding" className="btn-primary inline-block">
                  Create Your First Portfolio
                </Link>
              </div>
            )}
          </motion.div>

          {/* Asset Allocation */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.5 }}
            className="glass-card p-6"
          >
            <h2 className="text-xl font-semibold mb-6">Asset Allocation</h2>
            {portfolios.length > 0 && portfolios[0]?.holdings ? (
              <AssetAllocation holdings={portfolios[0].holdings} />
            ) : (
              <div className="text-center py-8 text-gray-500">
                <PieChart className="w-12 h-12 mx-auto mb-3 opacity-50" />
                <p>Create a portfolio to see allocation</p>
              </div>
            )}
          </motion.div>
        </div>

        {/* Recent Activity & AI Insights */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mt-8">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.6 }}
            className="glass-card p-6"
          >
            <h2 className="text-xl font-semibold mb-6">Recent Activity</h2>
            <RecentActivity portfolios={portfolios} />
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.7 }}
            className="glass-card p-6"
          >
            <div className="flex items-center gap-2 mb-6">
              <Brain className="w-5 h-5 text-primary" />
              <h2 className="text-xl font-semibold">AI Insights</h2>
            </div>
            <div className="space-y-4">
              {aiInsights.length > 0 ? (
                aiInsights.map((insight, index) => (
                  <div
                    key={index}
                    className="p-4 rounded-lg bg-dark-lighter border border-gray-800 hover:border-primary/30 transition-colors"
                  >
                    <div className="flex items-start justify-between mb-2">
                      <h3 className="font-medium">{insight.title}</h3>
                      <span className={`text-xs px-2 py-1 rounded-full ${
                        insight.type === 'opportunity' ? 'bg-success/20 text-success' :
                        insight.type === 'action' ? 'bg-primary/20 text-primary' :
                        insight.type === 'warning' ? 'bg-warning/20 text-warning' :
                        'bg-gray-700 text-gray-300'
                      }`}>
                        {insight.confidence.toFixed(0)}% confidence
                      </span>
                    </div>
                    <p className="text-gray-400 text-sm">{insight.description}</p>
                  </div>
                ))
              ) : (
                <div className="text-center py-8 text-gray-500">
                  <AlertCircle className="w-12 h-12 mx-auto mb-3 opacity-50" />
                  <p>No insights available yet</p>
                </div>
              )}
            </div>
          </motion.div>
        </div>

        {/* Top Movers Section */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.8 }}
          className="mt-8"
        >
          <div className="glass-card p-6">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-semibold">Today's Top Movers</h2>
              <span className="text-sm text-gray-400">Real-time data</span>
            </div>
            {isLoading ? (
              <div className="flex items-center justify-center py-8">
                <Loader2 className="w-8 h-8 text-primary animate-spin" />
              </div>
            ) : (
              <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
                {topMovers.map((stock, index) => (
                  <div key={index} className="p-4 rounded-lg bg-dark-lighter">
                    <div className="font-bold text-lg">{stock.symbol}</div>
                    <div className="text-gray-400 text-sm">${stock.price?.toFixed(2)}</div>
                    <div className={`text-sm font-medium ${stock.change_percent >= 0 ? 'text-success' : 'text-danger'}`}>
                      {stock.change_percent >= 0 ? '+' : ''}{stock.change_percent?.toFixed(2)}%
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </motion.div>
      </div>
    </div>
  )
}
