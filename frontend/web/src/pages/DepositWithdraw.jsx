import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { 
  Wallet, 
  ArrowDownLeft, 
  ArrowUpRight, 
  History,
  AlertCircle,
  CheckCircle,
  Loader2
} from 'lucide-react'
import { useAuthStore } from '../store/authStore'
import { portfolioApi, userApi } from '../services/api'
import toast from 'react-hot-toast'

export default function DepositWithdraw() {
  const { user } = useAuthStore()
  const [activeTab, setActiveTab] = useState('deposit')
  const [amount, setAmount] = useState('')
  const [balance, setBalance] = useState(0)
  const [portfolios, setPortfolios] = useState([])
  const [selectedPortfolio, setSelectedPortfolio] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [isFetching, setIsFetching] = useState(true)
  const [transactions, setTransactions] = useState([])

  useEffect(() => {
    fetchUserData()
  }, [])

  const fetchUserData = async () => {
    try {
      setIsFetching(true)
      
      // Get user preferences for balance
      const userRes = await userApi.getPreferences()
      if (userRes.data) {
        setBalance(userRes.data.initial_investment || 0)
      }

      // Get portfolios
      const portfolioRes = await portfolioApi.getAll()
      if (portfolioRes.data && portfolioRes.data.length > 0) {
        setPortfolios(portfolioRes.data)
        setSelectedPortfolio(portfolioRes.data[0].id.toString())
      }

      // Mock transactions for now - in production this would come from API
      setTransactions([
        { id: 1, type: 'deposit', amount: 10000, date: new Date().toISOString(), status: 'completed' },
      ])
    } catch (error) {
      console.error('Error fetching user data:', error)
      toast.error('Failed to load account data')
    } finally {
      setIsFetching(false)
    }
  }

  const handleDeposit = async () => {
    const depositAmount = parseFloat(amount)
    if (!depositAmount || depositAmount <= 0) {
      toast.error('Please enter a valid amount')
      return
    }

    if (!selectedPortfolio) {
      toast.error('Please select a portfolio')
      return
    }

    setIsLoading(true)
    try {
      // Update user preferences with new balance
      const newBalance = balance + depositAmount
      await userApi.updatePreferences({
        initial_investment: newBalance,
      })

      // Update portfolio value
      const portfolio = portfolios.find(p => p.id.toString() === selectedPortfolio)
      if (portfolio) {
        await portfolioApi.update(selectedPortfolio, {
          total_value: (portfolio.total_value || 0) + depositAmount,
        })
      }

      setBalance(newBalance)
      setTransactions(prev => [
        { 
          id: Date.now(), 
          type: 'deposit', 
          amount: depositAmount, 
          date: new Date().toISOString(), 
          status: 'completed' 
        },
        ...prev
      ])

      toast.success(`Successfully deposited $${depositAmount.toLocaleString()}`)
      setAmount('')
      fetchUserData() // Refresh data
    } catch (error) {
      console.error('Deposit error:', error)
      toast.error('Failed to process deposit')
    } finally {
      setIsLoading(false)
    }
  }

  const handleWithdraw = async () => {
    const withdrawAmount = parseFloat(amount)
    if (!withdrawAmount || withdrawAmount <= 0) {
      toast.error('Please enter a valid amount')
      return
    }

    if (withdrawAmount > balance) {
      toast.error('Insufficient funds')
      return
    }

    if (!selectedPortfolio) {
      toast.error('Please select a portfolio')
      return
    }

    setIsLoading(true)
    try {
      // Update user preferences with new balance
      const newBalance = balance - withdrawAmount
      await userApi.updatePreferences({
        initial_investment: newBalance,
      })

      // Update portfolio value
      const portfolio = portfolios.find(p => p.id.toString() === selectedPortfolio)
      if (portfolio) {
        await portfolioApi.update(selectedPortfolio, {
          total_value: Math.max(0, (portfolio.total_value || 0) - withdrawAmount),
        })
      }

      setBalance(newBalance)
      setTransactions(prev => [
        { 
          id: Date.now(), 
          type: 'withdrawal', 
          amount: withdrawAmount, 
          date: new Date().toISOString(), 
          status: 'completed' 
        },
        ...prev
      ])

      toast.success(`Successfully withdrew $${withdrawAmount.toLocaleString()}`)
      setAmount('')
      fetchUserData() // Refresh data
    } catch (error) {
      console.error('Withdrawal error:', error)
      toast.error('Failed to process withdrawal')
    } finally {
      setIsLoading(false)
    }
  }

  const handleSubmit = () => {
    if (activeTab === 'deposit') {
      handleDeposit()
    } else {
      handleWithdraw()
    }
  }

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
    })
  }

  if (isFetching) {
    return (
      <div className="min-h-screen flex items-center justify-center pt-20">
        <div className="flex items-center gap-2">
          <Loader2 className="w-6 h-6 text-primary animate-spin" />
          <span className="text-gray-400">Loading...</span>
        </div>
      </div>
    )
  }

  return (
    <div className="pt-24 pb-12 px-4">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8"
        >
          <h1 className="text-3xl font-bold font-display mb-2">Deposit & Withdraw</h1>
          <p className="text-gray-400">Manage your fake investment funds</p>
        </motion.div>

        {/* Balance Card */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="glass-card p-6 mb-8"
        >
          <div className="flex items-center gap-4">
            <div className="w-14 h-14 rounded-xl bg-primary/10 flex items-center justify-center">
              <Wallet className="w-7 h-7 text-primary" />
            </div>
            <div>
              <p className="text-gray-400 text-sm">Available Balance</p>
              <p className="text-3xl font-bold font-display">${balance.toLocaleString()}</p>
            </div>
          </div>
        </motion.div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Transaction Form */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="glass-card p-6"
          >
            {/* Tabs */}
            <div className="flex gap-2 mb-6">
              <button
                onClick={() => setActiveTab('deposit')}
                className={`flex-1 py-3 px-4 rounded-lg font-medium transition-colors flex items-center justify-center gap-2 ${
                  activeTab === 'deposit'
                    ? 'bg-success text-dark'
                    : 'bg-dark-lighter text-gray-400 hover:text-white'
                }`}
              >
                <ArrowDownLeft className="w-5 h-5" />
                Deposit
              </button>
              <button
                onClick={() => setActiveTab('withdraw')}
                className={`flex-1 py-3 px-4 rounded-lg font-medium transition-colors flex items-center justify-center gap-2 ${
                  activeTab === 'withdraw'
                    ? 'bg-danger text-white'
                    : 'bg-dark-lighter text-gray-400 hover:text-white'
                }`}
              >
                <ArrowUpRight className="w-5 h-5" />
                Withdraw
              </button>
            </div>

            {/* Portfolio Selection */}
            {portfolios.length > 0 && (
              <div className="mb-6">
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Select Portfolio
                </label>
                <select
                  value={selectedPortfolio}
                  onChange={(e) => setSelectedPortfolio(e.target.value)}
                  className="w-full px-4 py-3 bg-dark-lighter border border-gray-700 rounded-lg focus:outline-none focus:border-primary transition-colors"
                >
                  {portfolios.map((portfolio) => (
                    <option key={portfolio.id} value={portfolio.id}>
                      {portfolio.name} - ${(portfolio.total_value || 0).toLocaleString()}
                    </option>
                  ))}
                </select>
              </div>
            )}

            {/* Amount Input */}
            <div className="mb-6">
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Amount (USD)
              </label>
              <div className="relative">
                <span className="absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-500">$</span>
                <input
                  type="number"
                  value={amount}
                  onChange={(e) => setAmount(e.target.value)}
                  placeholder="0.00"
                  min="0"
                  step="0.01"
                  className="w-full pl-8 pr-4 py-3 bg-dark-lighter border border-gray-700 rounded-lg focus:outline-none focus:border-primary transition-colors"
                />
              </div>
            </div>

            {/* Quick Amounts */}
            <div className="grid grid-cols-4 gap-2 mb-6">
              {[100, 500, 1000, 5000].map((quickAmount) => (
                <button
                  key={quickAmount}
                  onClick={() => setAmount(quickAmount.toString())}
                  className="py-2 px-3 bg-dark-lighter rounded-lg text-sm text-gray-400 hover:text-white hover:bg-gray-800 transition-colors"
                >
                  ${quickAmount.toLocaleString()}
                </button>
              ))}
            </div>

            {/* Warning for withdrawal */}
            {activeTab === 'withdraw' && (
              <div className="flex items-start gap-3 p-4 bg-danger/10 rounded-lg mb-6">
                <AlertCircle className="w-5 h-5 text-danger flex-shrink-0 mt-0.5" />
                <p className="text-sm text-gray-300">
                  Withdrawals are limited to your available balance. This is a simulation with fake money.
                </p>
              </div>
            )}

            {/* Submit Button */}
            <button
              onClick={handleSubmit}
              disabled={isLoading || !amount}
              className={`w-full py-3 rounded-lg font-medium transition-colors flex items-center justify-center gap-2 disabled:opacity-50 ${
                activeTab === 'deposit'
                  ? 'bg-success text-dark hover:bg-success/90'
                  : 'bg-danger text-white hover:bg-danger/90'
              }`}
            >
              {isLoading ? (
                <>
                  <Loader2 className="w-5 h-5 animate-spin" />
                  Processing...
                </>
              ) : activeTab === 'deposit' ? (
                <>
                  <ArrowDownLeft className="w-5 h-5" />
                  Deposit Funds
                </>
              ) : (
                <>
                  <ArrowUpRight className="w-5 h-5" />
                  Withdraw Funds
                </>
              )}
            </button>
          </motion.div>

          {/* Transaction History */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
            className="glass-card p-6"
          >
            <div className="flex items-center gap-2 mb-6">
              <History className="w-5 h-5 text-primary" />
              <h2 className="text-xl font-semibold">Transaction History</h2>
            </div>

            {transactions.length === 0 ? (
              <div className="text-center py-8 text-gray-500">
                <History className="w-12 h-12 mx-auto mb-3 opacity-50" />
                <p>No transactions yet</p>
              </div>
            ) : (
              <div className="space-y-3">
                {transactions.map((transaction) => (
                  <div
                    key={transaction.id}
                    className="flex items-center justify-between p-4 bg-dark-lighter rounded-lg"
                  >
                    <div className="flex items-center gap-3">
                      <div
                        className={`w-10 h-10 rounded-full flex items-center justify-center ${
                          transaction.type === 'deposit'
                            ? 'bg-success/20 text-success'
                            : 'bg-danger/20 text-danger'
                        }`}
                      >
                        {transaction.type === 'deposit' ? (
                          <ArrowDownLeft className="w-5 h-5" />
                        ) : (
                          <ArrowUpRight className="w-5 h-5" />
                        )}
                      </div>
                      <div>
                        <p className="font-medium capitalize">{transaction.type}</p>
                        <p className="text-sm text-gray-500">{formatDate(transaction.date)}</p>
                      </div>
                    </div>
                    <div className="text-right">
                      <p
                        className={`font-semibold ${
                          transaction.type === 'deposit' ? 'text-success' : 'text-danger'
                        }`}
                      >
                        {transaction.type === 'deposit' ? '+' : '-'}${transaction.amount.toLocaleString()}
                      </p>
                      <div className="flex items-center gap-1 text-sm text-success">
                        <CheckCircle className="w-3 h-3" />
                        <span className="capitalize">{transaction.status}</span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </motion.div>
        </div>
      </div>
    </div>
  )
}
