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
  Brain
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
  const { isAuthenticated, user } = useAuthStore()
  const navigate = useNavigate()
  
  const [step, setStep] = useState(1)
  const [isLoading, setIsLoading] = useState(false)
  const [isCreating, setIsCreating] = useState(false)
  
  // Form state
  const [walletBalance, setWalletBalance] = useState(0)
  const [amount, setAmount] = useState(10000)
  const [riskProfile, setRiskProfile] = useState('moderate')
  const [portfolioName, setPortfolioName] = useState('')
  
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
        cash_reserve_pct: 0.05,
        model_type: 'temporal_fusion_transformer',
      })
      
      if (res.data) {
        toast.success('Portfolio created successfully!')
        navigate(`/portfolio/${res.data.id}`)
      }
    } catch (error) {
      console.error('Error creating portfolio:', error)
      toast.error('Failed to create portfolio. Please try again.')
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
                    Creating Portfolio...
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
    </div>
  )
}
