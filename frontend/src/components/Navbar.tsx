import React from "react";
import { UserResponse } from "../lib/api";
import { LogOut, BookOpen, User, Sun, Moon, Home as HomeIcon, LayoutDashboard } from "lucide-react";

interface NavbarProps {
  user: UserResponse | null;
  onLogout: () => void;
  theme: "light" | "dark";
  onThemeToggle: () => void;
  viewMode: "home" | "app";
  setViewMode: (mode: "home" | "app") => void;
}

export default function Navbar({
  user,
  onLogout,
  theme,
  onThemeToggle,
  viewMode,
  setViewMode,
}: NavbarProps) {
  return (
    <nav className="bg-card-bg border-b border-app-border sticky top-0 z-50 transition-all duration-300 select-none">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          {/* Logo Section */}
          <div
            onClick={() => setViewMode("home")}
            className="flex items-center space-x-2 sm:space-x-3 cursor-pointer group"
          >
            <div className="flex items-center justify-center h-9 w-9 sm:h-10 sm:w-10 rounded-xl bg-gradient-to-br from-primary-blue to-calm-blue text-white shadow-sm group-hover:opacity-90 transition-all">
              <BookOpen className="h-5 w-5 sm:h-5.5 sm:w-5.5" />
            </div>
            <div className="text-left">
              <span className="font-display font-bold text-lg sm:text-xl text-app-text tracking-tight group-hover:text-primary-blue transition-all">
                Syllabot
              </span>
            </div>
          </div>

          {/* Controls & Profile Section */}
          <div className="flex items-center space-x-2 sm:space-x-3.5">
            {/* View switcher buttons based on state */}
            {viewMode === "home" ? (
              <button
                onClick={() => setViewMode("app")}
                className="flex items-center space-x-1 sm:space-x-1.5 text-xs font-bold text-white bg-gradient-to-r from-primary-blue to-calm-blue hover:from-primary-navy hover:to-primary-blue px-3 py-2 sm:px-4.5 sm:py-2.5 rounded-xl shadow-xs transition-all cursor-pointer"
              >
                {user ? (
                  <>
                    <LayoutDashboard className="h-3.5 w-3.5" />
                    <span className="hidden xs:inline">Dashboard</span>
                    <span className="xs:hidden">App</span>
                  </>
                ) : (
                  <span>Login / Start</span>
                )}
              </button>
            ) : (
              <button
                onClick={() => setViewMode("home")}
                className="flex items-center space-x-1 sm:space-x-1.5 text-xs font-bold text-app-text bg-app-bg hover:bg-card-bg px-3 py-2 sm:px-4.5 sm:py-2.5 rounded-xl border border-app-border transition-all cursor-pointer"
              >
                <HomeIcon className="h-3.5 w-3.5" />
                <span className="hidden xs:inline">Home</span>
                <span className="xs:hidden">Home</span>
              </button>
            )}

            {/* Theme Toggle Button */}
            <button
              onClick={onThemeToggle}
              aria-label="Toggle theme"
              className="flex items-center justify-center h-9 w-9 rounded-xl bg-app-bg border border-app-border text-app-text hover:bg-card-bg transition-all duration-200 shadow-2xs cursor-pointer"
            >
              {theme === "light" ? (
                <Moon className="h-4.5 w-4.5 text-primary-navy" />
              ) : (
                <Sun className="h-4.5 w-4.5 text-neon-yellow" />
              )}
            </button>

            {user && (
              <div className="flex items-center space-x-1.5 sm:space-x-3">
                <div className="flex items-center space-x-2 px-2.5 py-1.5 rounded-xl bg-app-bg border border-app-border transition-all duration-300">
                  <div className="h-6 w-6 sm:h-7 sm:w-7 rounded-full bg-app-border/40 flex items-center justify-center text-primary-blue font-semibold text-xs sm:text-sm">
                    <User className="h-3.5 w-3.5 text-app-text/80" />
                  </div>
                  <div className="text-left hidden sm:block">
                    <p className="text-xs font-bold text-app-text leading-tight">
                      {user.name || user.email}
                    </p>
                    <p className="text-[10px] text-calm-blue font-medium leading-none mt-0.5">
                      {user.email}
                    </p>
                  </div>
                </div>

                <button
                  onClick={onLogout}
                  className="flex items-center space-x-1 text-xs font-semibold text-app-text/75 hover:text-red-500 transition-colors duration-200 px-2 py-1.5 sm:px-3 sm:py-2 rounded-xl hover:bg-red-50/10 border border-transparent hover:border-red-500/20 cursor-pointer"
                >
                  <LogOut className="h-4 w-4" />
                  <span className="hidden md:inline">Sign Out</span>
                </button>
              </div>
            )}
          </div>
        </div>
      </div>
    </nav>
  );
}
