"use client";
import { useRouter } from "next/navigation";
export default function LoginPage() {
  const router = useRouter();

  function handleLogin(e: React.FormEvent) {
    e.preventDefault();
    router.push("/dashboard");
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-950 to-slate-900 flex items-center justify-center p-4">
      
      {/* Card */}
      <div className="bg-white rounded-2xl shadow-2xl w-full max-w-md p-8">
        
        {/* Logo & Title */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-blue-600 rounded-2xl mb-4">
            <span className="text-white text-2xl">🧠</span>
          </div>
          <h1 className="text-2xl font-bold text-slate-900">MindBridge Health AI</h1>
          <p className="text-slate-500 text-sm mt-1">HIPAA-Compliant Behavioral Health Platform</p>
        </div>

        {/* Form */}
        <form className="space-y-4" onSubmit={handleLogin}>
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">
              Email Address
            </label>
            <input
              type="email"
              placeholder="clinician@mindbridge.health"
              className="w-full px-4 py-3 border border-slate-200 rounded-lg text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">
              Password
            </label>
            <input
              type="password"
              placeholder="••••••••"
              className="w-full px-4 py-3 border border-slate-200 rounded-lg text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>

          <button
            type="submit"
            className="w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold py-3 px-4 rounded-lg transition-colors duration-200"
          >
            Sign In to Dashboard
          </button>
        </form>

        {/* Demo credentials */}
        <div className="mt-6 p-4 bg-slate-50 rounded-lg border border-slate-200">
          <p className="text-xs font-semibold text-slate-500 uppercase tracking-wide mb-2">Demo Credentials</p>
          <p className="text-sm text-slate-600">📧 demo@mindbridge.health</p>
          <p className="text-sm text-slate-600">🔑 MindBridge2026!</p>
        </div>

        {/* HIPAA badge */}
        <div className="mt-6 flex items-center justify-center gap-2 text-xs text-slate-400">
          <span>🔒</span>
          <span>256-bit encrypted · HIPAA compliant · SOC 2 ready</span>
        </div>
      </div>
    </div>
  );
}