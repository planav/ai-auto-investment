import { useMemo } from 'react'
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts'

export default function PortfolioChart() {
  // Generate mock data
  const data = useMemo(() => {
    const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    let value = 100000
    
    return months.map((month) => {
      const change = (Math.random() - 0.3) * 5000
      value += change
      return {
        month,
        value: Math.round(value),
        benchmark: Math.round(value * 0.95),
      }
    })
  }, [])

  const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      return (
        <div className="glass-card p-3 border border-primary/30">
          <p className="text-gray-400 text-sm mb-1">{label}</p>
          <p className="text-primary font-bold">
            ${payload[0].value.toLocaleString()}
          </p>
          <p className="text-gray-500 text-xs">
            Benchmark: ${payload[1].value.toLocaleString()}
          </p>
        </div>
      )
    }
    return null
  }

  return (
    <div className="h-80">
      <ResponsiveContainer width="100%" height="100%">
        <AreaChart data={data} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
          <defs>
            <linearGradient id="colorValue" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#00D4AA" stopOpacity={0.3}/>
              <stop offset="95%" stopColor="#00D4AA" stopOpacity={0}/>
            </linearGradient>
            <linearGradient id="colorBenchmark" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#7B61FF" stopOpacity={0.3}/>
              <stop offset="95%" stopColor="#7B61FF" stopOpacity={0}/>
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="#1A1A2E" />
          <XAxis 
            dataKey="month" 
            stroke="#6B7280"
            tick={{ fill: '#6B7280', fontSize: 12 }}
            axisLine={{ stroke: '#374151' }}
          />
          <YAxis 
            stroke="#6B7280"
            tick={{ fill: '#6B7280', fontSize: 12 }}
            axisLine={{ stroke: '#374151' }}
            tickFormatter={(value) => `$${(value / 1000).toFixed(0)}k`}
          />
          <Tooltip content={<CustomTooltip />} />
          <Area
            type="monotone"
            dataKey="value"
            stroke="#00D4AA"
            strokeWidth={2}
            fillOpacity={1}
            fill="url(#colorValue)"
            name="Portfolio"
          />
          <Area
            type="monotone"
            dataKey="benchmark"
            stroke="#7B61FF"
            strokeWidth={2}
            fillOpacity={1}
            fill="url(#colorBenchmark)"
            name="Benchmark"
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  )
}
