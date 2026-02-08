import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { Link } from 'react-router-dom'
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
  Loader2
} from 'lucide-react'
import { systemApi } from '../services/api'

export default function Home() {
  const [stats, setStats] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    fetchSystemStats()
  }, [])

  const fetchSystemStats = async () => {
    try {
      setLoading(true)
      const response = await systemApi.getStats()
      setStats(response.data)
    } catch (err) {
      console.error('Failed to fetch system stats:', err)
      setError('Failed to load stats')
      // Set default empty stats
      setStats({
        assets_analyzed: 0,
        avg_annual_return: null,
        prediction_accuracy: null,
        analysis_time_ms: null,
        model_status: {}
      })
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

  // Models with dynamic training status
  const getModels = () => [
    { 
      name: 'Temporal Fusion Transformer', 
      id: 'temporal_fusion_transformer',
      type: 'Time Series',
      status: stats?.model_status?.temporal_fusion_transformer || 'not_trained'
    },
    { 
      name: 'Graph Attention Network', 
      id: 'graph_attention_network',
      type: 'Relationships',
      status: stats?.model_status?.graph_attention_network || 'not_trained'
    },
    { 
      name: 'LSTM + Attention', 
      id: 'lstm_attention',
      type: 'Sequential',
      status: stats?.model_status?.lstm_attention || 'not_trained'
    },
    { 
      name: 'PatchTST', 
      id: 'patch_tst',
      type: 'Long Sequence',
      status: stats?.model_status?.patch_tst || 'not_trained'
    },
  ]

  // Format stats for display
  const getStatDisplay = (value, suffix = '', defaultText = 'Not enough data') => {
    if (loading) return <Loader2 className="w-6 h-6 animate-spin mx-auto" />
    if (value === null || value === undefined) return defaultText
    return `${value}${suffix}`
  }

  const models = getModels()

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
            <Link to="/register" className="btn-primary text-lg px-8 py-4">
              Start Investing
              <ArrowRight className="inline-block ml-2 w-5 h-5" />
            </Link>
            <Link to="/" className="btn-secondary text-lg px-8 py-4">
              View Demo
            </Link>
          </motion.div>

          {/* Stats */}
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 }}
            className="mt-20 grid grid-cols-2 md:grid-cols-4 gap-8"
          >
            {[
              { 
                value: getStatDisplay(stats?.prediction_accuracy, '%'), 
                label: 'Prediction Accuracy' 
              },
              { 
                value: getStatDisplay(stats?.assets_analyzed > 0 ? `${stats.assets_analyzed}+` : '0'), 
                label: 'Assets Analyzed' 
              },
              { 
                value: getStatDisplay(stats?.avg_annual_return, '%'), 
                label: 'Avg. Annual Return' 
              },
              { 
                value: getStatDisplay(stats?.analysis_time_ms ? `<${(stats.analysis_time_ms / 1000).toFixed(1)}s` : null), 
                label: 'Analysis Time' 
              },
            ].map((stat, index) => (
              <div key={index} className="text-center">
                <div className="text-3xl md:text-4xl font-bold text-gradient font-display min-h-[48px] flex items-center justify-center">
                  {stat.value}
                </div>
                <div className="text-gray-400 text-sm mt-1">{stat.label}</div>
              </div>
            ))}
          </motion.div>
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

      {/* Models Section */}
      <section className="py-24 px-4 bg-dark-lighter/30">
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
                {models.map((model, index) => (
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
                    <div className="text-right">
                      <div className={`font-bold font-display ${
                        model.status === 'trained' ? 'text-primary' : 'text-gray-500'
                      }`}>
                        {model.status === 'trained' ? 'Trained' : 'Not trained yet'}
                      </div>
                      <div className="text-xs text-gray-500">
                        {model.status === 'trained' ? 'Ready for predictions' : 'Training required'}
                      </div>
                    </div>
                  </motion.div>
                ))}
              </div>
            </div>

            <div className="relative">
              <div className="glass-card p-8 holographic">
                <div className="flex items-center justify-between mb-6">
                  <div className="flex items-center gap-3">
                    <div className="w-3 h-3 rounded-full bg-primary animate-pulse" />
                    <span className="text-sm text-gray-400 font-mono">AI MODEL ACTIVE</span>
                  </div>
                  <Zap className="w-5 h-5 text-accent" />
                </div>
                
                {/* Mock prediction visualization */}
                <div className="space-y-4">
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-400">Model</span>
                    <span className="text-primary font-mono">Temporal Fusion Transformer</span>
                  </div>
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-400">Prediction Horizon</span>
                    <span className="font-mono">5 Days</span>
                  </div>
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-400">Confidence</span>
                    <span className="text-accent font-mono">
                      {stats?.prediction_accuracy ? `${stats.prediction_accuracy.toFixed(1)}%` : 'Calculating...'}
                    </span>
                  </div>
                  
                  {/* Mock chart */}
                  <div className="mt-6 h-32 flex items-end gap-1">
                    {[40, 65, 45, 80, 55, 90, 70, 85, 60, 95, 75, 88].map((h, i) => (
                      <motion.div
                        key={i}
                        initial={{ height: 0 }}
                        whileInView={{ height: `${h}%` }}
                        transition={{ delay: i * 0.05 }}
                        viewport={{ once: true }}
                        className="flex-1 bg-gradient-to-t from-primary/50 to-primary rounded-t"
                      />
                    ))}
                  </div>
                </div>
              </div>
            </div>
          </div>
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
