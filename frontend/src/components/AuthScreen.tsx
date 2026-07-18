import React, { useState } from "react";
import { authApi, UserResponse } from "../lib/api";
import { Mail, Lock, User, AlertCircle, ArrowRight, Loader2 } from "lucide-react";

interface AuthScreenProps {
  onAuthSuccess: (user: UserResponse) => void;
}

export default function AuthScreen({ onAuthSuccess }: AuthScreenProps) {
  const [mode, setMode] = useState<"login" | "signup">("login");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [name, setName] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      if (mode === "signup") {
        if (!name.trim()) {
          throw new Error("Name is required");
        }
        await authApi.signup({ email, password, name });
        // After signup, automatically login
      }

      // Login logic
      const formData = new FormData();
      formData.append("username", email);
      formData.append("password", password);

      await authApi.login(formData);
      const user = await authApi.getMe();
      onAuthSuccess(user);
    } catch (err: any) {
      console.error(err);
      setError(err.message || "An authentication error occurred.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex-1 flex flex-col justify-center py-12 sm:px-6 lg:px-8 bg-warm-neutral">
      <div className="sm:mx-auto sm:w-full sm:max-w-md text-center">
        <h2 className="text-3xl font-display font-extrabold text-app-text tracking-tight animate-slide-up">
          {mode === "login" ? "Welcome back" : "Create your study space"}
        </h2>
        <p className="mt-2.5 text-sm text-calm-blue max-w-xs mx-auto">
          {mode === "login"
            ? "Log in to track your study goals and see your adaptive plan."
            : "Sign up to turn your syllabus into an intelligent study roadmap."}
        </p>
      </div>

      <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md animate-fade-in">
        <div className="bg-card-bg py-8 px-4 border border-app-border shadow-sm rounded-2xl sm:px-10 relative overflow-hidden transition-colors duration-300">
          {/* Top colored accent line */}
          <div className="absolute top-0 left-0 right-0 h-1.5 bg-gradient-to-r from-primary-blue via-calm-blue to-progress-teal" />

          <form className="space-y-5" onSubmit={handleSubmit}>
            {error && (
              <div className="rounded-xl bg-red-50/10 border border-red-500/20 p-4 flex items-start space-x-2.5">
                <AlertCircle className="h-5 w-5 text-red-500 shrink-0 mt-0.5" />
                <span className="text-sm text-red-500 font-medium">{error}</span>
              </div>
            )}

            {mode === "signup" && (
              <div>
                <label className="block text-xs font-semibold text-app-text/80 uppercase tracking-wider mb-1.5">
                  Full Name
                </label>
                <div className="relative rounded-xl shadow-xs">
                  <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-calm-blue/70">
                    <User className="h-5 w-5" />
                  </div>
                  <input
                    type="text"
                    required
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    className="block w-full pl-10 pr-4 py-2.5 bg-app-bg border border-app-border rounded-xl text-app-text placeholder-calm-blue/50 focus:outline-hidden focus:ring-2 focus:ring-primary-blue/20 focus:border-primary-blue transition-all text-sm"
                    placeholder="Alex Student"
                  />
                </div>
              </div>
            )}

            <div>
              <label className="block text-xs font-semibold text-app-text/80 uppercase tracking-wider mb-1.5">
                Email address
              </label>
              <div className="relative rounded-xl shadow-xs">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-calm-blue/70">
                  <Mail className="h-5 w-5" />
                </div>
                <input
                  type="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="block w-full pl-10 pr-4 py-2.5 bg-app-bg border border-app-border rounded-xl text-app-text placeholder-calm-blue/50 focus:outline-hidden focus:ring-2 focus:ring-primary-blue/20 focus:border-primary-blue transition-all text-sm"
                  placeholder="student@example.com"
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-semibold text-app-text/80 uppercase tracking-wider mb-1.5">
                Password
              </label>
              <div className="relative rounded-xl shadow-xs">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-calm-blue/70">
                  <Lock className="h-5 w-5" />
                </div>
                <input
                  type="password"
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="block w-full pl-10 pr-4 py-2.5 bg-app-bg border border-app-border rounded-xl text-app-text placeholder-calm-blue/50 focus:outline-hidden focus:ring-2 focus:ring-primary-blue/20 focus:border-primary-blue transition-all text-sm"
                  placeholder="••••••••"
                />
              </div>
            </div>

            <div className="pt-2">
              <button
                type="submit"
                disabled={loading}
                className="w-full flex justify-center items-center py-3 px-4 border border-transparent rounded-xl shadow-sm text-sm font-semibold text-white bg-gradient-to-r from-primary-blue to-calm-blue hover:from-primary-navy hover:to-primary-blue focus:outline-hidden focus:ring-2 focus:ring-offset-2 focus:ring-primary-blue transition-all disabled:opacity-50 cursor-pointer"
              >
                {loading ? (
                  <Loader2 className="animate-spin h-5 w-5 text-white" />
                ) : (
                  <>
                    <span>{mode === "login" ? "Sign In" : "Get Started"}</span>
                    <ArrowRight className="ml-2 h-4 w-4" />
                  </>
                )}
              </button>
            </div>
          </form>

          <div className="mt-6 pt-5 border-t border-app-border text-center">
            <button
              onClick={() => {
                setMode(mode === "login" ? "signup" : "login");
                setError(null);
              }}
              className="text-sm font-medium text-primary-blue hover:text-primary-navy transition-colors cursor-pointer"
            >
              {mode === "login"
                ? "Don't have an account? Sign up"
                : "Already have an account? Sign in"}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
