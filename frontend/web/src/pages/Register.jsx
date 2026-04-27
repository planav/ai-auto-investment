import { useState, useRef } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import {
  Eye, EyeOff, Mail, Lock, User, ArrowRight,
  CheckCircle, XCircle, Shield, RefreshCw, Loader2
} from 'lucide-react'
import { useAuthStore } from '../store/authStore'
import { authApi } from '../services/api'
import toast from 'react-hot-toast'

// ---------------------------------------------------------------------------
// Password strength helpers
// ---------------------------------------------------------------------------

const RULES = [
  { id: 'length',   label: 'At least 8 characters',         test: (p) => p.length >= 8 },
  { id: 'upper',    label: 'At least one capital letter',    test: (p) => /[A-Z]/.test(p) },
  { id: 'special',  label: 'At least one special character', test: (p) => /[!@#$%^&*()_+\-=\[\]{};:'",.<>?/\\|`~]/.test(p) },
]

function strengthLevel(password) {
  const passed = RULES.filter((r) => r.test(password)).length
  if (passed === 0) return { score: 0, label: '', color: '' }
  if (passed === 1) return { score: 1, label: 'Weak',   color: 'bg-red-500' }
  if (passed === 2) return { score: 2, label: 'Fair',   color: 'bg-yellow-500' }
  return               { score: 3, label: 'Strong', color: 'bg-emerald-500' }
}

// ---------------------------------------------------------------------------
// OTP digit input component
// ---------------------------------------------------------------------------

function OtpInput({ value, onChange }) {
  const refs = Array.from({ length: 6 }, () => useRef(null))

  const handleKey = (i, e) => {
    if (e.key === 'Backspace' && !e.target.value && i > 0) {
      refs[i - 1].current?.focus()
    }
  }

  const handleChange = (i, e) => {
    const digit = e.target.value.replace(/\D/g, '').slice(-1)
    const arr = value.split('')
    arr[i] = digit
    const next = arr.join('')
    onChange(next)
    if (digit && i < 5) refs[i + 1].current?.focus()
  }

  const handlePaste = (e) => {
    const pasted = e.clipboardData.getData('text').replace(/\D/g, '').slice(0, 6)
    onChange(pasted.padEnd(6, '').slice(0, 6))
    if (pasted.length > 0) refs[Math.min(pasted.length, 5)].current?.focus()
    e.preventDefault()
  }

  return (
    <div className="flex gap-3 justify-center">
      {Array.from({ length: 6 }).map((_, i) => (
        <input
          key={i}
          ref={refs[i]}
          type="text"
          inputMode="numeric"
          maxLength={1}
          value={value[i] || ''}
          onChange={(e) => handleChange(i, e)}
          onKeyDown={(e) => handleKey(i, e)}
          onPaste={handlePaste}
          className="w-12 h-14 text-center text-2xl font-bold bg-dark-lighter border-2 border-gray-700
                     rounded-xl focus:outline-none focus:border-primary transition-colors text-white
                     caret-primary"
        />
      ))}
    </div>
  )
}

// ---------------------------------------------------------------------------
// Main Register page
// ---------------------------------------------------------------------------

export default function Register() {
  const [step, setStep]           = useState('form')    // 'form' | 'otp'
  const [isLoading, setIsLoading] = useState(false)
  const [showPassword, setShowPassword] = useState(false)
  const [otp, setOtp]             = useState('')
  const [otpEmail, setOtpEmail]   = useState('')
  const [devOtp, setDevOtp]       = useState(null)    // shown only in dev mode
  const [resendCooldown, setResendCooldown] = useState(0)

  const [formData, setFormData] = useState({
    full_name:           '',
    email:               '',
    password:            '',
    confirmPassword:     '',
    risk_tolerance:      'moderate',
    investment_horizon:  5,
  })

  const navigate  = useNavigate()
  const loginStore = useAuthStore((state) => state.login)
  const strength   = strengthLevel(formData.password)

  // ── Step 1: Submit registration form ──────────────────────────────────────

  const handleRegister = async (e) => {
    e.preventDefault()

    if (formData.password !== formData.confirmPassword) {
      toast.error('Passwords do not match.')
      return
    }

    const failing = RULES.find((r) => !r.test(formData.password))
    if (failing) {
      toast.error(failing.label)
      return
    }

    setIsLoading(true)
    try {
      const res = await authApi.register({
        email:               formData.email,
        password:            formData.password,
        full_name:           formData.full_name,
        risk_tolerance:      formData.risk_tolerance,
        investment_horizon:  formData.investment_horizon,
      })

      setOtpEmail(formData.email)
      setDevOtp(res.data.dev_otp || null)   // populated only when SMTP not configured
      setStep('otp')
      startResendCooldown()
      toast.success(res.data.message)
    } catch (err) {
      const msg =
        err.response?.data?.detail ||
        (Array.isArray(err.response?.data?.detail)
          ? err.response.data.detail.map((d) => d.msg).join(' ')
          : null) ||
        'Registration failed. Please try again.'
      toast.error(msg)
    } finally {
      setIsLoading(false)
    }
  }

  // ── Step 2: Verify OTP ────────────────────────────────────────────────────

  const handleVerifyOtp = async () => {
    if (otp.length < 6) {
      toast.error('Please enter the complete 6-digit code.')
      return
    }
    setIsLoading(true)
    try {
      const res = await authApi.verifyOtp(otpEmail, otp)
      const { access_token, refresh_token } = res.data

      // Fetch user profile then auto-login
      const { default: axios } = await import('axios')
      const base = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1'
      const me = await axios.get(`${base}/auth/me`, {
        headers: { Authorization: `Bearer ${access_token}` },
      })

      loginStore(me.data, access_token, refresh_token)
      toast.success('Email verified! Welcome to AutoInvest.')
      navigate('/onboarding')
    } catch (err) {
      const msg = err.response?.data?.detail || 'Invalid OTP. Please try again.'
      toast.error(msg)
      setOtp('')
    } finally {
      setIsLoading(false)
    }
  }

  // ── Resend OTP ─────────────────────────────────────────────────────────────

  const startResendCooldown = () => {
    setResendCooldown(60)
    const t = setInterval(() => {
      setResendCooldown((prev) => {
        if (prev <= 1) { clearInterval(t); return 0 }
        return prev - 1
      })
    }, 1000)
  }

  const handleResend = async () => {
    if (resendCooldown > 0) return
    setIsLoading(true)
    try {
      const res = await authApi.resendOtp(otpEmail)
      setDevOtp(res.data.dev_otp || null)
      setOtp('')
      startResendCooldown()
      toast.success('New OTP sent.')
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to resend OTP.')
    } finally {
      setIsLoading(false)
    }
  }

  // ─────────────────────────────────────────────────────────────────────────

  return (
    <div className="min-h-screen flex items-center justify-center px-4 pt-20 pb-10">
      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="w-full max-w-md">
        <div className="glass-card p-8">

          <AnimatePresence mode="wait">

            {/* ── STEP 1: Registration Form ─────────────────────────────── */}
            {step === 'form' && (
              <motion.div key="form" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>

                <div className="text-center mb-8">
                  <h1 className="text-3xl font-bold font-display text-gradient mb-2">Create Account</h1>
                  <p className="text-gray-400">Start your AI-powered investment journey</p>
                </div>

                <form onSubmit={handleRegister} className="space-y-5">

                  {/* Full Name */}
                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-1.5">Full Name</label>
                    <div className="relative">
                      <User className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-500" />
                      <input
                        type="text"
                        value={formData.full_name}
                        onChange={(e) => setFormData({ ...formData, full_name: e.target.value })}
                        className="w-full pl-10 pr-4 py-3 bg-dark-lighter border border-gray-700 rounded-lg focus:outline-none focus:border-primary transition-colors"
                        placeholder="John Doe"
                        required
                      />
                    </div>
                  </div>

                  {/* Email */}
                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-1.5">Email Address</label>
                    <div className="relative">
                      <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-500" />
                      <input
                        type="email"
                        value={formData.email}
                        onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                        className="w-full pl-10 pr-4 py-3 bg-dark-lighter border border-gray-700 rounded-lg focus:outline-none focus:border-primary transition-colors"
                        placeholder="you@company.com"
                        required
                      />
                    </div>
                  </div>

                  {/* Password */}
                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-1.5">Password</label>
                    <div className="relative">
                      <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-500" />
                      <input
                        type={showPassword ? 'text' : 'password'}
                        value={formData.password}
                        onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                        className="w-full pl-10 pr-12 py-3 bg-dark-lighter border border-gray-700 rounded-lg focus:outline-none focus:border-primary transition-colors"
                        placeholder="••••••••"
                        required
                      />
                      <button
                        type="button"
                        onClick={() => setShowPassword(!showPassword)}
                        className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-500 hover:text-gray-300"
                      >
                        {showPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                      </button>
                    </div>

                    {/* Strength bar */}
                    {formData.password && (
                      <div className="mt-2 space-y-1.5">
                        <div className="flex gap-1">
                          {[1, 2, 3].map((lvl) => (
                            <div
                              key={lvl}
                              className={`h-1 flex-1 rounded-full transition-all ${
                                strength.score >= lvl ? strength.color : 'bg-gray-700'
                              }`}
                            />
                          ))}
                          <span className="text-xs text-gray-400 ml-1 min-w-[40px]">{strength.label}</span>
                        </div>
                        {/* Rule checklist */}
                        <div className="space-y-0.5">
                          {RULES.map((r) => {
                            const ok = r.test(formData.password)
                            return (
                              <div key={r.id} className="flex items-center gap-1.5 text-xs">
                                {ok
                                  ? <CheckCircle className="w-3.5 h-3.5 text-emerald-400 flex-shrink-0" />
                                  : <XCircle    className="w-3.5 h-3.5 text-gray-600     flex-shrink-0" />}
                                <span className={ok ? 'text-emerald-400' : 'text-gray-500'}>{r.label}</span>
                              </div>
                            )
                          })}
                        </div>
                      </div>
                    )}
                  </div>

                  {/* Confirm Password */}
                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-1.5">Confirm Password</label>
                    <input
                      type="password"
                      value={formData.confirmPassword}
                      onChange={(e) => setFormData({ ...formData, confirmPassword: e.target.value })}
                      className={`w-full px-4 py-3 bg-dark-lighter border rounded-lg focus:outline-none transition-colors ${
                        formData.confirmPassword && formData.confirmPassword !== formData.password
                          ? 'border-red-500 focus:border-red-500'
                          : 'border-gray-700 focus:border-primary'
                      }`}
                      placeholder="••••••••"
                      required
                    />
                    {formData.confirmPassword && formData.confirmPassword !== formData.password && (
                      <p className="text-xs text-red-400 mt-1">Passwords do not match.</p>
                    )}
                  </div>

                  {/* Risk Tolerance */}
                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-1.5">Risk Tolerance</label>
                    <select
                      value={formData.risk_tolerance}
                      onChange={(e) => setFormData({ ...formData, risk_tolerance: e.target.value })}
                      className="w-full px-4 py-3 bg-dark-lighter border border-gray-700 rounded-lg focus:outline-none focus:border-primary transition-colors"
                    >
                      <option value="conservative">Conservative</option>
                      <option value="moderate">Moderate</option>
                      <option value="aggressive">Aggressive</option>
                    </select>
                  </div>

                  {/* Investment Horizon */}
                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-1.5">Investment Horizon (years)</label>
                    <input
                      type="number"
                      min="1"
                      max="30"
                      value={formData.investment_horizon}
                      onChange={(e) => setFormData({ ...formData, investment_horizon: parseInt(e.target.value) })}
                      className="w-full px-4 py-3 bg-dark-lighter border border-gray-700 rounded-lg focus:outline-none focus:border-primary transition-colors"
                    />
                  </div>

                  <button
                    type="submit"
                    disabled={isLoading || strength.score < 3 || formData.password !== formData.confirmPassword}
                    className="w-full btn-primary py-3 flex items-center justify-center gap-2 disabled:opacity-50"
                  >
                    {isLoading
                      ? <Loader2 className="w-5 h-5 animate-spin" />
                      : <><span>Create Account</span><ArrowRight className="w-5 h-5" /></>}
                  </button>
                </form>

                <div className="flex items-center gap-4 my-6">
                  <div className="flex-1 h-px bg-gray-800" />
                  <span className="text-gray-500 text-sm">or</span>
                  <div className="flex-1 h-px bg-gray-800" />
                </div>
                <p className="text-center text-gray-400">
                  Already have an account?{' '}
                  <Link to="/login" className="text-primary hover:text-primary-light transition-colors">Sign in</Link>
                </p>
              </motion.div>
            )}

            {/* ── STEP 2: OTP Verification ──────────────────────────────── */}
            {step === 'otp' && (
              <motion.div key="otp" initial={{ opacity: 0, x: 30 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0 }}>

                <div className="text-center mb-8">
                  <div className="w-16 h-16 rounded-full bg-primary/10 flex items-center justify-center mx-auto mb-4">
                    <Shield className="w-8 h-8 text-primary" />
                  </div>
                  <h1 className="text-2xl font-bold font-display mb-2">Verify Your Email</h1>
                  <p className="text-gray-400 text-sm">
                    We sent a 6-digit code to <span className="text-primary font-medium">{otpEmail}</span>
                  </p>
                </div>

                {/* Dev-mode OTP banner */}
                {devOtp && (
                  <div className="mb-6 p-3 bg-yellow-500/10 border border-yellow-500/30 rounded-xl text-center">
                    <p className="text-yellow-400 text-xs font-medium mb-1">Dev Mode — No SMTP configured</p>
                    <p className="text-yellow-300 text-2xl font-mono font-bold tracking-widest">{devOtp}</p>
                    <p className="text-yellow-500 text-xs mt-1">Configure SMTP in .env to send real emails</p>
                  </div>
                )}

                {/* OTP digit boxes */}
                <div className="mb-6">
                  <OtpInput value={otp} onChange={setOtp} />
                </div>

                {/* Verify button */}
                <button
                  onClick={handleVerifyOtp}
                  disabled={isLoading || otp.length < 6}
                  className="w-full btn-primary py-3 flex items-center justify-center gap-2 disabled:opacity-50 mb-4"
                >
                  {isLoading
                    ? <Loader2 className="w-5 h-5 animate-spin" />
                    : <><CheckCircle className="w-5 h-5" /><span>Verify Email</span></>}
                </button>

                {/* Resend */}
                <div className="text-center">
                  {resendCooldown > 0 ? (
                    <p className="text-gray-500 text-sm">
                      Resend available in <span className="text-gray-300">{resendCooldown}s</span>
                    </p>
                  ) : (
                    <button
                      onClick={handleResend}
                      disabled={isLoading}
                      className="text-primary hover:text-primary-light text-sm flex items-center gap-1.5 mx-auto transition-colors"
                    >
                      <RefreshCw className="w-4 h-4" />
                      Resend OTP
                    </button>
                  )}
                </div>

                {/* Back link */}
                <button
                  onClick={() => { setStep('form'); setOtp(''); setDevOtp(null) }}
                  className="mt-4 text-gray-500 hover:text-gray-300 text-sm text-center w-full transition-colors"
                >
                  ← Back to registration
                </button>
              </motion.div>
            )}

          </AnimatePresence>
        </div>
      </motion.div>
    </div>
  )
}
