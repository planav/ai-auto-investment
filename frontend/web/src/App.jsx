import { Routes, Route } from 'react-router-dom'
import { Suspense, lazy } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import Navbar from './components/Navbar'
import Footer from './components/Footer'
import LoadingScreen from './components/LoadingScreen'
import ProtectedRoute from './components/ProtectedRoute'

// Lazy load pages for better performance
const Home = lazy(() => import('./pages/Home'))
const Dashboard = lazy(() => import('./pages/Dashboard'))
const Portfolio = lazy(() => import('./pages/Portfolio'))
const Analysis = lazy(() => import('./pages/Analysis'))
const Login = lazy(() => import('./pages/Login'))
const Register = lazy(() => import('./pages/Register'))
const Onboarding = lazy(() => import('./pages/Onboarding'))
const NotFound = lazy(() => import('./pages/NotFound'))
const Unauthorized = lazy(() => import('./pages/Unauthorized'))
const DepositWithdraw = lazy(() => import('./pages/DepositWithdraw'))

function App() {
  return (
    <div className="min-h-screen bg-dark text-white overflow-x-hidden">
      {/* Background Effects */}
      <div className="fixed inset-0 pointer-events-none">
        {/* Gradient mesh */}
        <div className="absolute inset-0 bg-mesh-gradient opacity-30" />
        
        {/* Grid pattern */}
        <div className="absolute inset-0 grid-bg opacity-50" />
        
        {/* Floating orbs */}
        <motion.div
          className="absolute w-96 h-96 rounded-full bg-primary/10 blur-3xl"
          animate={{
            x: [0, 100, 0],
            y: [0, -50, 0],
          }}
          transition={{
            duration: 20,
            repeat: Infinity,
            ease: "linear"
          }}
          style={{ top: '10%', left: '10%' }}
        />
        <motion.div
          className="absolute w-96 h-96 rounded-full bg-secondary/10 blur-3xl"
          animate={{
            x: [0, -100, 0],
            y: [0, 100, 0],
          }}
          transition={{
            duration: 25,
            repeat: Infinity,
            ease: "linear"
          }}
          style={{ top: '50%', right: '10%' }}
        />
        <motion.div
          className="absolute w-64 h-64 rounded-full bg-accent/10 blur-3xl"
          animate={{
            x: [0, 50, 0],
            y: [0, 50, 0],
          }}
          transition={{
            duration: 15,
            repeat: Infinity,
            ease: "linear"
          }}
          style={{ bottom: '10%', left: '30%' }}
        />
      </div>

      {/* Main Content */}
      <div className="relative z-10">
        <Navbar />
        
        <main className="min-h-screen">
          <Suspense fallback={<LoadingScreen />}>
            <AnimatePresence mode="wait">
              <Routes>
                <Route path="/" element={<Home />} />
                <Route path="/login" element={<Login />} />
                <Route path="/register" element={<Register />} />
                <Route path="/unauthorized" element={<Unauthorized />} />
                <Route 
                  path="/onboarding" 
                  element={
                    <ProtectedRoute>
                      <Onboarding />
                    </ProtectedRoute>
                  } 
                />
                <Route 
                  path="/dashboard" 
                  element={
                    <ProtectedRoute>
                      <Dashboard />
                    </ProtectedRoute>
                  } 
                />
                <Route 
                  path="/portfolio/:id?" 
                  element={
                    <ProtectedRoute>
                      <Portfolio />
                    </ProtectedRoute>
                  } 
                />
                <Route 
                  path="/analysis" 
                  element={
                    <ProtectedRoute>
                      <Analysis />
                    </ProtectedRoute>
                  } 
                />
                <Route 
                  path="/deposit-withdraw" 
                  element={
                    <ProtectedRoute>
                      <DepositWithdraw />
                    </ProtectedRoute>
                  } 
                />
                <Route path="*" element={<NotFound />} />
              </Routes>
            </AnimatePresence>
          </Suspense>
        </main>

        <Footer />
      </div>
    </div>
  )
}

export default App
