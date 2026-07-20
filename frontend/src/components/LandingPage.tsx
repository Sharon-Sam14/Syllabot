"use client";

import React from "react";
import { BookOpen, ArrowRight, Server, Database, CheckCircle2, Star, ShieldCheck, Compass } from "lucide-react";

interface LandingPageProps {
  onEnterApp: () => void;
  isLoggedIn: boolean;
}

export default function LandingPage({ onEnterApp, isLoggedIn }: LandingPageProps) {
  return (
    <div className="bento-container min-h-screen py-12 px-4 sm:px-6 lg:px-8 select-none">
      
      {/* 1. Top Call-to-Action header */}
      <div className="max-w-7xl mx-auto text-center mb-12 space-y-4">
        <h1 className="text-4xl sm:text-6xl font-display font-black text-[#EDE9F6] tracking-tight max-w-4xl mx-auto leading-none">
          The Support System for Your Syllabus
        </h1>
        <p className="text-calm-blue text-sm sm:text-md max-w-xl mx-auto leading-relaxed">
          Ingest unstructured syllabus text, build custom timelines, track consistency, and auto-replan dynamically when falling behind.
        </p>
        <button
          onClick={onEnterApp}
          className="mt-3 inline-flex items-center space-x-2 px-6.5 py-3.5 bg-[#6C3CFA] hover:bg-[#5225E0] text-white font-bold rounded-full shadow-lg transition-all transform hover:scale-105 cursor-pointer text-sm"
        >
          <span>{isLoggedIn ? "Go to Study Space Dashboard" : "Get Started with Syllabot"}</span>
          <ArrowRight className="h-4 w-4 animate-pulse" />
        </button>
      </div>

      {/* 2. Bento-Box Grid Layout (Replicating reference layout structure & colors) */}
      <div className="max-w-7xl mx-auto grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        
        {/* Widget 1: Syllabot Branding Logo Card (Top-Left) */}
        <div className="col-span-2 lg:col-span-1 rounded-3xl p-6 bg-gradient-to-br from-[#6C3CFA] to-[#4D15EA] text-white flex flex-col justify-between lg:aspect-square shadow-md hover:translate-y-[-2px] transition-all text-left">
          <div className="h-12 w-12 rounded-2xl bg-white/10 flex items-center justify-center border border-white/20">
            <BookOpen className="h-6 w-6 text-white" />
          </div>
          <div className="mt-4">
            <h2 className="text-4xl font-display font-black tracking-tight leading-none">
              syllabot
            </h2>
            <p className="text-[10px] font-bold text-white/70 uppercase tracking-wider mt-1.5 leading-relaxed">
              SUPPORTIVE PLANNING ENGINE
            </p>
            <p className="text-[11px] text-white/60 mt-3 leading-relaxed">
              Syllabot acts as the "Google Maps for your syllabus," organizing text schedules into responsive study roadmaps.
            </p>
          </div>
        </div>

        {/* Widget 2: App Mockup/Clock Preview (Top-Middle, Spans 2 Columns) */}
        <div className="col-span-1 md:col-span-2 rounded-3xl p-6 bg-[#EDE9F6] text-[#2C1D54] flex flex-row items-center justify-between overflow-hidden relative min-h-[220px] shadow-sm hover:translate-y-[-2px] transition-all">
          <div className="flex flex-col justify-between h-full max-w-[50%] z-10 text-left">
            <div>
              <span className="text-[9px] font-black uppercase tracking-wider text-[#6C3CFA] bg-[#6C3CFA]/10 px-2 py-0.5 rounded-full">
                Interactive Visuals
              </span>
              <h3 className="text-2xl font-display font-black tracking-tight mt-3 mb-1.5 leading-none">
                Dynamic Study Clock
              </h3>
              <p className="text-xs text-[#2C1D54]/70 leading-relaxed font-semibold">
                Integrates visual 3D flip-cards tracking your active study hours. Click checkboxes to update logs and trigger dynamic calendar updates.
              </p>
            </div>
            <div className="flex items-center space-x-1.5 text-xs font-bold text-[#6C3CFA] cursor-pointer mt-4" onClick={onEnterApp}>
              <span>Preview Dashboard</span>
              <ArrowRight className="h-3 w-3" />
            </div>
          </div>
          
          {/* Centered 3D Graduation Cap & Books Asset */}
          <img 
            src="/graduation_cap.png" 
            alt="3D Graduation Cap on Stacked Books" 
            className="absolute right-12 top-1/2 w-44 h-44 md:w-48 md:h-48 object-contain drop-shadow-2xl hover:scale-105 transition-all duration-300 pointer-events-none select-none hidden sm:block animate-float-slow" 
          />
        </div>

        {/* Widget 3: Student Success Profile Card (Top-Right, Double Height) */}
        <div className="col-span-1 lg:row-span-2 rounded-3xl p-6 bg-[#EDE9F6] text-[#2C1D54] flex flex-col justify-between overflow-hidden relative shadow-sm min-h-[440px] hover:translate-y-[-2px] transition-all">
          <div className="text-left z-10">
            <span className="text-[9px] font-black uppercase tracking-wider text-[#6C3CFA] bg-[#6C3CFA]/10 px-2 py-0.5 rounded-full">
              Vision & Goal
            </span>
            <h3 className="text-xl font-display font-black tracking-tight mt-3 leading-tight">
              Calm Consistency
            </h3>
            <p className="text-xs text-[#2C1D54]/70 leading-relaxed font-semibold mt-1">
              Maintains focus on small study milestones, reducing anxiety through visual transparency.
            </p>
          </div>

          {/* Avatar with layered purple circle background shapes */}
          <div className="my-6 relative flex justify-center items-center h-48 w-full">
            <div className="absolute w-44 h-44 rounded-full bg-[#6C3CFA]/15 transform -translate-x-3 -translate-y-2 animate-pulse" />
            <div className="absolute w-40 h-40 rounded-full bg-[#6C3CFA]/25 transform translate-x-2 translate-y-3" />
            <img 
              src="/student_avatar.png" 
              alt="Student Success Profile Avatar" 
              className="w-40 h-40 object-contain rounded-full border border-[#2C1D54]/10 shadow-md bg-white relative z-10" 
            />
          </div>

          <div className="flex justify-between items-center text-xs font-bold text-[#2C1D54]/90 pt-3 border-t border-[#2C1D54]/10 z-10 mt-2">
            <span>STUDENT VIVAS</span>
            <span className="text-white bg-[#6C3CFA] uppercase tracking-wider font-extrabold px-3 py-1 rounded-full text-[10px]">
              Avail
            </span>
          </div>
        </div>

        {/* Widget 4: Stack Architecture stats (Middle-Left) */}
        <div className="col-span-1 rounded-3xl p-6 bg-[#EDE9F6] text-[#2C1D54] flex flex-col justify-between aspect-square shadow-sm hover:translate-y-[-2px] transition-all text-left">
          <div>
            <span className="text-[9px] font-black uppercase tracking-wider text-[#6C3CFA] bg-[#6C3CFA]/10 px-2 py-0.5 rounded-full">
              Core Architecture
            </span>
            <h3 className="text-sm font-bold text-[#2C1D54]/80 mt-3 uppercase tracking-wider">
              Application Stack
            </h3>
            <p className="text-3xl font-display font-black tracking-tight mt-1 leading-none">
              FastAPI
            </p>
            <div className="text-[11px] text-[#2C1D54]/70 mt-2 font-semibold space-y-1">
              <p>• Next.js TS Client</p>
              <p>• SQLAlchemy models</p>
              <p>• Alembic migration logs</p>
            </div>
          </div>
          <div className="flex items-center space-x-1.5 text-xs text-[#2C1D54]/90 pt-2 border-t border-[#2C1D54]/10 font-bold uppercase tracking-wider">
            <Server className="h-4 w-4 text-[#6C3CFA]" />
            <span>SQLite db</span>
          </div>
        </div>

        {/* Widget 5: Overlapping Avatars & Rating (Middle Middle-Left) */}
        <div className="col-span-1 rounded-3xl p-6 bg-[#EDE9F6] text-[#2C1D54] flex flex-col justify-between aspect-square shadow-sm hover:translate-y-[-2px] transition-all text-left">
          <div>
            <span className="text-[9px] font-black uppercase tracking-wider text-[#6C3CFA] bg-[#6C3CFA]/10 px-2 py-0.5 rounded-full">
              Engine Health
            </span>
            
            <div className="flex justify-between items-baseline mt-3">
              <p className="text-4xl font-display font-black tracking-tight leading-none">
                4.9
              </p>
              <div className="flex text-amber-500 scale-90">
                {[1, 2, 3, 4, 5].map((s) => (
                  <Star key={s} className="h-3.5 w-3.5 fill-current" />
                ))}
              </div>
            </div>

            {/* Overlapping avatar visual circles emulating reference image */}
            <div className="flex items-center space-x-[-8px] my-3">
              {["#FF9F43", "#00CFE8", "#28C76F", "#EA5455"].map((color, i) => (
                <div 
                  key={i} 
                  className="h-7 w-7 rounded-full border-2 border-[#EDE9F6] flex items-center justify-center text-[9px] font-black text-white"
                  style={{ backgroundColor: color }}
                >
                  {["A", "J", "M", "S"][i]}
                </div>
              ))}
              <span className="text-[10px] text-calm-blue font-bold ml-2">Active Students</span>
            </div>
          </div>

          <div className="flex items-center space-x-1.5 text-xs text-[#2C1D54]/90 pt-2 border-t border-[#2C1D54]/10 font-bold uppercase tracking-wider">
            <CheckCircle2 className="h-4 w-4 text-emerald-600" />
            <span>14 tests passed</span>
          </div>
        </div>

        {/* Widget 6: Tall Working Steps Card (Middle Middle-Right, Double Height) */}
        <div className="col-span-1 lg:row-span-2 rounded-3xl p-6 bg-[#EDE9F6] text-[#2C1D54] flex flex-col justify-between shadow-sm min-h-[440px] hover:translate-y-[-2px] transition-all text-left">
          <div>
            <span className="text-[9px] font-black uppercase tracking-wider text-[#6C3CFA] bg-[#6C3CFA]/10 px-2 py-0.5 rounded-full">
              Working Process
            </span>
            <h3 className="text-2xl font-display font-black tracking-tight mt-3 mb-3 leading-none">
              Planner Lifecycle
            </h3>
            
            <div className="space-y-4 mt-3 text-[11px] font-semibold text-[#2C1D54]/90 leading-relaxed">
              <div className="flex items-start space-x-2">
                <span className="h-4 w-4 bg-[#6C3CFA] text-white text-[8px] font-black flex items-center justify-center rounded-full shrink-0 mt-0.5">1</span>
                <p className="leading-tight"><strong className="text-[#6C3CFA]">Ingestion:</strong> Paste syllabus text. The parsing parser extracts hierarchical study topics.</p>
              </div>
              <div className="flex items-start space-x-2">
                <span className="h-4 w-4 bg-[#6C3CFA] text-white text-[8px] font-black flex items-center justify-center rounded-full shrink-0 mt-0.5">2</span>
                <p className="leading-tight"><strong className="text-[#6C3CFA]">Allocation:</strong> Daily timelines split topics evenly to hit targets before deadlines.</p>
              </div>
              <div className="flex items-start space-x-2">
                <span className="h-4 w-4 bg-[#6C3CFA] text-white text-[8px] font-black flex items-center justify-center rounded-full shrink-0 mt-0.5">3</span>
                <p className="leading-tight"><strong className="text-[#6C3CFA]">Logs:</strong> Checking off topics updates study velocity. Falling behind triggers automated dynamically adjusted recalculations.</p>
              </div>
            </div>
          </div>

          {/* Rotating purple Asterisk */}
          <div className="flex justify-center items-center my-4">
            <svg className="w-20 h-20 text-[#6C3CFA] animate-spin-slow" viewBox="0 0 100 100">
              <path 
                d="M 50 10 L 50 90 M 10 50 L 90 50 M 22 22 L 78 78 M 22 78 L 78 22" 
                stroke="currentColor" 
                strokeWidth="10" 
                strokeLinecap="round" 
              />
            </svg>
          </div>
        </div>

        {/* Widget 7: Pacing Wave Chart Card (Bottom-Left, Spans 2 Columns) */}
        <div className="col-span-1 md:col-span-2 rounded-3xl p-6 bg-gradient-to-br from-[#6C3CFA] to-[#4D15EA] text-white flex flex-col justify-between overflow-hidden relative min-h-[200px] shadow-md hover:translate-y-[-2px] transition-all text-left">
          <div className="text-left z-10 flex justify-between items-start">
            <div>
              <span className="text-[9px] font-black uppercase tracking-wider text-white bg-white/10 px-2 py-0.5 rounded-full border border-white/15">
                Planning Engine
              </span>
              <h3 className="text-2xl font-display font-black tracking-tight mt-3 leading-none">
                Pacing Dynamics
              </h3>
            </div>
            <div className="text-right">
              <p className="text-[8px] font-extrabold text-white/70 uppercase">Velocity Ratio</p>
              <p className="text-xl font-bold">1.0x (Stable)</p>
            </div>
          </div>

          {/* Flowing consistency wave visualizer with multiple layers matching reference */}
          <div className="absolute bottom-0 left-0 right-0 h-28 overflow-hidden pointer-events-none opacity-45">
            <svg className="w-full h-full" viewBox="0 0 200 60" preserveAspectRatio="none">
              {/* Wave Layer 1 */}
              <path 
                d="M 0 50 Q 25 20 50 35 T 100 20 T 150 40 T 200 10 L 200 60 L 0 60 Z" 
                fill="url(#bento-wave-1)" 
                opacity="0.3"
              />
              {/* Wave Layer 2 */}
              <path 
                d="M 0 40 Q 30 10 60 25 T 120 15 T 180 30 T 200 5 L 200 60 L 0 60 Z" 
                fill="url(#bento-wave-2)" 
                opacity="0.6"
              />
              <defs>
                <linearGradient id="bento-wave-1" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="#ffffff" stopOpacity="0.4" />
                  <stop offset="100%" stopColor="#6C3CFA" stopOpacity="0" />
                </linearGradient>
                <linearGradient id="bento-wave-2" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="#ffffff" stopOpacity="0.6" />
                  <stop offset="100%" stopColor="#6C3CFA" stopOpacity="0" />
                </linearGradient>
              </defs>
            </svg>
          </div>
        </div>

        {/* Widget 8: Pie Chart Progress Completion Card (Bottom-Right) */}
        <div className="col-span-2 lg:col-span-1 rounded-3xl p-6 bg-gradient-to-br from-[#6C3CFA] to-[#4D15EA] text-white flex flex-col justify-between lg:aspect-square shadow-md hover:translate-y-[-2px] transition-all text-left">
          <div>
            <span className="text-[9px] font-black uppercase tracking-wider text-white bg-white/10 px-2 py-0.5 rounded-full border border-white/15">
              Analytics Tracker
            </span>
            <h3 className="text-sm font-bold text-white/80 mt-3 uppercase tracking-wider">
              Study Velocity
            </h3>
          </div>
          
          {/* Circular donut graph visual representation */}
          <div className="relative flex justify-center items-center my-1.5 h-16 w-full">
            <svg className="w-16 h-16" viewBox="0 0 36 36">
              <circle cx="18" cy="18" r="16" fill="none" stroke="rgba(255, 255, 255, 0.1)" strokeWidth="4" />
              <circle 
                cx="18" 
                cy="18" 
                r="16" 
                fill="none" 
                stroke="#EDE9F6" 
                strokeWidth="4" 
                strokeDasharray="100" 
                strokeDashoffset="77"
                strokeLinecap="round" 
              />
            </svg>
            <span className="absolute text-xs font-black text-white">+23%</span>
          </div>

          <div className="flex justify-between items-center text-[10px] font-bold text-white/90 pt-2 border-t border-white/10">
            <span>INTENSITY SCORE</span>
            <span className="text-white font-extrabold uppercase">Stable</span>
          </div>
        </div>

      </div>

      <style jsx>{`
        .bento-container {
          background-color: #13111C;
        }

        @keyframes spin-slow {
          from {
            transform: rotate(0deg);
          }
          to {
            transform: rotate(360deg);
          }
        }

        .animate-spin-slow {
          animation: spin-slow 12s linear infinite;
        }

        @keyframes float-slow {
          0%, 100% {
            transform: translateY(-50%) translateY(0px);
          }
          50% {
            transform: translateY(-50%) translateY(-10px);
          }
        }

        .animate-float-slow {
          animation: float-slow 4s ease-in-out infinite;
        }
      `}</style>
    </div>
  );
}
