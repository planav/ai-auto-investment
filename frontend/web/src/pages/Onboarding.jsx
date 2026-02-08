import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import { 
  Wallet, 
  Target, 
  Clock, 
  TrendingUp, 
  ArrowRight, 
  ArrowLeft,
  CheckCircle,
  Sparkles,
  Loader2
} from 'lucide-react'
import { useAuthStore } from '../store/authStore'
import { userApi, portfolioApi } from '../services/api'
import toast from 'react-hot-toast'

const steps = [
  { id: 'balance', title: 'Initial Investment', icon: Wallet },
  { id: 'goal', title: 'Investment Goal', icon: Target },
  { id: 'timeframe', title: 'Time Frame', icon: Clock },
  { id: 'risk', title: 'Risk Level', icon: TrendingUp },
]

const investmentGoals = [
  { id: 'short_term', label: 'Short Term', description: '1-3 years - Quick returns, capital preservation', years: 2 },
  { id: 'medium_term', label: 'Medium Term', description: '3-7 years - Balanced growth and stability', years: 5 },
  { id: 'long_term', label: 'Long Term', description: '7+ years - Maximum growth potential', years: 10 },
]

const riskLevels = [
  { id: 'conservative', label: 'Conservative', description: 'Lower risk, steady returns, capital preservation', color: 'text-success' },
  { id: 'moderate', label: 'Moderate', description: 'Balanced risk and return potential', color: 'text-primary' },
  { id: 'aggressive', label: 'Aggressive', description: 'Higher risk, higher potential returns', color: 'text-danger' },
]

export default function Onboarding() {
  const navigate = useNavigate()
  const { user, updateUser } = useAuthStore()
  const [currentStep, setCurrentStep] = useState(0)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [formData, setFormData] = useState({
    initial_balance: 10000,
    investment_goal: 'medium_term',
    time_frame: 5,
    risk_level: 'moderate',
  })

  const handleNext = () => {
    if (currentStep < steps.length - 1) {
      setCurrentStep(prev => prev + 1)
    } else {
      handleSubmit()
    }
  }

  const handleBack = () => {
    if (currentStep > 0) {
      setCurrentStep(prev => prev - 1)
    }
  }

  const handleSubmit = async () => {
    setIsSubmitting(true)
    try {
      // Update user preferences
      await userApi.updatePreferences({
        risk_tolerance: formData.risk_level,
        investment_horizon: formData.time_frame,
        initial_investment: formData.initial_balance,
        monthly_contribution: 0,
        preferred_assets: 'stocks,etfs',
      })

      // Create initial portfolio with AI analysis
      await portfolioApi.create({
        name: 'My First AI Portfolio',
        description: `AI-generated portfolio based on ${formData.risk_level} risk profile`,
        investment_amount: formData.initial_balance,
        cash_reserve_pct: 0.05,
        model_type: 'temporal_fusion_transformer',
      })

      // Update local user state
      updateUser({
        risk_tolerance: formData.risk_level,
        investment_horizon: formData.time_frame,
        initial_investment: formData.initial_balance,
      })

      toast.success('Portfolio created successfully!')
      navigate('/dashboard')
    } catch (error) {
      console.error('Onboarding error:', error)
      toast.error(error.response?.data?.detail || 'Failed to create portfolio')
    } finally {
      setIsSubmitting(false)
    }
  }

  const renderStepContent = () => {
    switch (currentStep) {
      case 0:
        return (
          <div className="space-y-6">
            <div className="text-center mb-8">
              <h2 className="text-2xl font-bold mb-2">Set Your Initial Investment</h2>
              <p className="text-gray-400">How much would you like to start with? (Fake money for simulation)</p>
            </div>
            
            <div className="space-y-4">
              <label className="block text-sm font-medium text-gray-300">
                Initial Balance: <span className="text-primary text-xl font-bold">${formData.initial_balance.toLocaleString()}</span>
              </label>
              <input
                type="range"
                min="1000"
                max="100000"
                step="1000"
                value={formData.initial_balance}
                onChange={(e) => setFormData({ ...formData, initial_balance: parseInt(e.target.value) })}
                className="w-full h-2 bg-dark-lighter rounded-lg appearance-none cursor-pointer accent-primary"
              />
              <div className="flex justify-between text-sm text-gray-500">
                <span>$1,000</span>
                <span>$100,000</span>
              </div>
              
              <div className="grid grid-cols-4 gap-2 mt-4">
                {[5000, 10000, 25000, 50000].map((amount) => (
                  <button
                    key={amount}
                    onClick={() => setFormData({ ...formData, initial_balance: amount })}
                    className={`py-2 px-3 rounded-lg text-sm transition-colors ${
                      formData.initial_balance === amount
                        ? 'bg-primary text-dark font-medium'
                        : 'bg-dark-lighter text-gray-400 hover:text-white'
                    }`}
                  >
                    ${amount.toLocaleString()}
                  </button>
                ))}
              </div>
            </div>
          </div>
        )

      case 1:
        return (
          <div className="space-y-6">
            <div className="text-center mb-8">
              <h2 className="text-2xl font-bold mb-2">What's Your Investment Goal?</h2>
              <p className="text-gray-400">This helps us tailor your portfolio strategy</p>
            </div>
            
            <div className="space-y-3">
              {investmentGoals.map((goal) => (
                <button
                  key={goal.id}
                  onClick={() => setFormData({ 
                    ...formData, 
                    investment_goal: goal.id,
                    time_frame: goal.years 
                  })}
                  className={`w-full p-4 rounded-xl border-2 transition-all text-left ${
                    formData.investment_goal === goal.id
                      ? 'border-primary bg-primary/10'
                      : 'border-gray-800 hover:border-gray-700'
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <div>
                      <h3 className="font-semibold">{goal.label}</h3>
                      <p className="text-sm text-gray-400">{goal.description}</p>
                    </div>
                    {formData.investment_goal === goal.id && (
                      <CheckCircle className="w-6 h-6 text-primary" />
                    )}
                  </div>
                </button>
              ))}
            </div>
          </div>
        )

      case 2:
        return (
          <div className="space-y-6">
            <div className="text-center mb-8">
              <h2 className="text-2xl font-bold mb-2">Investment Time Frame</h2>
              <p className="text-gray-400">How long do you plan to invest?</p>
            </div>
            
            <div className="space-y-4">
              <label className="block text-sm font-medium text-gray-300">
                Time Frame: <span className="text-primary text-xl font-bold">{formData.time_frame} years</span>
              </label>
              <input
                type="range"
                min="1"
                max="30"
                step="1"
                value={formData.time_frame}
                onChange={(e) => setFormData({ ...formData, time_frame: parseInt(e.target.value) })}
                className="w-full h-2 bg-dark-lighter rounded-lg appearance-none cursor-pointer accent-primary"
              />
              <div className="flex justify-between text-sm text-gray-500">
                <span>1 year</span>
                <span>30 years</span>
              </div>
              
              <div className="grid grid-cols-5 gap-2 mt-4">
                {[1, 3, 5, 10, 20].map((years) => (
                  <button
                    key={years}
                    onClick={() => setFormData({ ...formData, time_frame: years })}
                    className={`py-2 px-3 rounded-lg text-sm transition-colors ${
                      formData.time_frame === years
                        ? 'bg-primary text-dark font-medium'
                        : 'bg-dark-lighter text-gray-400 hover:text-white'
                    }`}
                  >
                    {years} {years === 1 ? 'yr' : 'yrs'}
                  </button>
                ))}
              </div>
            </div>
          </div>
        )

      case 3:
        return (
          <div className="space-y-6">
            <div className="text-center mb-8">
              <h2 className="text-2xl font-bold mb-2">Select Your Risk Level</h2>
              <p className="text-gray-400">How much risk are you comfortable with?</p>
            </div>
            
            <div className="space-y-3">
              {riskLevels.map((risk) => (
                <button
                  key={risk.id}
                  onClick={() => setFormData({ ...formData, risk_level: risk.id })}
                  className={`w-full p-4 rounded-xl border-2 transition-all text-left ${
                    formData.risk_level === risk.id
                      ? 'border-primary bg-primary/10'
                      : 'border-gray-800 hover:border-gray-700'
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <div>
                      <h3 className={`font-semibold ${risk.color}`}>{risk.label}</h3>
                      <p className="text-sm text-gray-400">{risk.description}</p>
                    </div>
                    {formData.risk_level === risk.id && (
                      <CheckCircle className="w-6 h-6 text-primary" />
                    )}
                  </div>
                </button>
              ))}
            </div>
          </div>
        )

      default:
        return null
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center px-4 pt-20 pb-12">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="w-full max-w-lg"
      >
        <div className="glass-card p-8">
          {/* Progress Header */}
          <div className="mb-8">
            <div className="flex items-center justify-between mb-4">
              {steps.map((step, index) => {
                const Icon = step.icon
                return (
                  <div key={step.id} className="flex flex-col items-center">
                    <div
                      className={`w-10 h-10 rounded-full flex items-center justify-center transition-colors ${
                        index <= currentStep
                          ? 'bg-primary text-dark'
                          : 'bg-dark-lighter text-gray-500'
                      }`}
                    >
                      <Icon className="w-5 h-5" />
                    </div>
                    <span className="text-xs mt-1 text-gray-500 hidden sm:block">{step.title}</span>
                  </div>
                )
              })}
            </div>
            <div className="h-1 bg-dark-lighter rounded-full overflow-hidden">
              <motion.div
                className="h-full bg-primary"
                initial={{ width: 0 }}
                animate={{ width: `${((currentStep + 1) / steps.length) * 100}%` }}
                transition={{ duration: 0.3 }}
              />
            </div>
          </div>

          {/* Step Content */}
          <AnimatePresence mode="wait">
            <motion.div
              key={currentStep}
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -20 }}
              transition={{ duration: 0.2 }}
            >
              {renderStepContent()}
            </motion.div>
          </AnimatePresence>

          {/* Navigation Buttons */}
          <div className="flex gap-4 mt-8">
            {currentStep > 0 && (
              <button
                onClick={handleBack}
                disabled={isSubmitting}
                className="flex-1 btn-secondary flex items-center justify-center gap-2"
              >
                <ArrowLeft className="w-5 h-5" />
                Back
              </button>
            )}
            <button
              onClick={handleNext}
              disabled={isSubmitting}
              className="flex-1 btn-primary flex items-center justify-center gap-2"
            >
              {isSubmitting ? (
                <>
                  <Loader2 className="w-5 h-5 animate-spin" />
                  Creating Portfolio...
                </>
              ) : currentStep === steps.length - 1 ? (
                <>
                  <Sparkles className="w-5 h-5" />
                  Create Portfolio
                </>
              ) : (
                <>
                  Next
                  <ArrowRight className="w-5 h-5" />
                </>
              )}
            </button>
          </div>

          {/* Summary on last step */}
          {currentStep === steps.length - 1 && (
            <div className="mt-6 p-4 bg-dark-lighter rounded-lg">
              <h4 className="font-semibold mb-2">Your Selection Summary</h4>
              <div className="space-y-1 text-sm text-gray-400">
                <p>Initial Investment: <span className="text-white">${formData.initial_balance.toLocaleString()}</span></p>
                <p>Goal: <span className="text-white">{investmentGoals.find(g => g.id === formData.investment_goal)?.label}</span></p>
                <p>Time Frame: <span className="text-white">{formData.time_frame} years</span></p>
                <p>Risk Level: <span className="text-white capitalize">{formData.risk_level}</span></p>
              </div>
            </div>
          )}
        </div>
      </motion.div>
    </div>
  )
}
