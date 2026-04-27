import { useState, useEffect } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import {
  DollarSign,
  Shield,
  TrendingUp,
  Loader2,
  CheckCircle,
  ArrowRight,
  ArrowLeft,
  Sparkles,
  Wallet,
  AlertCircle,
  Brain,
  Newspaper,
  BarChart3,
  Zap,
  X
} from 'lucide-react'
import { useAuthStore } from '../store/authStore'
import { walletApi, portfolioApi } from '../services/api'
import toast from 'react-hot-toast'

const RISK_PROFILES = {
  conservative: {
    name: 'Conservative',
    description: 'Lower risk, stable returns',
    expectedReturn: '5-8%',
    volatility: 'Low',
    color: 'success'
  },
  moderate: {
    name: 'Moderate',
    description: 'Balanced risk and returns',
    expectedReturn: '8-12%',
    volatility: 'Medium',
    color: 'primary'
  },
  aggressive: {
    name: 'Aggressive',
    description: 'Higher risk, potential higher returns',
    expectedReturn: '12-20%',
    volatility: 'High',
    color: 'danger'
  }
}

export default function Invest() {
  const { isAuthenticated } = useAuthStore()
  const navigate = useNavigate()
  
  const [step, setStep] = useState(1)
  const [isCreating, setIsCreating] = useState(false)
  const [aiResult, setAiResult] = useState(null)   // holds the created portfolio for the AI summary screen
  
  // Form state
  const [walletBalance, setWalletBalance] = useState(0)
  const [amount, setAmount] = useState(10000)
  const [riskProfile, setRiskProfile] = useState('moderate')
  const [portfolioName] = useState('')
  
  useEffect(() => {
    if (!isAuthenticated) {
      navigate('/login')
    } else {
      fetchWalletBalance()
    }
  }, [isAuthenticated, navigate])
  
  const fetchWalletBalance = async () => {
    try {
      const res = await walletApi.getBalance()
      if (res.data) {
        setWalletBalance(res.data.balance || 0)
      }
    } catch (error) {
      console.error('Error fetching wallet:', error)
    }
  }
  
  const canProceed = () => {
    if (step === 1) {
      return amount >= 1000 && amount <= walletBalance
    }
    if (step === 2) {
      return riskProfile in RISK_PROFILES
    }
    return true
  }
  
  const handleNext = () => {
    if (step < 3) {
      setStep(step + 1)
    }
  }
  
  const handleBack = () => {
    if (step > 1) {
      setStep(step - 1)
    }
  }
  
  const handleCreatePortfolio = async () => {
    setIsCreating(true)
    try {
      const portfolioNameValue = portfolioName || generatePortfolioName()
      const res = await portfolioApi.create({
        name: portfolioNameValue,
        investment_amount: amount,
        risk_profile: riskProfile,
        cash_reserve_pct: 0.05,
        model_type: 'temporal_fusion_transformer',
      })
      if (res.data) {
        // Show AI analysis summary before navigating
        setAiResult(res.data)
      }
    } catch (error) {
      console.error('Error creating portfolio:', error)
      toast.error(error.response?.data?.detail || 'Failed to create portfolio. Please try again.')
    } finally {
      setIsCreating(false)
    }
  }
  
  const generatePortfolioName = () => {
    const riskName = RISK_PROFILES[riskProfile]?.name || 'Portfolio'
    const date = new Date().toLocaleDateString('en-US', { month: 'short', year: 'numeric' })
    return `${riskName} Portfolio - ${date}`
  }
  
  const cashReserve = amount * 0.05 // 5% cash reserve
  const investableAmount = amount - cashReserve
  
  if (!isAuthenticated) {
    return null
  }
  
  return (
    <div className="pt-24 pb-12 px-4">
      <div className="max-w-2xl mx-auto">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8 text-center"
        >
          <h1 className="text-3xl font-bold font-display mb-2">Start Investing</h1>
          <p className="text-gray-400">Create your AI-powered portfolio in just a few steps</p>
        </motion.div>
        
        {/* Progress Steps */}
        <div className="flex items-center justify-center mb-8">
          {[1, 2, 3].map((s) => (
            <div key={s} className="flex items-center">
              <div className={`w-10 h-10 rounded-full flex items-center justify-center font-semibold ${
                s < step ? 'bg-success text-dark' :
                s === step ? 'bg-primary text-dark' :
                'bg-dark-lighter text-gray-500'
              }`}>
                {s < step ? <CheckCircle className="w-5 h-5" /> : s}
              </div>
              {s < 3 && (
                <div className={`w-16 h-1 ${s < step ? 'bg-success' : 'bg-dark-lighter'}`} />
              )}
            </div>
          ))}
        </div>
        
        {/* Step Labels */}
        <div className="flex justify-between mb-8 text-sm">
          <span className={step >= 1 ? 'text-primary' : 'text-gray-500'}>Amount</span>
          <span className={step >= 2 ? 'text-primary' : 'text-gray-500'}>Risk Profile</span>
          <span className={step >= 3 ? 'text-primary' : 'text-gray-500'}>Review</span>
        </div>
        
        {/* Card */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="glass-card p-8"
        >
          <AnimatePresence mode="wait">
            
            {/* Step 1: Amount */}
            {step === 1 && (
              <motion.div
                key="step1"
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -20 }}
              >
                <div className="flex items-center gap-3 mb-6">
                  <div className="w-12 h-12 rounded-xl bg-primary/10 flex items-center justify-center">
                    <DollarSign className="w-6 h-6 text-primary" />
                  </div>
                  <div>
                    <h2 className="text-xl font-semibold">How much to invest?</h2>
                    <p className="text-gray-400 text-sm">Enter the amount from your wallet</p>
                  </div>
                </div>
                
                {/* Wallet Balance */}
                <div className="flex items-center gap-3 p-4 bg-dark-lighter rounded-lg mb-6">
                  <Wallet className="w-5 h-5 text-accent" />
                  <span className="text-gray-400">Available Balance:</span>
                  <span className="font-semibold text-accent">${walletBalance.toLocaleString()}</span>
                </div>
                
                {/* Amount Input */}
                <div className="mb-6">
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    Investment Amount (USD)
                  </label>
                  <div className="relative">
                    <span className="absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-500">$</span>
                    <input
                      type="number"
                      value={amount}
                      onChange={(e) => setAmount(parseFloat(e.target.value) || 0)}
                      min={1000}
                      max={walletBalance}
                      step={100}
                      className="w-full pl-8 pr-4 py-4 bg-dark-lighter border border-gray-700 rounded-lg focus:outline-none focus:border-primary transition-colors text-xl"
                    />
                  </div>
                </div>
                
                {/* Quick Amounts */}
                <div className="grid grid-cols-4 gap-2 mb-6">
                  {[5000, 10000, 25000, 50000].map((quickAmount) => (
                    <button
                      key={quickAmount}
                      onClick={() => setAmount(quickAmount)}
                      disabled={quickAmount > walletBalance}
                      className={`py-2 px-3 rounded-lg text-sm transition-colors disabled:opacity-30 ${
                        amount === quickAmount
                          ? 'bg-primary text-dark'
                          : 'bg-dark-lighter text-gray-400 hover:text-white hover:bg-gray-800'
                      }`}
                    >
                      ${quickAmount.toLocaleString()}
                    </button>
                  ))}
                </div>
                
                {/* Validation Message */}
                {amount > walletBalance && (
                  <div className="flex items-center gap-2 text-danger text-sm mb-4">
                    <AlertCircle className="w-4 h-4" />
                    Amount exceeds available balance
                  </div>
                )}
                {amount > 0 && amount < 1000 && (
                  <div className="flex items-center gap-2 text-warning text-sm mb-4">
                    <AlertCircle className="w-4 h-4" />
                    Minimum investment is $1,000
                  </div>
                )}
              </motion.div>
            )}
            
            {/* Step 2: Risk Profile */}
            {step === 2 && (
              <motion.div
                key="step2"
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -20 }}
              >
                <div className="flex items-center gap-3 mb-6">
                  <div className="w-12 h-12 rounded-xl bg-primary/10 flex items-center justify-center">
                    <Shield className="w-6 h-6 text-primary" />
                  </div>
                  <div>
                    <h2 className="text-xl font-semibold">What's your risk tolerance?</h2>
                    <p className="text-gray-400 text-sm">Choose your investment risk level</p>
                  </div>
                </div>
                
                {/* Risk Options */}
                <div className="space-y-3">
                  {Object.entries(RISK_PROFILES).map(([key, profile]) => (
                    <button
                      key={key}
                      onClick={() => setRiskProfile(key)}
                      className={`w-full p-4 rounded-lg border-2 text-left transition-all ${
                        riskProfile === key
                          ? 'border-primary bg-primary/10'
                          : 'border-gray-700 bg-dark-lighter hover:border-gray-600'
                      }`}
                    >
                      <div className="flex items-center justify-between">
                        <div>
                          <h3 className={`font-semibold text-${profile.color}`}>{profile.name}</h3>
                          <p className="text-gray-400 text-sm">{profile.description}</p>
                        </div>
                        {riskProfile === key && (
                          <CheckCircle className={`w-6 h-6 text-${profile.color}`} />
                        )}
                      </div>
                      <div className="flex gap-6 mt-3 text-sm">
                        <div>
                          <span className="text-gray-500">Expected Return:</span>
                          <span className="ml-2 text-success">{profile.expectedReturn}</span>
                        </div>
                        <div>
                          <span className="text-gray-500">Volatility:</span>
                          <span className="ml-2">{profile.volatility}</span>
                        </div>
                      </div>
                    </button>
                  ))}
                </div>
              </motion.div>
            )}
            
            {/* Step 3: Review */}
            {step === 3 && (
              <motion.div
                key="step3"
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -20 }}
              >
                <div className="flex items-center gap-3 mb-6">
                  <div className="w-12 h-12 rounded-xl bg-primary/10 flex items-center justify-center">
                    <Sparkles className="w-6 h-6 text-primary" />
                  </div>
                  <div>
                    <h2 className="text-xl font-semibold">Review & Confirm</h2>
                    <p className="text-gray-400 text-sm">Verify your investment details</p>
                  </div>
                </div>
                
                {/* Summary */}
                <div className="space-y-4 mb-6">
                  <div className="flex justify-between p-4 bg-dark-lighter rounded-lg">
                    <span className="text-gray-400">Investment Amount</span>
                    <span className="font-semibold">${amount.toLocaleString()}</span>
                  </div>
                  <div className="flex justify-between p-4 bg-dark-lighter rounded-lg">
                    <span className="text-gray-400">Cash Reserve (5%)</span>
                    <span className="font-semibold text-gray-500">-${cashReserve.toLocaleString()}</span>
                  </div>
                  <div className="flex justify-between p-4 bg-dark-lighter rounded-lg border border-primary/30">
                    <span className="text-gray-400">Investable Amount</span>
                    <span className="font-semibold text-primary">${investableAmount.toLocaleString()}</span>
                  </div>
                  <div className="flex justify-between p-4 bg-dark-lighter rounded-lg">
                    <span className="text-gray-400">Risk Profile</span>
                    <span className={`font-semibold text-${RISK_PROFILES[riskProfile].color}`}>
                      {RISK_PROFILES[riskProfile]?.name}
                    </span>
                  </div>
                </div>
                
                {/* AI Processing Notice */}
                <div className="flex items-start gap-3 p-4 bg-primary/10 rounded-lg mb-6">
                  <Brain className="w-5 h-5 text-primary flex-shrink-0 mt-0.5" />
                  <div className="text-sm">
                    <p className="font-medium text-primary">AI Analysis in Progress</p>
                    <p className="text-gray-400">
                      Our AI will analyze thousands of stocks, apply ML models for predictions, 
                      and create an optimized portfolio based on your risk tolerance.
                    </p>
                  </div>
                </div>
              </motion.div>
            )}
          </AnimatePresence>
          
          {/* Navigation Buttons */}
          <div className="flex items-center justify-between mt-8 pt-6 border-t border-gray-700">
            <button
              onClick={handleBack}
              disabled={step === 1}
              className={`flex items-center gap-2 px-6 py-3 rounded-lg font-medium transition-colors ${
                step === 1
                  ? 'text-gray-600 cursor-not-allowed'
                  : 'text-gray-300 hover:text-white'
              }`}
            >
              <ArrowLeft className="w-5 h-5" />
              Back
            </button>
            
            {step < 3 ? (
              <button
                onClick={handleNext}
                disabled={!canProceed()}
                className={`flex items-center gap-2 px-6 py-3 rounded-lg font-medium transition-colors ${
                  canProceed()
                    ? 'bg-primary text-dark hover:bg-primary/90'
                    : 'bg-gray-700 text-gray-500 cursor-not-allowed'
                }`}
              >
                Continue
                <ArrowRight className="w-5 h-5" />
              </button>
            ) : (
              <button
                onClick={handleCreatePortfolio}
                disabled={isCreating}
                className="flex items-center gap-2 px-8 py-3 rounded-lg font-medium bg-success text-dark hover:bg-success/90 transition-colors"
              >
                {isCreating ? (
                  <>
                    <Loader2 className="w-5 h-5 animate-spin" />
                    Fetching live market data & building portfolio…
                  </>
                ) : (
                  <>
                    <Sparkles className="w-5 h-5" />
                    Create Portfolio
                  </>
                )}
              </button>
            )}
          </div>
        </motion.div>
        
        {/* Need Funds */}
        {walletBalance < 1000 && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="mt-6 p-4 bg-warning/10 rounded-lg flex items-center justify-between"
          >
            <div className="flex items-center gap-3">
              <AlertCircle className="w-5 h-5 text-warning" />
              <span className="text-warning">Insufficient funds to invest</span>
            </div>
            <Link to="/deposit-withdraw" className="btn-secondary">
              Add Funds
            </Link>
          </motion.div>
        )}
      </div>

    {/* ── AI Analysis Summary Modal ─────────────────────────────────────── */}
    {aiResult && (
      <div className="fixed inset-0 bg-black/80 z-50 flex items-center justify-center p-4 overflow-y-auto">
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          className="glass-card w-full max-w-2xl border border-primary/30 my-8"
        >
          {/* Header */}
          <div className="p-6 border-b border-gray-800">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-xl bg-primary/10 flex items-center justify-center">
                  <Brain className="w-5 h-5 text-primary" />
                </div>
                <div>
                  <h2 className="text-xl font-bold">Claude AI Analysis Complete</h2>
                  <p className="text-gray-400 text-sm">
                    Powered by Claude Sonnet · Real-time market data · Finnhub + NewsAPI
                  </p>
                </div>
              </div>
              <span className="text-xs px-3 py-1 rounded-full bg-emerald-500/20 text-emerald-400 font-medium">
                ✓ Live Analysis
              </span>
            </div>
          </div>

          {/* Market Context */}
          {aiResult.market_context && (
            <div className="p-6 border-b border-gray-800">
              <div className="flex items-start gap-3">
                <Newspaper className="w-4 h-4 text-primary flex-shrink-0 mt-1" />
                <div>
                  <div className="text-xs text-gray-500 uppercase tracking-wide mb-1">Today's Market Context</div>
                  <p className="text-gray-300 text-sm leading-relaxed">{aiResult.market_context}</p>
                </div>
              </div>
            </div>
          )}

          {/* AI Metrics */}
          <div className="grid grid-cols-3 gap-4 p-6 border-b border-gray-800">
            <div className="text-center">
              <div className="text-2xl font-bold text-primary">
                {aiResult.holdings?.filter(h => h.symbol !== 'CASH').length || 0}
              </div>
              <div className="text-xs text-gray-500 mt-1">Stocks Selected</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-emerald-400">
                +{((aiResult.expected_return || 0) * 100).toFixed(1)}%
              </div>
              <div className="text-xs text-gray-500 mt-1">Expected Annual</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-secondary">
                {(aiResult.sharpe_ratio || 0).toFixed(2)}
              </div>
              <div className="text-xs text-gray-500 mt-1">Sharpe Ratio</div>
            </div>
          </div>

          {/* Per-stock reasoning */}
          {aiResult.stock_reasoning && (
            <div className="p-6 border-b border-gray-800">
              <div className="flex items-center gap-2 mb-3">
                <BarChart3 className="w-4 h-4 text-secondary" />
                <div className="text-xs text-gray-500 uppercase tracking-wide">Why Claude Picked Each Stock</div>
              </div>
              <div className="space-y-2 max-h-48 overflow-y-auto pr-1">
                {aiResult.stock_reasoning.split('\n').filter(l => l.trim()).map((line, i) => {
                  const m = line.match(/^([A-Z0-9]+):\s*(.*)/)
                  return (
                    <div key={i} className="flex items-start gap-2 text-xs">
                      <span className="text-primary mt-0.5 flex-shrink-0">▸</span>
                      {m ? (
                        <span>
                          <span className="font-bold text-white">{m[1]}: </span>
                          <span className="text-gray-400">{m[2]}</span>
                        </span>
                      ) : (
                        <span className="text-gray-400">{line}</span>
                      )}
                    </div>
                  )
                })}
              </div>
            </div>
          )}

          {/* Holdings preview */}
          <div className="p-6 border-b border-gray-800">
            <div className="flex items-center gap-2 mb-3">
              <Zap className="w-4 h-4 text-accent" />
              <div className="text-xs text-gray-500 uppercase tracking-wide">Portfolio Allocation</div>
            </div>
            <div className="flex flex-wrap gap-2">
              {(aiResult.holdings || []).filter(h => h.symbol !== 'CASH').map(h => (
                <span key={h.symbol} className={`px-2 py-1 rounded-lg text-xs font-medium border ${
                  h.signal_strength === 'strong_buy' ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20' :
                  h.signal_strength === 'buy' ? 'bg-primary/10 text-primary border-primary/20' :
                  'bg-gray-700 text-gray-400 border-gray-600'
                }`}>
                  {h.symbol} {(h.weight * 100).toFixed(1)}%
                </span>
              ))}
            </div>
          </div>

          {/* CTA */}
          <div className="p-6 flex gap-3">
            <button
              onClick={() => navigate(`/portfolio/${aiResult.id}`)}
              className="flex-1 btn-primary py-3 flex items-center justify-center gap-2"
            >
              <CheckCircle className="w-5 h-5" />
              View Portfolio
            </button>
            <button
              onClick={() => { setAiResult(null); navigate('/dashboard') }}
              className="px-4 py-3 bg-dark-lighter rounded-xl text-gray-400 hover:text-white transition-colors"
            >
              Dashboard
            </button>
          </div>
        </motion.div>
      </div>
    )}
    </div>
  )
}
