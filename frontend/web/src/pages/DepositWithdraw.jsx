import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { 
  Wallet, 
  ArrowDownLeft, 
  ArrowUpRight, 
  History,
  AlertCircle,
  CheckCircle,
  Loader2,
  TrendingUp
} from 'lucide-react'
import { useAuthStore } from '../store/authStore'
import { walletApi, dashboardApi } from '../services/api'
import toast from 'react-hot-toast'

export default function DepositWithdraw() {
  const { user } = useAuthStore()
  const [activeTab, setActiveTab] = useState('deposit')
  const [amount, setAmount] = useState('')
  const [walletBalance, setWalletBalance] = useState({
    balance: 0,
    total_deposited: 0,
    total_withdrawn: 0,
    total_invested: 0,
    currency: 'USD'
  })
  const [isLoading, setIsLoading] = useState(false)
  const [isFetching, setIsFetching] = useState(true)
  const [transactions, setTransactions] = useState([])
  const [pagination, setPagination] = useState({ page: 1, page_size: 20, total: 0 })

  useEffect(() => {
    fetchWalletData()
  }, [])

  const fetchWalletData = async () => {
    try {
      setIsFetching(true)
      
      // Get wallet balance
      const walletRes = await walletApi.getBalance()
      if (walletRes.data) {
        setWalletBalance(walletRes.data)
      }

      // Get transactions
      const transRes = await walletApi.getTransactions(1, 20)
      if (transRes.data) {
        setTransactions(transRes.data.transactions || [])
        setPagination({
          page: transRes.data.page,
          page_size: transRes.data.page_size,
          total: transRes.data.total
        })
      }
    } catch (error) {
      console.error('Error fetching wallet data:', error)
      toast.error('Failed to load wallet data')
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

    if (depositAmount > 1000000) {
      toast.error('Maximum deposit is $1,000,000')
      return
    }

    setIsLoading(true)
    try {
      await walletApi.deposit(depositAmount, 'Deposit to investment wallet')
      
      toast.success(`Successfully deposited $${depositAmount.toLocaleString()}`)
      setAmount('')
      fetchWalletData()
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

    if (withdrawAmount > walletBalance.balance) {
      toast.error('Insufficient funds')
      return
    }

    setIsLoading(true)
    try {
      await walletApi.withdraw(withdrawAmount, 'Withdrawal from investment wallet')
      
      toast.success(`Successfully withdrew $${withdrawAmount.toLocaleString()}`)
      setAmount('')
      fetchWalletData()
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
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  const getTransactionIcon = (type) => {
    switch (type) {
      case 'deposit':
        return <ArrowDownLeft className="w-5 h-5" />
      case 'withdraw':
      case 'withdrawal':
        return <ArrowUpRight className="w-5 h-5" />
      case 'trade_buy':
        return <TrendingUp className="w-5 h-5" />
      case 'trade_sell':
        return <ArrowDownLeft className="w-5 h-5" />
      default:
        return <History className="w-5 h-5" />
    }
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
          <h1 className="text-3xl font-bold font-display mb-2">Wallet</h1>
          <p className="text-gray-400">Manage your simulated investment funds</p>
        </motion.div>

        {/* Balance Cards */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8"
        >
          {/* Available Balance */}
          <div className="glass-card p-6">
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 rounded-xl bg-primary/10 flex items-center justify-center">
                <Wallet className="w-6 h-6 text-primary" />
              </div>
              <div>
                <p className="text-gray-400 text-sm">Available Balance</p>
                <p className="text-2xl font-bold font-display">${walletBalance.balance.toLocaleString()}</p>
              </div>
            </div>
          </div>

          {/* Total Deposited */}
          <div className="glass-card p-6">
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 rounded-xl bg-success/10 flex items-center justify-center">
                <ArrowDownLeft className="w-6 h-6 text-success" />
              </div>
              <div>
                <p className="text-gray-400 text-sm">Total Deposited</p>
                <p className="text-2xl font-bold font-display text-success">${walletBalance.total_deposited.toLocaleString()}</p>
              </div>
            </div>
          </div>

          {/* Total Invested */}
          <div className="glass-card p-6">
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 rounded-xl bg-secondary/10 flex items-center justify-center">
                <TrendingUp className="w-6 h-6 text-secondary" />
              </div>
              <div>
                <p className="text-gray-400 text-sm">Total Invested</p>
                <p className="text-2xl font-bold font-display text-secondary">${walletBalance.total_invested.toLocaleString()}</p>
              </div>
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
                  max="1000000"
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
                  Withdrawals are limited to your available balance. This is a simulation with simulated money.
                </p>
              </div>
            )}

            {/* Submit Button */}
            <button
              onClick={handleSubmit}
              disabled={isLoading || !amount || (activeTab === 'withdraw' && parseFloat(amount) > walletBalance.balance)}
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
              <div className="space-y-3 max-h-96 overflow-y-auto">
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
                            : transaction.type === 'withdraw' || transaction.type === 'withdrawal'
                            ? 'bg-danger/20 text-danger'
                            : transaction.type === 'trade_buy'
                            ? 'bg-secondary/20 text-secondary'
                            : 'bg-primary/20 text-primary'
                        }`}
                      >
                        {getTransactionIcon(transaction.type)}
                      </div>
                      <div>
                        <p className="font-medium capitalize">{transaction.type.replace(/_/g, ' ')}</p>
                        <p className="text-sm text-gray-500">{formatDate(transaction.created_at)}</p>
                      </div>
                    </div>
                    <div className="text-right">
                      <p
                        className={`font-semibold ${
                          transaction.type === 'deposit' || transaction.type === 'trade_sell'
                            ? 'text-success'
                            : 'text-danger'
                        }`}
                      >
                        {transaction.type === 'deposit' || transaction.type === 'trade_sell' ? '+' : '-'}${transaction.amount.toLocaleString()}
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
