import { Link, useLocation } from 'react-router-dom'
import { motion } from 'framer-motion'
import { LogIn, ShieldAlert } from 'lucide-react'

export default function Unauthorized() {
  const location = useLocation()
  const from = location.state?.from?.pathname || '/dashboard'

  return (
    <div className="min-h-screen flex items-center justify-center px-4 pt-20">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="text-center max-w-md"
      >
        <div className="w-24 h-24 mx-auto mb-6 rounded-full bg-danger/10 flex items-center justify-center">
          <ShieldAlert className="w-12 h-12 text-danger" />
        </div>
        
        <h1 className="text-5xl font-bold font-display text-gradient mb-4">
          Access Denied
        </h1>
        
        <h2 className="text-2xl font-semibold mb-4">
          Authentication Required
        </h2>
        
        <p className="text-gray-400 mb-8">
          You need to be logged in to access this page. Please sign in to continue.
        </p>
        
        <Link 
          to="/login"
          state={{ from: location.state?.from }}
          className="btn-primary inline-flex items-center gap-2"
        >
          <LogIn className="w-5 h-5" />
          Sign In
        </Link>
        
        <p className="mt-6 text-sm text-gray-500">
          Don't have an account?{' '}
          <Link to="/register" className="text-primary hover:underline">
            Create one
          </Link>
        </p>
      </motion.div>
    </div>
  )
}
