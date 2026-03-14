import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import { 
  Brain, 
  TrendingUp, 
  Shield, 
  Zap, 
  LineChart, 
  PieChart,
  ArrowRight,
  Sparkles,
  Cpu,
  Network,
  Loader2,
  Globe,
  ArrowUpRight,
  ArrowDownRight,
  BarChart3,
  Users,
  Lock
} from 'lucide-react'
import { marketApi } from '../services/api'
import { useAuthStore } from '../store/authStore'

export default function Home() {
  const { isAuthenticated, user } = useAuthStore()
  const [marketData, setMarketData] = useState(null)
  const [popularStocks, setPopularStocks] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchMarketData()
  }, [])

  const fetchMarketData = async () => {
    try {
      setLoading(true)
      
      // Fetch market overview (public endpoint)
      const overviewRes = await marketApi.getMarketOverview()
      setMarketData(overviewRes.data)
      
      // Fetch popular stocks (public endpoint)
      const popularRes = await marketApi.getPopularStocks()
      setPopularStocks(popularRes.data || [])
      
    } catch (err) {
      console.error('Failed to fetch market data:', err)
    } finally {
      setLoading(false)
    }
  }

  const features = [
    {
      icon: Brain,
      title: 'AI Research Agent',
      description: 'Advanced fundamental and sentiment analysis powered by large language models',
      color: 'from-primary to-primary-light',
    },
    {
      icon: Cpu,
      title: 'Deep Learning Models',
      description: 'Temporal Fusion Transformers, LSTMs, and Graph Neural Networks for predictions',
      color: 'from-secondary to-secondary-light',
    },
    {
      icon: PieChart,
      title: 'Smart Allocation',
      description: 'Mean-variance optimization with risk parity and equal risk contribution',
      color: 'from-accent to-accent-light',
    },
    {
      icon: Shield,
      title: 'Risk Management',
      description: 'Comprehensive VaR, CVaR, and stress testing for portfolio protection',
      color: 'from-primary to-secondary',
    },
    {
      icon: LineChart,
      title: 'Backtesting',
      description: 'Historical simulation with multiple model comparisons',
      color: 'from-secondary to-accent',
    },
    {
      icon: Network,
      title: 'Explainable AI',
      description: 'Transparent decision-making with SHAP values and attention visualization',
      color: 'from-accent to-primary',
    },
  ]

  const getStatusColor = (status) => {
    switch (status) {
      case 'open': return 'text-success'
      case 'closed': return 'text-danger'
      default: return 'text-warning'
    }
  }

  return (
    <div className="pt-24">
      {/* Hero Section */}
      <section className="relative min-h-[90vh] flex items-center justify-center px-4">
        <div className="max-w-6xl mx-auto text-center">
          {/* Badge */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-primary/10 border border-primary/30 mb-8"
          >
            <Sparkles className="w-4 h-4 text-primary" />
            <span className="text-sm text-primary font-medium">
              Powered by State-of-the-Art AI
            </span>
          </motion.div>

          {/* Main Headline */}
          <motion.h1
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="text-5xl md:text-7xl font-bold font-display mb-6 leading-tight"
          >
            <span className="text-white">Invest Smarter with</span>
            <br />
            <span className="text-gradient">Intelligent AI</span>
          </motion.h1>

          {/* Subheadline */}
          <motion.p
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="text-xl text-gray-400 max-w-2xl mx-auto mb-10"
          >
            AutoInvest combines deep learning, quantitative analysis, and AI research 
            to build optimized portfolios tailored to your goals.
          </motion.p>

          {/* CTA Buttons */}
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
            className="flex flex-col sm:flex-row items-center justify-center gap-4"
          >
            {isAuthenticated ? (
              <>
                <Link to="/dashboard" className="btn-primary text-lg px-8 py-4">
                  Go to Dashboard
                  <ArrowRight className="inline-block ml-2 w-5 h-5" />
                </Link>
                <div className="flex items-center gap-2 text-gray-300">
                  <span>Welcome, {user?.full_name?.split(' ')[0] || 'Investor'}</span>
                </div>
              </>
            ) : (
              <>
                <Link to="/register" className="btn-primary text-lg px-8 py-4">
                  Start Investing
                  <ArrowRight className="inline-block ml-2 w-5 h-5" />
                </Link>
                <Link to="/login" className="btn-secondary text-lg px-8 py-4">
                  Sign In
                </Link>
              </>
            )}
          </motion.div>

          {/* Live Market Ticker */}
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 }}
            className="mt-16"
          >
            <div className="glass-card p-6 max-w-4xl mx-auto">
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-2">
                  <Globe className="w-4 h-4 text-primary" />
                  <span className="text-sm text-gray-400">Live Market</span>
                  {marketData?.market_status && (
                    <span className={`text-xs px-2 py-0.5 rounded-full ${getStatusColor(marketData.market_status) === 'text-success' ? 'bg-success/20 text-success' : getStatusColor(marketData.market_status) === 'text-danger' ? 'bg-danger/20 text-danger' : 'bg-warning/20 text-warning'}`}>
                      {marketData.market_status.charAt(0).toUpperCase() + marketData.market_status.slice(1)}
                    </span>
                  )}
                  <span className="flex w-2 h-2 bg-success rounded-full animate-pulse"></span>
                </div>
                <span className="text-xs text-gray-500">
                  {marketData?.timestamp ? new Date(marketData.timestamp).toLocaleTimeString() : ''}
                </span>
              </div>
              
              {loading ? (
                <div className="flex items-center justify-center py-4">
                  <Loader2 className="w-6 h-6 text-primary animate-spin" />
                </div>
              ) : (
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  {marketData?.indices && Object.entries(marketData.indices).map(([key, index]) => (
                    <div key={key} className="p-3 bg-dark-lighter rounded-lg">
                      <div className="text-xs text-gray-500 mb-1">{index.name}</div>
                      <div className="font-semibold text-lg">{index.price?.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</div>
                      <div className={`text-sm flex items-center gap-1 ${index.change >= 0 ? 'text-success' : 'text-danger'}`}>
                        {index.change >= 0 ? <ArrowUpRight className="w-3 h-3" /> : <ArrowDownRight className="w-3 h-3" />}
                        {index.change >= 0 ? '+' : ''}{index.change_percent?.toFixed(2)}%
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </motion.div>
        </div>
      </section>

      {/* Popular Stocks Section */}
      <section className="py-12 px-4 bg-dark-lighter/30">
        <div className="max-w-6xl mx-auto">
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-xl font-semibold flex items-center gap-2">
              <BarChart3 className="w-5 h-5 text-primary" />
              Trending Stocks
            </h3>
            {isAuthenticated ? (
              <Link to="/analysis" className="text-primary text-sm hover:underline flex items-center gap-1">
                Get AI Analysis <ArrowRight className="w-4 h-4" />
              </Link>
            ) : (
              <Link to="/login" className="text-primary text-sm hover:underline flex items-center gap-1">
                Sign in for AI Analysis <ArrowRight className="w-4 h-4" />
              </Link>
            )}
          </div>
          
          {loading ? (
            <div className="flex items-center justify-center py-8">
              <Loader2 className="w-6 h-6 text-primary animate-spin" />
            </div>
          ) : (
            <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-3">
              {popularStocks.slice(0, 12).map((stock) => (
                <motion.div
                  key={stock.symbol}
                  whileHover={{ scale: 1.02 }}
                  className="glass-card p-4 card-hover"
                >
                  <div className="flex items-center justify-between mb-2">
                    <span className="font-bold">{stock.symbol}</span>
                    <span className={`text-xs flex items-center gap-0.5 ${stock.change_percent >= 0 ? 'text-success' : 'text-danger'}`}>
                      {stock.change_percent >= 0 ? <ArrowUpRight className="w-3 h-3" /> : <ArrowDownRight className="w-3 h-3" />}
                      {stock.change_percent >= 0 ? '+' : ''}{stock.change_percent?.toFixed(2)}%
                    </span>
                  </div>
                  <div className="text-lg font-semibold">${stock.price?.toFixed(2)}</div>
                  <div className={`text-xs ${stock.change >= 0 ? 'text-success' : 'text-danger'}`}>
                    {stock.change >= 0 ? '+' : ''}{stock.change?.toFixed(2)}
                  </div>
                </motion.div>
              ))}
            </div>
          )}
        </div>
      </section>

      {/* Features Section */}
      <section className="py-24 px-4">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold font-display mb-4">
              <span className="text-gradient">Advanced Capabilities</span>
            </h2>
            <p className="text-gray-400 max-w-2xl mx-auto">
              Our platform leverages cutting-edge machine learning and quantitative finance 
              techniques to deliver superior investment insights.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {features.map((feature, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
                viewport={{ once: true }}
                className="glass-card p-6 card-hover group"
              >
                <div className={`w-12 h-12 rounded-xl bg-gradient-to-br ${feature.color} flex items-center justify-center mb-4 group-hover:scale-110 transition-transform`}>
                  <feature.icon className="w-6 h-6 text-dark" />
                </div>
                <h3 className="text-xl font-semibold mb-2">{feature.title}</h3>
                <p className="text-gray-400 text-sm">{feature.description}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* How It Works Section */}
      <section className="py-24 px-4 bg-dark-lighter/30">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold font-display mb-4">
              <span className="text-gradient">How It Works</span>
            </h2>
            <p className="text-gray-400 max-w-2xl mx-auto">
              Get started in minutes with our simple investment process
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {[
              {
                step: '01',
                title: 'Create Account',
                description: 'Sign up for free and set your investment preferences and risk tolerance.',
                icon: Users,
              },
              {
                step: '02',
                title: 'Deposit Funds',
                description: 'Add simulated funds to your wallet to start building portfolios.',
                icon: Sparkles,
              },
              {
                step: '03',
                title: 'AI Does the Work',
                description: 'Our AI analyzes thousands of stocks and builds an optimized portfolio for you.',
                icon: Brain,
              },
            ].map((item, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
                viewport={{ once: true }}
                className="glass-card p-8 relative"
              >
                <div className="absolute -top-4 -left-4 w-12 h-12 rounded-full bg-gradient-to-br from-primary to-secondary flex items-center justify-center text-xl font-bold">
                  {item.step}
                </div>
                <div className={`w-12 h-12 rounded-xl bg-gradient-to-br from-primary/20 to-secondary/20 flex items-center justify-center mb-4 mt-2`}>
                  <item.icon className="w-6 h-6 text-primary" />
                </div>
                <h3 className="text-xl font-semibold mb-2">{item.title}</h3>
                <p className="text-gray-400 text-sm">{item.description}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Model Zoo Section */}
      <section className="py-24 px-4">
        <div className="max-w-7xl mx-auto">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
            <div>
              <h2 className="text-4xl font-bold font-display mb-6">
                <span className="text-white">Deep Learning</span>
                <br />
                <span className="text-gradient">Model Zoo</span>
              </h2>
              <p className="text-gray-400 mb-8">
                Our Quant Engine implements the latest architectures in deep learning 
                for financial time series prediction. From Temporal Fusion Transformers 
                to Graph Neural Networks, we use the best model for each prediction task.
              </p>
              
              <div className="space-y-4">
                {[
                  { name: 'Temporal Fusion Transformer', type: 'Multi-horizon forecasting', status: 'Coming Soon', description: 'Advanced transformer for interpretable time series forecasting' },
                  { name: 'LSTM + Attention', type: 'Sequential patterns', status: 'Coming Soon', description: 'Long short-term memory with self-attention mechanism' },
                  { name: 'PatchTST', type: 'Long sequence modeling', status: 'Coming Soon', description: 'Patch Time Series Transformer - state-of-the-art accuracy' },
                  { name: 'N-BEATS', type: 'Trend & seasonality', status: 'Coming Soon', description: 'Neural basis expansion for interpretable time series' },
                ].map((model, index) => (
                  <motion.div
                    key={index}
                    initial={{ opacity: 0, x: -20 }}
                    whileInView={{ opacity: 1, x: 0 }}
                    transition={{ delay: index * 0.1 }}
                    viewport={{ once: true }}
                    className="flex items-center justify-between p-4 glass-card"
                  >
                    <div>
                      <div className="font-semibold">{model.name}</div>
                      <div className="text-sm text-gray-400">{model.type}</div>
                    </div>
                    <div className={`text-sm font-medium px-3 py-1 rounded-full ${
                      model.status === 'Ready' 
                        ? 'bg-success/20 text-success' 
                        : 'bg-warning/20 text-warning'
                    }`}>
                      {model.status}
                    </div>
                  </motion.div>
                ))}
              </div>
              
              <div className="mt-6 p-4 bg-dark-lighter rounded-lg">
                <p className="text-sm text-gray-400">
                  <Zap className="w-4 h-4 inline mr-2 text-warning" />
                  Models are currently being trained. Once ready, they'll analyze thousands of stocks 
                  and provide AI-powered investment recommendations.
                </p>
              </div>
            </div>

            <div className="relative">
              <div className="glass-card p-8 holographic">
                <div className="flex items-center justify-between mb-6">
                  <div className="flex items-center gap-3">
                    <div className="w-3 h-3 rounded-full bg-warning animate-pulse" />
                    <span className="text-sm text-warning font-mono">MODEL TRAINING IN PROGRESS</span>
                  </div>
                  <Brain className="w-5 h-5 text-warning" />
                </div>
                
                {/* Dynamic prediction visualization */}
                <div className="space-y-4">
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-400">Status</span>
                    <span className="text-warning font-mono">Initializing...</span>
                  </div>
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-400">Training Progress</span>
                    <span className="font-mono">0%</span>
                  </div>
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-400">Est. Completion</span>
                    <span className="text-gray-500 font-mono">TBD</span>
                  </div>
                  
                  {/* Placeholder chart */}
                  <div className="mt-6 h-32 flex items-end gap-1 opacity-30">
                    {[35, 45, 40, 55, 50, 65, 60, 75, 70, 85, 80, 95, 90].map((h, i) => (
                      <motion.div
                        key={i}
                        initial={{ height: 0 }}
                        whileInView={{ height: `${h}%` }}
                        transition={{ delay: i * 0.05, duration: 0.3 }}
                        viewport={{ once: true }}
                        className={`flex-1 rounded-t ${
                          i > 8 ? 'bg-gradient-to-t from-success/50 to-success' : 'bg-gradient-to-t from-primary/50 to-primary'
                        }`}
                      />
                    ))}
                  </div>
                  
                  <div className="flex items-center justify-between text-xs text-gray-500 mt-2">
                    <span>Waiting</span>
                    <span>For</span>
                    <span>Training</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Security Section */}
      <section className="py-24 px-4 bg-dark-lighter/30">
        <div className="max-w-4xl mx-auto text-center">
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            whileInView={{ opacity: 1, scale: 1 }}
            viewport={{ once: true }}
            className="glass-card p-12"
          >
            <div className="w-16 h-16 rounded-full bg-success/20 flex items-center justify-center mx-auto mb-6">
              <Lock className="w-8 h-8 text-success" />
            </div>
            <h2 className="text-3xl font-bold font-display mb-4">
              Safe & Secure Simulation
            </h2>
            <p className="text-gray-400 mb-6 max-w-xl mx-auto">
              AutoInvest is a simulation platform for learning and research purposes. 
              No real money is involved - practice investing with fake funds and 
              understand how AI-driven investing works.
            </p>
            <div className="flex items-center justify-center gap-6 text-sm text-gray-500">
              <div className="flex items-center gap-2">
                <Shield className="w-4 h-4 text-success" />
                <span>Simulation Only</span>
              </div>
              <div className="flex items-center gap-2">
                <Zap className="w-4 h-4 text-success" />
                <span>Learn Risk-Free</span>
              </div>
              <div className="flex items-center gap-2">
                <Brain className="w-4 h-4 text-success" />
                <span>AI-Powered Insights</span>
              </div>
            </div>
          </motion.div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-24 px-4">
        <div className="max-w-4xl mx-auto text-center">
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            whileInView={{ opacity: 1, scale: 1 }}
            viewport={{ once: true }}
            className="glass-card p-12 relative overflow-hidden"
          >
            {/* Background glow */}
            <div className="absolute inset-0 bg-gradient-to-r from-primary/20 via-secondary/20 to-accent/20 blur-3xl" />
            
            <div className="relative z-10">
              <h2 className="text-4xl font-bold font-display mb-4">
                Ready to <span className="text-gradient">Transform</span> Your Investments?
              </h2>
              <p className="text-gray-400 mb-8 max-w-xl mx-auto">
                Join thousands of investors using AI-powered insights to build 
                smarter portfolios. Start your journey today.
              </p>
              <Link to="/register" className="btn-primary text-lg px-8 py-4 inline-block">
                Create Free Account
                <ArrowRight className="inline-block ml-2 w-5 h-5" />
              </Link>
            </div>
          </motion.div>
        </div>
      </section>
    </div>
  )
}
