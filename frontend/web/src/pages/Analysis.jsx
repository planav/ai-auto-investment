import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { 
  Search, 
  Brain, 
  TrendingUp, 
  TrendingDown,
  Activity,
  BarChart3,
  PieChart,
  ArrowRight,
  Sparkles,
  Loader2
} from 'lucide-react'
import { marketApi } from '../services/api'
import toast from 'react-hot-toast'

export default function Analysis() {
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedAsset, setSelectedAsset] = useState(null)
  const [popularAssets, setPopularAssets] = useState([])
  const [marketOverview, setMarketOverview] = useState({
    SPY: { name: 'S&P 500', price: 0, change: 0, change_percent: 0 },
    QQQ: { name: 'NASDAQ', price: 0, change: 0, change_percent: 0 },
    DIA: { name: 'Dow Jones', price: 0, change: 0, change_percent: 0 },
    IWM: { name: 'Russell 2000', price: 0, change: 0, change_percent: 0 }
  })
  const [isLoading, setIsLoading] = useState(true)
  const [isSearching, setIsSearching] = useState(false)
  const [searchResults, setSearchResults] = useState([])
  const [aiAnalysis, setAiAnalysis] = useState(null)
  const [, setIsAnalyzing] = useState(false)

  // Fetch real market data on mount
  useEffect(() => {
    fetchMarketData()
    // Refresh data every 60 seconds
    const interval = setInterval(fetchMarketData, 60000)
    return () => clearInterval(interval)
  }, [])

  const fetchMarketData = async () => {
    try {
      setIsLoading(true)
      
      // Fetch market overview (indices)
      const overviewRes = await marketApi.getMarketOverview()
      if (overviewRes.data?.indices) {
        setMarketOverview(overviewRes.data.indices)
      }
      
      // Fetch popular stocks
      const popularRes = await marketApi.getPopularStocks()
      if (popularRes.data) {
        // Map API response to our format with AI signals derived from price action
        const assets = popularRes.data.slice(0, 8).map(stock => {
          const change = stock.change_percent
          let aiSignal, confidence
          if (change > 2.5) { aiSignal = 'strong_buy'; confidence = 74 }
          else if (change > 0.5) { aiSignal = 'buy'; confidence = 64 }
          else if (change > -0.5) { aiSignal = 'hold'; confidence = 60 }
          else if (change > -2.5) { aiSignal = 'sell'; confidence = 64 }
          else { aiSignal = 'strong_sell'; confidence = 72 }
          return {
            symbol: stock.symbol,
            name: getCompanyName(stock.symbol),
            price: stock.price,
            change,
            aiSignal,
            confidence,
          }
        })
        setPopularAssets(assets)
      }
    } catch (error) {
      console.error('Error fetching market data:', error)
      toast.error('Failed to load market data')
    } finally {
      setIsLoading(false)
    }
  }

  const getCompanyName = (symbol) => {
    const names = {
      'AAPL': 'Apple Inc.',
      'MSFT': 'Microsoft Corp.',
      'GOOGL': 'Alphabet Inc.',
      'AMZN': 'Amazon.com Inc.',
      'TSLA': 'Tesla Inc.',
      'META': 'Meta Platforms Inc.',
      'NVDA': 'NVIDIA Corp.',
      'NFLX': 'Netflix Inc.',
      'AMD': 'Advanced Micro Devices',
      'INTC': 'Intel Corp.',
      'CRM': 'Salesforce Inc.',
      'ADBE': 'Adobe Inc.',
      'PYPL': 'PayPal Holdings',
      'UBER': 'Uber Technologies',
      'COIN': 'Coinbase Global'
    }
    return names[symbol] || symbol
  }

  const handleSearch = async (e) => {
    e.preventDefault()
    if (!searchQuery.trim()) return
    
    setIsSearching(true)
    const upperQuery = searchQuery.trim().toUpperCase()
    try {
      const response = await marketApi.searchStocks(searchQuery)
      const results = response.data || []
      setSearchResults(results)
      
      if (results.length > 0) {
        // Auto-select first result and get AI analysis
        await fetchAIAnalysis(results[0].symbol)
      } else {
        // No search results - try AI analysis directly with the typed symbol
        toast(`Showing AI analysis for ${upperQuery}`, { icon: 'ℹ️' })
        await fetchAIAnalysis(upperQuery)
      }
    } catch {
      // Search API unavailable - try AI analysis directly with typed symbol
      toast(`Showing AI analysis for ${upperQuery}`, { icon: 'ℹ️' })
      await fetchAIAnalysis(upperQuery)
    } finally {
      setIsSearching(false)
    }
  }

  const fetchAIAnalysis = async (symbol) => {
    setIsAnalyzing(true)
    try {
      const response = await marketApi.getAIAnalysis(symbol)
      setAiAnalysis(response.data)
      setSelectedAsset({
        symbol: response.data.symbol,
        signal: response.data.signal,
        confidence: response.data.confidence,
        rationale: response.data.rationale
      })
    } catch (error) {
      console.error('AI analysis error:', error)
      toast.error('Failed to get AI analysis')
    } finally {
      setIsAnalyzing(false)
    }
  }

  const handleAssetClick = async (asset) => {
    await fetchAIAnalysis(asset.symbol)
  }

  const aiModels = [
    { name: 'Temporal Fusion Transformer', status: 'active', description: 'Multi-horizon forecasting with interpretable attention' },
    { name: 'Graph Attention Network', status: 'active', description: 'Cross-asset relationship modeling' },
    { name: 'LSTM + Attention', status: 'active', description: 'Sequential pattern recognition' },
    { name: 'PatchTST', status: 'coming_soon', description: 'Patch-based time series transformer' },
  ]

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
            <span className="text-gradient">AI Analysis</span>
          </h1>
          <p className="text-gray-400">
            Deep learning powered asset analysis with real-time market data
          </p>
        </motion.div>

        {/* Market Overview - Real Data */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8"
        >
          {Object.entries(marketOverview).map(([key, data]) => (
            <div key={key} className="glass-card p-4">
              <div className="text-gray-400 text-sm mb-1 uppercase">{data.name || key}</div>
              <div className="text-xl font-bold font-display">
                ${data.price?.toLocaleString() || '---'}
              </div>
              <div className={`text-sm ${(data.change_percent || 0) >= 0 ? 'text-success' : 'text-danger'}`}>
                {(data.change_percent || 0) >= 0 ? '+' : ''}{data.change_percent?.toFixed(2) || '0.00'}%
              </div>
            </div>
          ))}
        </motion.div>

        {/* Search */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="mb-8"
        >
          <form onSubmit={handleSearch} className="relative max-w-2xl">
            <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-500" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search assets (e.g., AAPL, MSFT, TSLA)..."
              className="w-full pl-12 pr-12 py-4 glass-card border border-gray-700 rounded-xl focus:outline-none focus:border-primary transition-colors text-lg"
            />
            {isSearching && (
              <Loader2 className="absolute right-4 top-1/2 transform -translate-y-1/2 w-5 h-5 text-primary animate-spin" />
            )}
          </form>
          
          {/* Search Results */}
          {searchResults.length > 0 && (
            <div className="mt-4 glass-card p-4 max-w-2xl">
              <h3 className="text-sm text-gray-400 mb-2">Search Results</h3>
              <div className="space-y-2">
                {searchResults.map((result) => (
                  <button
                    key={result.symbol}
                    onClick={() => fetchAIAnalysis(result.symbol)}
                    className="w-full flex items-center justify-between p-3 rounded-lg bg-dark-lighter hover:bg-dark-lighter/80 transition-colors"
                  >
                    <div className="flex items-center gap-3">
                      <span className="font-bold text-primary">{result.symbol}</span>
                      <span className="text-gray-400">{result.name}</span>
                    </div>
                    <ArrowRight className="w-4 h-4 text-gray-500" />
                  </button>
                ))}
              </div>
            </div>
          )}
        </motion.div>

        {/* AI Analysis Result */}
        {selectedAsset && aiAnalysis && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="mb-8"
          >
            <div className="glass-card p-6 border border-primary/30">
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-3">
                  <Brain className="w-8 h-8 text-primary" />
                  <div>
                    <h2 className="text-2xl font-bold">{selectedAsset.symbol}</h2>
                    <p className="text-gray-400">AI-Powered Analysis</p>
                  </div>
                </div>
                <span className={`px-4 py-2 rounded-full text-sm font-bold ${
                  aiAnalysis.signal === 'buy' || aiAnalysis.signal === 'strong_buy' ? 'bg-success/20 text-success' :
                  aiAnalysis.signal === 'sell' ? 'bg-danger/20 text-danger' :
                  'bg-warning/20 text-warning'
                }`}>
                  {aiAnalysis.signal?.toUpperCase()}
                </span>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
                <div className="bg-dark-lighter p-4 rounded-lg">
                  <div className="text-gray-400 text-sm">Confidence</div>
                  <div className="text-2xl font-bold text-primary">{aiAnalysis.confidence}%</div>
                </div>
                <div className="bg-dark-lighter p-4 rounded-lg">
                  <div className="text-gray-400 text-sm">Risk Level</div>
                  <div className="text-2xl font-bold capitalize">{aiAnalysis.risk_level}</div>
                </div>
                <div className="bg-dark-lighter p-4 rounded-lg">
                  <div className="text-gray-400 text-sm">Key Factors</div>
                  <div className="text-sm">{aiAnalysis.key_factors?.length || 0} identified</div>
                </div>
              </div>
              
              <div className="bg-dark-lighter p-4 rounded-lg">
                <div className="text-gray-400 text-sm mb-2">AI Rationale</div>
                <p className="text-gray-300">{aiAnalysis.rationale}</p>
              </div>
              
              {aiAnalysis.key_factors?.length > 0 && (
                <div className="mt-4">
                  <div className="text-gray-400 text-sm mb-2">Key Factors</div>
                  <div className="flex flex-wrap gap-2">
                    {aiAnalysis.key_factors.map((factor, idx) => (
                      <span key={idx} className="px-3 py-1 bg-primary/10 text-primary rounded-full text-sm">
                        {factor}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </motion.div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Popular Assets - Real Data */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
            className="lg:col-span-2"
          >
            <div className="glass-card p-6">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-xl font-semibold">Popular Assets</h2>
                <span className="flex items-center gap-2 text-sm text-primary">
                  <Sparkles className="w-4 h-4" />
                  Live Data
                </span>
              </div>

              {isLoading ? (
                <div className="flex items-center justify-center py-12">
                  <Loader2 className="w-8 h-8 text-primary animate-spin" />
                </div>
              ) : (
                <div className="space-y-4">
                  {popularAssets.map((asset, index) => (
                    <div
                      key={index}
                      className="flex items-center justify-between p-4 rounded-lg bg-dark-lighter hover:bg-dark-lighter/80 transition-colors cursor-pointer group"
                      onClick={() => handleAssetClick(asset)}
                    >
                      <div className="flex items-center gap-4">
                        <div className="w-12 h-12 rounded-xl bg-primary/10 flex items-center justify-center">
                          <span className="font-bold text-primary">{asset.symbol[0]}</span>
                        </div>
                        <div>
                          <div className="font-semibold">{asset.symbol}</div>
                          <div className="text-sm text-gray-400">{asset.name}</div>
                        </div>
                      </div>

                      <div className="text-right">
                        <div className="font-semibold">${asset.price?.toFixed(2)}</div>
                        <div className={`text-sm ${asset.change >= 0 ? 'text-success' : 'text-danger'}`}>
                          {asset.change >= 0 ? '+' : ''}{asset.change?.toFixed(2)}%
                        </div>
                      </div>

                      <div className="flex items-center gap-4">
                        <div className="text-right">
                          <span className={`px-3 py-1 rounded-full text-xs font-medium ${
                            asset.aiSignal === 'strong_buy' ? 'bg-success/20 text-success' :
                            asset.aiSignal === 'buy' ? 'bg-primary/20 text-primary' :
                            asset.aiSignal === 'sell' ? 'bg-danger/20 text-danger' :
                            'bg-gray-700 text-gray-400'
                          }`}>
                            {asset.aiSignal?.replace('_', ' ').toUpperCase()}
                          </span>
                          <div className="text-xs text-gray-500 mt-1">{asset.confidence}% confidence</div>
                        </div>
                        <ArrowRight className="w-5 h-5 text-gray-500 group-hover:text-primary transition-colors" />
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </motion.div>

          {/* AI Models */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 }}
          >
            <div className="glass-card p-6">
              <div className="flex items-center gap-2 mb-6">
                <Brain className="w-5 h-5 text-primary" />
                <h2 className="text-xl font-semibold">AI Models</h2>
              </div>

              <div className="space-y-4">
                {aiModels.map((model, index) => (
                  <div
                    key={index}
                    className="p-4 rounded-lg bg-dark-lighter"
                  >
                    <div className="flex items-start justify-between mb-2">
                      <h3 className="font-medium text-sm">{model.name}</h3>
                      <span className={`px-2 py-0.5 rounded-full text-xs ${
                        model.status === 'active' ? 'bg-success/20 text-success' :
                        'bg-warning/20 text-warning'
                      }`}>
                        {model.status === 'active' ? 'Active' : 'Coming Soon'}
                      </span>
                    </div>
                    <p className="text-xs text-gray-400">{model.description}</p>
                  </div>
                ))}
              </div>

              <button className="w-full mt-6 btn-secondary text-sm">
                View All Models
              </button>
            </div>

            {/* Quick Stats */}
            <div className="glass-card p-6 mt-6">
              <h3 className="font-semibold mb-4">Analysis Stats</h3>
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-gray-400 text-sm">Active Models</span>
                  <span className="font-bold">{aiModels.filter(m => m.status === 'active').length}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-gray-400 text-sm">Data Sources</span>
                  <span className="font-bold">Finnhub · Yahoo Finance</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-gray-400 text-sm">Signal Types</span>
                  <span className="font-bold text-success">RSI · MA · Momentum</span>
                </div>
              </div>
            </div>
          </motion.div>
        </div>

        {/* Feature Cards */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
          className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-8"
        >
          {[
            {
              icon: BarChart3,
              title: 'Technical Analysis',
              description: 'Advanced chart patterns and indicator analysis using deep learning',
              color: 'primary',
            },
            {
              icon: PieChart,
              title: 'Fundamental Analysis',
              description: 'AI-powered evaluation of financial statements and metrics',
              color: 'secondary',
            },
            {
              icon: Activity,
              title: 'Sentiment Analysis',
              description: 'Real-time sentiment from news, social media, and market data',
              color: 'accent',
            },
          ].map((feature, index) => (
            <div
              key={index}
              className="glass-card p-6 card-hover group cursor-pointer"
            >
              <div className={`w-12 h-12 rounded-xl bg-${feature.color}/10 flex items-center justify-center mb-4 group-hover:scale-110 transition-transform`}>
                <feature.icon className={`w-6 h-6 text-${feature.color}`} />
              </div>
              <h3 className="text-lg font-semibold mb-2">{feature.title}</h3>
              <p className="text-gray-400 text-sm">{feature.description}</p>
            </div>
          ))}
        </motion.div>
      </div>
    </div>
  )
}
