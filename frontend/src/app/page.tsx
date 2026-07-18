"use client";

import React, { useState, useEffect } from "react";
import { authApi, plansApi, UserResponse, StudyPlanResponse } from "../lib/api";
import Navbar from "../components/Navbar";
import LandingPage from "../components/LandingPage";
import AuthScreen from "../components/AuthScreen";
import IntakeScreen from "../components/IntakeScreen";
import DashboardScreen from "../components/DashboardScreen";
import { Loader2 } from "lucide-react";

export default function Home() {
  const [user, setUser] = useState<UserResponse | null>(null);
  const [activePlan, setActivePlan] = useState<StudyPlanResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [theme, setTheme] = useState<"light" | "dark">("light");
  
  // Controls whether we display the Landing Home view or the App study workspace
  const [viewMode, setViewMode] = useState<"home" | "app">("home");

  // Authenticate user and fetch plans on mount, plus initialize theme
  useEffect(() => {
    // Initialize Theme
    const savedTheme = localStorage.getItem("syllabot_theme") as "light" | "dark";
    const prefersDark = window.matchMedia("(prefers-color-scheme: dark)").matches;
    const initialTheme = savedTheme || (prefersDark ? "dark" : "light");
    setTheme(initialTheme);
    if (initialTheme === "dark") {
      document.documentElement.classList.add("dark");
    } else {
      document.documentElement.classList.remove("dark");
    }

    const initializeSession = async () => {
      if (authApi.isLoggedIn()) {
        try {
          const currentUser = await authApi.getMe();
          setUser(currentUser);

          const plans = await plansApi.getAll();
          const active = plans.find((p) => p.status === "active") || plans[0] || null;
          setActivePlan(active);
        } catch (err) {
          console.error("Session initialization failed, logging out", err);
          authApi.logout();
          setUser(null);
          setActivePlan(null);
        }
      }
      setLoading(false);
    };

    initializeSession();
  }, []);

  const handleThemeToggle = () => {
    const nextTheme = theme === "light" ? "dark" : "light";
    setTheme(nextTheme);
    localStorage.setItem("syllabot_theme", nextTheme);
    if (nextTheme === "dark") {
      document.documentElement.classList.add("dark");
    } else {
      document.documentElement.classList.remove("dark");
    }
  };

  const handleAuthSuccess = async (authenticatedUser: UserResponse) => {
    setUser(authenticatedUser);
    setLoading(true);
    try {
      const plans = await plansApi.getAll();
      const active = plans.find((p) => p.status === "active") || plans[0] || null;
      setActivePlan(active);
      setViewMode("app"); // Transition straight into the app workspace
    } catch (err) {
      console.error("Failed to load user plans on auth success", err);
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    authApi.logout();
    setUser(null);
    setActivePlan(null);
    setViewMode("home"); // Return to landing page on logout
  };

  const handlePlanCreated = (newPlan: StudyPlanResponse) => {
    setActivePlan(newPlan);
  };

  const handlePlanUpdated = (updatedPlan: StudyPlanResponse) => {
    setActivePlan(updatedPlan);
  };

  const handleResetPlan = () => {
    setActivePlan(null);
  };

  if (loading) {
    return (
      <div className="flex-1 flex flex-col items-center justify-center min-h-screen bg-[#13111C]">
        <Loader2 className="animate-spin h-10 w-10 text-primary-blue mb-4" />
        <p className="text-sm font-semibold text-calm-blue animate-pulse">
          Initializing your study space...
        </p>
      </div>
    );
  }

  return (
    <div className="flex flex-col min-h-screen bg-app-bg text-app-text transition-all duration-300">
      <Navbar 
        user={user} 
        onLogout={handleLogout} 
        theme={theme} 
        onThemeToggle={handleThemeToggle} 
        viewMode={viewMode}
        setViewMode={setViewMode}
      />
      
      <main className="flex-1 flex flex-col justify-center">
        {viewMode === "home" ? (
          <LandingPage 
            onEnterApp={() => setViewMode("app")} 
            isLoggedIn={!!user} 
          />
        ) : (
          <div className="flex-1 flex flex-col justify-center">
            {!user ? (
              <AuthScreen onAuthSuccess={handleAuthSuccess} />
            ) : !activePlan ? (
              <IntakeScreen onPlanCreated={handlePlanCreated} />
            ) : (
              <DashboardScreen
                plan={activePlan}
                onPlanUpdated={handlePlanUpdated}
                onResetPlan={handleResetPlan}
                theme={theme}
              />
            )}
          </div>
        )}
      </main>

      <footer className="bg-card-bg border-t border-app-border py-4 text-center text-xs text-calm-blue font-semibold transition-colors duration-300">
        <p>© {new Date().getFullYear()} Syllabot. Your supportive learning companion.</p>
      </footer>
    </div>
  );
}
