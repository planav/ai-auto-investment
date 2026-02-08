import { 
  TrendingUp, 
  TrendingDown, 
  Plus, 
  RefreshCw,
  Brain,
  AlertCircle
} from 'lucide-react'

const activities = [
  {
    id: 1,
    type: 'buy',
    asset: 'AAPL',
    amount: '$5,000',
    date: '2 hours ago',
    icon: Plus,
    color: 'success',
  },
  {
    id: 2,
    type: 'ai_prediction',
    description: 'TFT model predicted 12% upside for NVDA',
    date: '5 hours ago',
    icon: Brain,
    color: 'primary',
  },
  {
    id: 3,
    type: 'rebalance',
    description: 'Portfolio rebalanced automatically',
    date: '1 day ago',
    icon: RefreshCw,
    color: 'secondary',
  },
  {
    id: 4,
    type: 'alert',
    description: 'High volatility detected in tech sector',
    date: '2 days ago',
    icon: AlertCircle,
    color: 'warning',
  },
  {
    id: 5,
    type: 'sell',
    asset: 'TSLA',
    amount: '$3,200',
    date: '3 days ago',
    icon: TrendingDown,
    color: 'danger',
  },
]

export default function RecentActivity() {
  return (
    <div className="space-y-4">
      {activities.map((activity) => (
        <div
          key={activity.id}
          className="flex items-start gap-4 p-3 rounded-lg hover:bg-dark-lighter transition-colors"
        >
          <div className={`w-10 h-10 rounded-lg bg-${activity.color}/10 flex items-center justify-center flex-shrink-0`}>
            <activity.icon className={`w-5 h-5 text-${activity.color}`} />
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-sm font-medium">
              {activity.type === 'buy' && `Bought ${activity.asset}`}
              {activity.type === 'sell' && `Sold ${activity.asset}`}
              {activity.description}
            </p>
            {activity.amount && (
              <p className="text-sm text-gray-400">{activity.amount}</p>
            )}
            <p className="text-xs text-gray-500 mt-1">{activity.date}</p>
          </div>
        </div>
      ))}
    </div>
  )
}
