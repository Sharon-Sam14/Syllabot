import React, { useState, useEffect, useRef, useCallback } from "react";
import {
  StudyPlanResponse,
  DailyProgressResponse,
  plansApi,
  progressApi,
  StudyPlanDay,
  StudyPlanTopic,
  aiApi,
  AIChatMessage,
} from "../lib/api";
import FlipClock from "./FlipClock";
import {
  Calendar,
  CheckCircle,
  Clock,
  RotateCcw,
  BookOpen,
  CalendarDays,
  CheckSquare,
  Square,
  Award,
  Sparkles,
  HelpCircle,
  FileText,
  ChevronRight,
  TrendingUp,
  RefreshCw,
  Clock3,
  Loader2,
  AlertCircle,
  MoreHorizontal,
  Flame,
  Search,
  Sliders,
  Pause,
  Play
} from "lucide-react";

interface DashboardScreenProps {
  plan: StudyPlanResponse;
  onPlanUpdated: (updatedPlan: StudyPlanResponse) => void;
  onResetPlan: () => void;
  theme: "light" | "dark";
}

export default function DashboardScreen({
  plan,
  onPlanUpdated,
  onResetPlan,
  theme,
}: DashboardScreenProps) {
  const [progressHistory, setProgressHistory] = useState<DailyProgressResponse[]>([]);
  const [completedTopicIds, setCompletedTopicIds] = useState<Set<string>>(new Set());
  
  // Check-in form state
  const [hoursStudied, setHoursStudied] = useState<string>("1.5");
  const [checkInNote, setCheckInNote] = useState("");
  const [selectedTopics, setSelectedTopics] = useState<Record<string, boolean>>({});
  const [formLoading, setFormLoading] = useState(false);
  const [formError, setFormError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  // Manual Replan state
  const [replanDate, setReplanDate] = useState(() => {
    const tomorrow = new Date();
    tomorrow.setDate(tomorrow.getDate() + 1);
    return tomorrow.toISOString().split("T")[0];
  });
  const [replanLoading, setReplanLoading] = useState(false);

  const [activeCategory, setActiveCategory] = useState<string>("Roadmap");

  // Interactive Stopwatch Timer state
  const [timerActive, setTimerActive] = useState(false);
  const [timerSeconds, setTimerSeconds] = useState(0);

  // AI Neural Assist state
  const [aiMessages, setAiMessages] = useState<AIChatMessage[]>([]);
  const [aiInput, setAiInput] = useState("");
  const [aiLoading, setAiLoading] = useState(false);
  const [aiError, setAiError] = useState<string | null>(null);
  const [aiConversationId] = useState(() => Math.random().toString(36).slice(2) + Date.now().toString(36));
  const aiChatEndRef = useRef<HTMLDivElement>(null);

  // Tuner recall target state
  const [recallTarget, setRecallTarget] = useState(92.4);

  // Collapsible schedule days
  const [collapsedDays, setCollapsedDays] = useState<Record<number, boolean>>({});

  // Active Dropdowns state
  const [activeDropdown, setActiveDropdown] = useState<string | null>(null);

  // Live stopwatch timer hook
  useEffect(() => {
    let interval: any = null;
    if (timerActive) {
      interval = setInterval(() => {
        setTimerSeconds((prev) => prev + 1);
      }, 1000);
    } else {
      clearInterval(interval);
    }
    return () => clearInterval(interval);
  }, [timerActive]);

  const formatTime = (totalSecs: number) => {
    const hrs = Math.floor(totalSecs / 3600);
    const mins = Math.floor((totalSecs % 3600) / 60);
    const secs = totalSecs % 60;
    return [
      hrs.toString().padStart(2, "0"),
      mins.toString().padStart(2, "0"),
      secs.toString().padStart(2, "0"),
    ].join(":");
  };

  const toggleDayCollapse = (dayNum: number) => {
    setCollapsedDays((prev) => ({
      ...prev,
      [dayNum]: !prev[dayNum],
    }));
  };

  const handleDropdownToggle = (dropdownId: string) => {
    setActiveDropdown((prev) => (prev === dropdownId ? null : dropdownId));
  };


  // Fetch progress history
  const fetchProgress = async () => {
    try {
      const history = await progressApi.getHistory(plan.id);
      setProgressHistory(history);
      
      const completedSet = new Set<string>();
      history.forEach((log) => {
        if (log.completed_topics) {
          log.completed_topics.forEach((topicId: string) => completedSet.add(topicId));
        }
      });
      setCompletedTopicIds(completedSet);
    } catch (err) {
      console.error("Error loading progress logs", err);
    }
  };

  useEffect(() => {
    fetchProgress();
  }, [plan.id]);

  // Find today's plan day
  const todayStr = new Date().toISOString().split("T")[0];
  const todayPlanDay = plan.plan_json.find((d) => d.date === todayStr) || 
                       plan.plan_json.find((d) => {
                         const dayTopics = d.topics || [];
                         return dayTopics.some((t) => !completedTopicIds.has(t.id));
                       }) || 
                       plan.plan_json[0];

  // Initialize selected check-in topics when today's plan day changes
  useEffect(() => {
    if (todayPlanDay && todayPlanDay.topics) {
      const initialSelection: Record<string, boolean> = {};
      todayPlanDay.topics.forEach((t) => {
        initialSelection[t.id] = completedTopicIds.has(t.id);
      });
      setSelectedTopics(initialSelection);
    }
  }, [todayPlanDay, completedTopicIds]);

  const handleTopicToggle = (topicId: string) => {
    setSelectedTopics((prev) => ({
      ...prev,
      [topicId]: !prev[topicId],
    }));
  };

  const handleCheckInSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setFormError(null);
    setSuccessMessage(null);
    setFormLoading(true);

    const completedList = Object.entries(selectedTopics)
      .filter(([_, isChecked]) => isChecked)
      .map(([topicId]) => topicId);

    const checkInDate = todayPlanDay?.date || todayStr;

    try {
      await progressApi.log(plan.id, {
        date: checkInDate,
        completed_hours: parseFloat(hoursStudied) || 0,
        completed_topics: completedList,
        check_in_note: checkInNote,
      });

      setSuccessMessage("Progress logged! Schedule replanned dynamically.");
      setCheckInNote("");
      
      await fetchProgress();
      const updatedPlan = await plansApi.getOne(plan.id);
      onPlanUpdated(updatedPlan);
    } catch (err: any) {
      console.error(err);
      setFormError(err.message || "Failed to log progress.");
    } finally {
      setFormLoading(false);
    }
  };

  const handleManualReplan = async () => {
    setReplanLoading(true);
    try {
      const updatedPlan = await plansApi.replan(plan.id, replanDate);
      onPlanUpdated(updatedPlan);
      await fetchProgress();
      alert("Plan recalculated successfully.");
    } catch (err: any) {
      alert(err.message || "Manual replan failed.");
    } finally {
      setReplanLoading(false);
    }
  };

  const handleToggleRoadmapTopic = async (topicId: string, topicDate: string) => {
    const isCompleted = completedTopicIds.has(topicId);
    if (isCompleted) {
      alert("Topic is already marked as completed.");
      return;
    }

    try {
      await progressApi.log(plan.id, {
        date: topicDate,
        completed_hours: 0.5,
        completed_topics: [topicId],
        check_in_note: "Covered topic from roadmap checklist.",
      });
      await fetchProgress();
      const updatedPlan = await plansApi.getOne(plan.id);
      onPlanUpdated(updatedPlan);
    } catch (err: any) {
      alert(err.message || "Failed to log progress.");
    }
  };

  // Calculate Progress Stats
  const allPlanTopics = plan.plan_json.reduce<StudyPlanTopic[]>((acc, d) => {
    return acc.concat(d.topics || []);
  }, []);
  const totalTopicsCount = allPlanTopics.length;
  const completedTopicsCount = allPlanTopics.filter((t) => completedTopicIds.has(t.id)).length;
  const progressPercent = totalTopicsCount > 0 
    ? Math.round((completedTopicsCount / totalTopicsCount) * 100) 
    : 0;

  // Dynamic colors for charts/metrics mapping light vs dark mode
  const isDark = theme === "dark";
  const neonGreen = isDark ? "#00FF66" : "#2E9D9A";
  const neonCyan = isDark ? "#00F0FF" : "#4E7DA0";
  const neonYellow = isDark ? "#E1FF00" : "#1F4E79";
  const neonOrange = isDark ? "#FF5C00" : "#E67E22";
  const neonRed = isDark ? "#FF0055" : "#E74C3C";

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 space-y-8 animate-fade-in">
      
      {/* 1. Header Card (Cardiology styled layout structure for both themes) */}
      <div className="squircle-card p-6">
        <div className="flex flex-col lg:flex-row justify-between items-start lg:items-center gap-6 pb-6 border-b border-app-border">
          <div className="flex items-center space-x-4">
            <div className="h-14 w-14 rounded-2xl bg-app-bg border border-app-border flex items-center justify-center text-primary-blue transition-colors duration-300">
              <BookOpen className="h-7 w-7 text-app-text/90" />
            </div>
            <div className="text-left">
              <h1 className="text-3xl font-display font-extrabold text-app-text tracking-tight transition-colors duration-300">
                Syllabot Overview
              </h1>
              <p className="text-xs font-semibold text-calm-blue mt-0.5 uppercase tracking-wider">
                Timeline: {plan.start_date} to {plan.end_date}
              </p>
            </div>
          </div>

          {/* Cardiology Category Tabs */}
          <div className="flex flex-wrap items-center gap-2">
            {[
              { id: "Roadmap", label: "Treatment Dynamics" },
              { id: "Check-ins", label: "Visits & Logs" },
              { id: "Settings", label: "Genetics & Replan" },
              { id: "AI Assistant", label: "Neural Assist" }
            ].map((tab) => (
              <button
                key={tab.id}
                id={`dashboard-tab-${tab.id.toLowerCase().replace(/\s+/g, '-')}`}
                onClick={() => setActiveCategory(tab.id)}
                className={`px-4 py-2 text-xs font-bold rounded-full border transition-all duration-200 cursor-pointer ${
                  activeCategory === tab.id
                    ? "bg-card-bg text-app-text border-app-text ring-1 ring-app-text"
                    : "bg-app-bg/40 text-app-text/70 border-transparent hover:border-app-border"
                }`}
              >
                {tab.id === "AI Assistant" ? (
                  <span className="flex items-center gap-1">
                    <Sparkles className="h-3 w-3" />
                    {tab.label}
                  </span>
                ) : tab.label}
              </button>
            ))}
          </div>
        </div>

        {/* Diagnostic Stats Header Fields */}
        <div className="grid grid-cols-2 md:grid-cols-5 gap-6 pt-6 text-left">
          <div>
            <p className="text-[10px] font-bold text-calm-blue uppercase tracking-wider">Active Day</p>
            <p className="text-lg font-extrabold text-app-text mt-1 leading-tight">
              Day {todayPlanDay?.day_number || 1}
            </p>
          </div>
          <div>
            <p className="text-[10px] font-bold text-calm-blue uppercase tracking-wider">Calibration Rate</p>
            <p className="text-lg font-extrabold text-app-text mt-1 leading-tight">
              {progressPercent}% <span className="text-xs text-calm-blue">({completedTopicsCount}/{totalTopicsCount})</span>
            </p>
          </div>
          <div>
            <p className="text-[10px] font-bold text-calm-blue uppercase tracking-wider">Time Horizon</p>
            <p className="text-lg font-extrabold text-app-text mt-1 leading-tight">
              {plan.plan_json.length} days
            </p>
          </div>
          <div>
            <p className="text-[10px] font-bold text-calm-blue uppercase tracking-wider">Total Intensity</p>
            <p className="text-lg font-extrabold text-app-text mt-1 leading-tight">
              {progressHistory.reduce((acc, log) => acc + log.completed_hours, 0).toFixed(1)} hrs
            </p>
          </div>
          <div className="col-span-2 md:col-span-1 flex items-center md:justify-end">
            <button
              onClick={onResetPlan}
              className="flex items-center space-x-1.5 text-xs font-bold text-app-text bg-app-bg hover:bg-app-bg/75 px-4 py-2.5 rounded-full border border-app-border transition-all cursor-pointer"
            >
              <RotateCcw className="h-3.5 w-3.5" />
              <span>Reset Plan</span>
            </button>
          </div>
        </div>
      </div>

      {activeCategory === "Roadmap" && (
        <>
          {/* 2. 3x2 Widgets Grid Layout (Identical components in both Light and Dark themes) */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            
            {/* Widget 1: System Pacing / Time Calibration */}
            <div className={`squircle-card overflow-hidden min-h-[300px] flex flex-col justify-between p-6 ${isDark ? "neon-glow-green" : ""}`}>
              <div className="squircle-tab-top relative">
                <button
                  onClick={() => handleDropdownToggle("widget1")}
                  className="h-6 w-6 flex items-center justify-center hover:bg-app-bg/50 rounded-full transition-all cursor-pointer"
                >
                  <MoreHorizontal className="h-4 w-4 text-calm-blue" />
                </button>
                {activeDropdown === "widget1" && (
                  <div className="absolute right-0 top-7 w-44 bg-card-bg border border-app-border rounded-xl shadow-lg p-2 z-10 text-xs text-app-text text-left">
                    <div className="px-2 py-1.5 font-bold border-b border-app-border mb-1">Pacing Dynamics</div>
                    <p className="px-2 py-1 text-[10px] text-calm-blue leading-relaxed">
                      Velocity factor is calculated dynamically based on target pacing logs.
                    </p>
                  </div>
                )}
              </div>
              
              <div className="text-left">
                <p className="text-xs font-bold text-calm-blue uppercase tracking-wider">System Clock</p>
                <h3 className="text-sm font-extrabold text-app-text/60 mt-1 uppercase">
                  Paced Target Status
                </h3>
                <h2 className="text-4xl font-display font-black text-app-text mt-2 leading-none tracking-tight">
                  {todayPlanDay?.date?.split("-")?.[2] || "19"}{" "}
                  <span className="text-lg font-bold text-calm-blue block mt-1">{todayPlanDay?.date || todayStr}</span>
                </h2>
              </div>

              <div className="text-left space-y-4">
                <div>
                  <div className="flex justify-between items-center text-[10px] font-bold text-calm-blue mb-1">
                    <span>ROADMAP ADHERENCE</span>
                    <span style={{ color: neonGreen }} className="font-extrabold">{progressPercent}%</span>
                  </div>
                  <div className="h-3 w-full bg-app-bg rounded-full overflow-hidden p-0.5 border border-app-border">
                    <div 
                      className="h-full rounded-full transition-all duration-500"
                      style={{ 
                        width: `${progressPercent}%`, 
                        backgroundColor: neonGreen,
                        boxShadow: isDark ? `0 0 8px ${neonGreen}` : "none"
                      }}
                    />
                  </div>
                </div>

                <div className="flex justify-between items-center pt-2 border-t border-app-border text-[11px] font-bold text-calm-blue">
                  <span>VELOCITY RATIO</span>
                  <span className="text-app-text">1.0x (Optimal)</span>
                </div>
              </div>
            </div>

            {/* Widget 2: Syllabus Target Flight Path */}
            <div className={`squircle-card overflow-hidden min-h-[300px] flex flex-col justify-between p-6 ${isDark ? "neon-glow-cyan" : ""}`}>
              <div className="squircle-tab-top relative">
                <button
                  onClick={() => handleDropdownToggle("widget2")}
                  className="h-6 w-6 flex items-center justify-center hover:bg-app-bg/50 rounded-full transition-all cursor-pointer"
                >
                  <MoreHorizontal className="h-4 w-4 text-calm-blue" />
                </button>
                {activeDropdown === "widget2" && (
                  <div className="absolute right-0 top-7 w-44 bg-card-bg border border-app-border rounded-xl shadow-lg p-2 z-10 text-xs text-app-text text-left">
                    <div className="px-2 py-1.5 font-bold border-b border-app-border mb-1">Flight Map Tracker</div>
                    <p className="px-2 py-1 text-[10px] text-calm-blue leading-relaxed">
                      Shows study track progress arc connecting start and destination dates.
                    </p>
                  </div>
                )}
              </div>

              <div className="text-left">
                <p className="text-xs font-bold text-calm-blue uppercase tracking-wider">Timeline Ingestion</p>
                <h2 className="text-3xl font-display font-black text-app-text mt-1 leading-none tracking-tight">
                  FLIGHT MAP
                </h2>
              </div>

              <div className="my-2 relative flex flex-col justify-center items-center">
                <div className="flex justify-between w-full text-xs font-extrabold text-app-text px-2">
                  <div className="text-left">
                    <p className="text-calm-blue font-bold text-[9px] uppercase">START</p>
                    <p className="text-md font-bold">{plan.start_date.split("-").slice(1).join("/")}</p>
                  </div>
                  <div className="text-right">
                    <p className="text-calm-blue font-bold text-[9px] uppercase">EXAM DESTINATION</p>
                    <p className="text-md font-bold">{plan.end_date.split("-").slice(1).join("/")}</p>
                  </div>
                </div>
                
                <div className="w-full h-16 relative flex items-center justify-center my-2">
                  <svg className="w-full h-12" viewBox="0 0 300 50">
                    <path 
                      d="M 10 25 Q 150 5 290 25" 
                      fill="none" 
                      stroke="var(--app-border)" 
                      strokeWidth="3"
                    />
                    <path 
                      d="M 10 25 Q 150 5 290 25" 
                      fill="none" 
                      stroke={neonCyan} 
                      strokeWidth="3"
                      strokeDasharray="300"
                      strokeDashoffset={300 - (300 * progressPercent) / 100}
                      style={{
                        transition: "stroke-dashoffset 1s ease",
                        filter: isDark ? `drop-shadow(0 0 3px ${neonCyan})` : "none"
                      }}
                    />
                    <circle 
                      cx={10 + (280 * progressPercent) / 100} 
                      cy={25 - (15 * Math.sin(Math.PI * (progressPercent / 100)))} 
                      r="5" 
                      fill={neonCyan} 
                      className="animate-pulse" 
                    />
                  </svg>
                </div>
              </div>

              <div className="flex justify-between items-center text-xs font-bold text-calm-blue pt-3 border-t border-app-border">
                <span>TIME HORIZON SPACER</span>
                <span className="text-app-text">{plan.plan_json.length} days</span>
              </div>
            </div>

            {/* Widget 3: Coverage Checklist */}
            <div className={`squircle-card overflow-hidden min-h-[300px] flex flex-col justify-between p-6 ${isDark ? "neon-glow-yellow" : ""}`}>
              <div className="squircle-tab-top relative">
                <button
                  onClick={() => handleDropdownToggle("widget3")}
                  className="h-6 w-6 flex items-center justify-center hover:bg-app-bg/50 rounded-full transition-all cursor-pointer"
                >
                  <MoreHorizontal className="h-4 w-4 text-calm-blue" />
                </button>
                {activeDropdown === "widget3" && (
                  <div className="absolute right-0 top-7 w-44 bg-card-bg border border-app-border rounded-xl shadow-lg p-2 z-10 text-xs text-app-text text-left">
                    <div className="px-2 py-1.5 font-bold border-b border-app-border mb-1">Node Index</div>
                    <p className="px-2 py-1 text-[10px] text-calm-blue leading-relaxed">
                      Check today's covered syllabus target checklist nodes.
                    </p>
                  </div>
                )}
              </div>

              <div className="text-left">
                <p className="text-xs font-bold text-calm-blue uppercase tracking-wider">Coverage Index</p>
                <h2 className="text-4xl font-display font-black text-app-text mt-2 leading-none tracking-tight">
                  {completedTopicsCount} <span className="text-lg font-bold text-calm-blue">/ {totalTopicsCount}</span>
                </h2>
                <p 
                  style={{ color: isDark ? neonYellow : "var(--color-primary-blue)" }} 
                  className="text-[10px] font-bold mt-1 tracking-wider uppercase"
                >
                  NODES COMPLETED
                </p>
              </div>

              <div className="space-y-1.5 my-3 text-left">
                {todayPlanDay?.topics && todayPlanDay.topics.length > 0 ? (
                  todayPlanDay.topics.slice(0, 3).map((topic) => {
                    const isDone = completedTopicIds.has(topic.id);
                    return (
                      <div key={topic.id} className="flex items-center space-x-2 text-[11px] font-bold text-app-text/90">
                        <div 
                          className="h-3.5 w-3.5 rounded-sm border flex items-center justify-center"
                          style={{
                            borderColor: isDone ? "transparent" : "var(--app-border)",
                            backgroundColor: isDone ? neonYellow : "var(--card-bg)",
                            color: isDone ? (isDark ? "black" : "white") : "transparent"
                          }}
                        >
                          {isDone && <span className="text-[9px]">✓</span>}
                        </div>
                        <span className={`truncate ${isDone ? "line-through text-app-text/40" : ""}`}>{topic.title}</span>
                      </div>
                    );
                  })
                ) : (
                  <p className="text-xs text-calm-blue italic">No active targets today. Focus on review.</p>
                )}
              </div>

              <div className="flex justify-between items-center text-xs font-bold text-calm-blue pt-3 border-t border-app-border">
                <span>SYSTEM SYNC STATUS</span>
                <span style={{ color: neonYellow }} className="font-extrabold">Active</span>
              </div>
            </div>

            {/* Widget 4: Adherence Stock Graph */}
            <div className={`squircle-card overflow-hidden min-h-[300px] flex flex-col justify-between p-6 ${isDark ? "neon-glow-yellow" : ""}`}>
              <div className="squircle-tab-top relative">
                <button
                  onClick={() => handleDropdownToggle("widget4")}
                  className="h-6 w-6 flex items-center justify-center hover:bg-app-bg/50 rounded-full transition-all cursor-pointer"
                >
                  <MoreHorizontal className="h-4 w-4 text-calm-blue" />
                </button>
                {activeDropdown === "widget4" && (
                  <div className="absolute right-0 top-7 w-44 bg-card-bg border border-app-border rounded-xl shadow-lg p-2 z-10 text-xs text-app-text text-left">
                    <div className="px-2 py-1.5 font-bold border-b border-app-border mb-1">Adherence Chart</div>
                    <p className="px-2 py-1 text-[10px] text-calm-blue leading-relaxed">
                      Plots cumulative progress milestones and daily study velocity ratios.
                    </p>
                  </div>
                )}
              </div>

              <div className="text-left">
                <p className="text-xs font-bold text-calm-blue uppercase tracking-wider">Adherence Dynamics</p>
                <h2 className="text-3xl font-display font-black text-app-text mt-1 leading-none tracking-tight">
                  {progressPercent}%
                </h2>
                <span 
                  className="inline-block mt-1 text-[10px] border px-2 py-0.5 rounded-full font-bold"
                  style={{
                    backgroundColor: isDark ? "rgba(225, 255, 0, 0.1)" : "rgba(31, 78, 121, 0.1)",
                    color: neonYellow,
                    borderColor: isDark ? "rgba(225, 255, 0, 0.2)" : "rgba(31, 78, 121, 0.2)"
                  }}
                >
                  ▲ Stable
                </span>
              </div>

              <div className="h-20 w-full my-1">
                <svg className="w-full h-full overflow-visible" viewBox="0 0 100 40" preserveAspectRatio="none">
                  <path
                    d="M 0,30 C 20,25 30,12 45,15 C 60,18 70,35 85,18 C 90,12 95,8 100,10"
                    fill="none"
                    stroke={neonYellow}
                    strokeWidth="2.5"
                    style={{
                      filter: isDark ? `drop-shadow(0 0 4px ${neonYellow})` : "none"
                    }}
                  />
                  <path
                    d="M 0,30 C 20,25 30,12 45,15 C 60,18 70,35 85,18 C 90,12 95,8 100,10 L 100,40 L 0,40 Z"
                    fill="url(#yellow-gradient)"
                    opacity="0.1"
                  />
                  <defs>
                    <linearGradient id="yellow-gradient" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="0%" stopColor={neonYellow} />
                      <stop offset="100%" stopColor={neonYellow} stopOpacity="0" />
                    </linearGradient>
                  </defs>
                </svg>
              </div>

              <div className="flex justify-between items-center text-xs font-bold text-calm-blue pt-3 border-t border-app-border">
                <span>STABILITY FACTOR</span>
                <span className="text-app-text">Optimal (1.0)</span>
              </div>
            </div>

            {/* Unified Double-Width Widget: FlipClock + Calibration Form */}
            <div className={`md:col-span-2 squircle-card overflow-hidden min-h-[300px] p-6 flex flex-col justify-between relative ${isDark ? "neon-glow-orange" : ""}`}>
              <div className="squircle-tab-top relative">
                <button
                  onClick={() => handleDropdownToggle("flipClockWidget")}
                  className="h-6 w-6 flex items-center justify-center hover:bg-app-bg/50 rounded-full transition-all cursor-pointer"
                >
                  <MoreHorizontal className="h-4 w-4 text-calm-blue" />
                </button>
                {activeDropdown === "flipClockWidget" && (
                  <div className="absolute right-0 top-7 w-48 bg-card-bg border border-app-border rounded-xl shadow-lg p-2 z-10 text-xs text-app-text text-left">
                    <div className="px-2 py-1 font-bold border-b border-app-border mb-1">Time Horizon Hub</div>
                    <button
                      onClick={() => {
                        setTimerSeconds(0);
                        setTimerActive(false);
                        setActiveDropdown(null);
                      }}
                      className="w-full text-left px-2 py-1 hover:bg-app-bg rounded-lg cursor-pointer"
                    >
                      Reset Stopwatch
                    </button>
                    <p className="px-2 py-1 text-[10px] text-calm-blue leading-relaxed">
                      Main dashboard clock and study stopwatch tracker.
                    </p>
                  </div>
                )}
              </div>

              {/* Grid content split into Clock (left) and Form (right) */}
              <div className="grid grid-cols-1 md:grid-cols-12 gap-6 items-center flex-1">
                {/* Left Side: FlipClock */}
                <div className="md:col-span-7 flex flex-col items-center justify-center border-b md:border-b-0 md:border-r border-app-border pb-6 md:pb-0 md:pr-6 h-full text-center">
                  <p className="text-xs font-bold text-calm-blue uppercase tracking-wider mb-2">SYSTEM TIME HORIZON</p>
                  <div className="scale-90 md:scale-100 origin-center">
                    <FlipClock />
                  </div>
                  <span className="text-[10px] text-calm-blue font-semibold mt-3">
                    REAL-TIME PACING COUNTER
                  </span>
                </div>

                {/* Right Side: Calibration Form & Stopwatch controls */}
                <div className="md:col-span-5 flex flex-col justify-between h-full pt-4 md:pt-0 pl-0 md:pl-2 text-left">
                  <div>
                    <p className="text-xs font-bold text-calm-blue uppercase tracking-wider">Calibration Form</p>
                    <div className="flex justify-between items-baseline mt-0.5 mb-3">
                      <h2 className="text-xl font-display font-black text-app-text uppercase tracking-tight">
                        LOG LOGS
                      </h2>
                      <span className="text-xs font-mono font-bold text-calm-blue bg-app-bg px-2 py-0.5 rounded border border-app-border">
                        {formatTime(timerSeconds)}
                      </span>
                    </div>
                  </div>

                  <form onSubmit={handleCheckInSubmit} className="space-y-3">
                    <div className="flex items-center justify-between gap-2">
                      <div className="w-1/2 flex items-center bg-app-bg border border-app-border rounded-lg px-2 py-1 gap-1">
                        <input
                          type="number"
                          step="0.1"
                          value={hoursStudied}
                          onChange={(e) => setHoursStudied(e.target.value)}
                          className="w-full bg-transparent text-xs text-app-text focus:outline-hidden"
                          placeholder="Hrs"
                        />
                        {timerSeconds > 0 && (
                          <button
                            type="button"
                            onClick={() => {
                              const calculatedHrs = (timerSeconds / 3600).toFixed(2);
                              setHoursStudied(calculatedHrs);
                            }}
                            className="text-[9px] font-extrabold text-neon-orange hover:underline cursor-pointer uppercase shrink-0"
                          >
                            Use Time
                          </button>
                        )}
                      </div>
                      
                      <div className="flex items-center space-x-2">
                        <button
                          type="button"
                          onClick={() => setTimerActive(!timerActive)}
                          className="h-6 w-6 rounded-full bg-app-bg flex items-center justify-center border border-app-border hover:bg-card-bg transition-colors cursor-pointer"
                        >
                          {timerActive ? (
                            <Pause className="h-3 w-3" style={{ color: neonOrange }} />
                          ) : (
                            <Play className="h-3 w-3 fill-current" style={{ color: neonOrange }} />
                          )}
                        </button>
                        <button
                          type="submit"
                          style={{ backgroundColor: neonOrange }}
                          className="h-7 px-3 rounded-lg text-[10px] font-black text-white uppercase tracking-wider shadow-md hover:opacity-90 transition-all border border-transparent cursor-pointer"
                        >
                          LOG
                        </button>
                      </div>
                    </div>

                    <input
                      type="text"
                      value={checkInNote}
                      onChange={(e) => setCheckInNote(e.target.value)}
                      placeholder={timerActive ? "What are you studying now?" : "Study notes..."}
                      className="w-full bg-app-bg border border-app-border rounded-lg py-1.5 px-3 text-[11px] text-app-text focus:outline-hidden"
                    />
                  </form>

                  <div className="flex items-end justify-center space-x-1 h-5 pt-2 border-t border-app-border mt-3">
                    {[3, 5, 2, 7, 4, 6, 8, 3, 5, 2, 6, 7].map((h, i) => (
                      <div
                        key={i}
                        className={`w-1.5 rounded-full transition-all duration-300 ${
                          timerActive ? "equalizer-bar-animated" : ""
                        }`}
                        style={{
                          height: `${h * 1.5 + (formLoading ? Math.random() * 4 : 0)}px`,
                          backgroundColor: neonOrange,
                          opacity: timerActive ? 1 : 0.4,
                          animationDelay: `${i * -0.15}s`,
                        }}
                      />
                    ))}
                  </div>
                </div>
              </div>
            </div>

          </div>

          {/* 3. Study Timeline / Connecting Branch Schedule below widgets */}
          <div className="squircle-card p-6 text-left">
            <h2 className="text-xl font-bold text-app-text mb-6 flex items-center space-x-2">
              <Calendar className="h-5.5 w-5.5 text-calm-blue" />
              <span>Diagnostic Learning Roadmap</span>
            </h2>

            <div className="space-y-4">
              {plan.plan_json.map((day: StudyPlanDay) => {
                const isDayToday = day.date === todayStr;
                const dayTopics = day.topics || [];
                const allTopicsCompleted = dayTopics.length > 0 && dayTopics.every((t) => completedTopicIds.has(t.id));

                return (
                  <div
                    key={day.day_number}
                    className="rounded-2xl border text-left transition-all duration-300"
                    style={{
                      backgroundColor: isDayToday
                        ? (isDark ? "#1E1E22" : "#FAF9F5")
                        : allTopicsCompleted && dayTopics.length > 0
                        ? "rgba(16, 185, 129, 0.05)"
                        : "var(--card-bg)",
                      borderColor: isDayToday
                        ? neonCyan
                        : "var(--app-border)",
                      boxShadow: isDayToday && isDark
                        ? `0 0 12px rgba(0, 240, 255, 0.08)`
                        : "none"
                    }}
                  >
                    <div 
                      onClick={() => toggleDayCollapse(day.day_number)}
                      className="p-4 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 cursor-pointer hover:bg-app-bg/20 transition-colors select-none"
                    >
                      <div>
                        <div className="flex items-center space-x-2">
                          <span
                            className="text-[10px] font-extrabold px-2 py-0.5 rounded-md uppercase tracking-wider"
                            style={{
                              backgroundColor: isDayToday 
                                ? neonCyan 
                                : allTopicsCompleted && dayTopics.length > 0 
                                ? "rgba(16, 185, 129, 0.1)" 
                                : "var(--app-bg)",
                              color: isDayToday 
                                ? (isDark ? "black" : "white") 
                                : allTopicsCompleted && dayTopics.length > 0 
                                ? "#059669" 
                                : "var(--app-text)"
                            }}
                          >
                            Day {day.day_number}
                          </span>
                          <span className="text-xs font-bold text-calm-blue">{day.date}</span>
                          
                          {isDayToday && (
                            <span 
                              className="text-[9px] font-black px-1.5 py-0.5 rounded border animate-pulse"
                              style={{
                                backgroundColor: `rgba(255, 92, 0, 0.1)`,
                                color: neonOrange,
                                borderColor: `rgba(255, 92, 0, 0.2)`
                              }}
                            >
                              ACTIVE
                            </span>
                          )}

                          {/* Collapsible toggle icon */}
                          <span className="text-calm-blue text-[10px] font-bold">
                            {collapsedDays[day.day_number] ? "[+]" : "[-]"}
                          </span>
                        </div>
                        {day.notes && (
                          <p className="text-xs font-semibold text-app-text/80 mt-1.5 leading-relaxed">
                            {day.notes}
                          </p>
                        )}
                      </div>

                      <div className="shrink-0 flex items-center space-x-2">
                        {day.is_review ? (
                          <span 
                            className="text-[10px] px-2.5 py-1 rounded-md font-black uppercase tracking-wider"
                            style={{
                              backgroundColor: neonYellow,
                              color: isDark ? "black" : "white"
                            }}
                          >
                            Revision Focus
                          </span>
                        ) : dayTopics.length > 0 ? (
                          <div className="flex items-center space-x-2.5 text-xs font-semibold">
                            <span className={allTopicsCompleted ? "text-emerald-500" : "text-calm-blue"}>
                              {dayTopics.filter((t) => completedTopicIds.has(t.id)).length} / {dayTopics.length} done
                            </span>
                            <div className="w-16 h-2 bg-app-bg rounded-full overflow-hidden border border-app-border">
                              <div
                                className="h-full rounded-full transition-all duration-300"
                                style={{
                                  width: `${
                                    dayTopics.length > 0
                                      ? (dayTopics.filter((t) => completedTopicIds.has(t.id)).length / dayTopics.length) * 100
                                      : 0
                                    }%`,
                                  backgroundColor: allTopicsCompleted ? "#10B981" : neonCyan
                                }}
                              />
                            </div>
                          </div>
                        ) : (
                          <span className="text-[10px] text-calm-blue italic">No targets</span>
                        )}
                      </div>
                    </div>

                    {/* Day Topics Subpanel */}
                    {dayTopics.length > 0 && !collapsedDays[day.day_number] && (
                      <div className="border-t border-app-border px-4 py-3 bg-app-bg/25 space-y-2">
                        {dayTopics.map((topic) => {
                          const isTopicDone = completedTopicIds.has(topic.id);
                          return (
                            <div 
                              key={topic.id} 
                              onClick={() => handleToggleRoadmapTopic(topic.id, day.date)}
                              className="flex items-start space-x-2.5 text-xs text-app-text/90 cursor-pointer hover:opacity-85 select-none"
                            >
                              <div className="mt-0.5 shrink-0">
                                {isTopicDone ? (
                                  <button className="text-emerald-500 pointer-events-none" title="Completed">
                                    <CheckCircle className="h-4 w-4" />
                                  </button>
                                ) : (
                                  <button 
                                    className="h-4 w-4 rounded-sm border border-app-border bg-card-bg cursor-pointer hover:bg-app-bg flex items-center justify-center text-emerald-500 text-[10px] font-bold" 
                                    title="Click to complete topic"
                                  />
                                )}
                              </div>
                              <div className="leading-tight text-left">
                                <span className={isTopicDone ? "line-through text-app-text/40" : ""}>
                                  {topic.title}
                                </span>
                              </div>
                            </div>
                          );
                        })}
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          </div>
        </>
      )}

      {/* 4. Active Logs History */}
      {activeCategory === "Check-ins" && (
        <div className="squircle-card p-6 max-w-3xl mx-auto text-left">
          <h2 className="text-xl font-bold text-app-text mb-6 flex items-center space-x-2">
            <FileText className="h-5 w-5 text-calm-blue" />
            <span>Diagnostic Progress Logs</span>
          </h2>

          <div className="space-y-4">
            {progressHistory.length > 0 ? (
              progressHistory.map((log) => (
                <div key={log.id} className="bg-app-bg/40 border border-app-border rounded-2xl p-5 shadow-2xs">
                  <div className="flex justify-between items-center pb-3 border-b border-app-border">
                    <span className="text-xs font-extrabold text-app-text">{log.date}</span>
                    <span className="text-[10px] font-bold bg-card-bg text-app-text border border-app-border px-2.5 py-0.5 rounded-full">
                      {log.completed_hours} hours completed
                    </span>
                  </div>
                  <p className="text-xs text-app-text/90 mt-3 italic leading-relaxed">
                    "{log.check_in_note || "No comments log entry."}"
                  </p>
                  {log.completed_topics && log.completed_topics.length > 0 && (
                    <div className="mt-3 flex items-center text-[10px] font-bold text-emerald-600">
                      <CheckCircle className="h-4 w-4 mr-1 text-emerald-500" />
                      <span>Completed {log.completed_topics.length} topic nodes successfully</span>
                    </div>
                  )}
                </div>
              ))
            ) : (
              <p className="text-xs text-calm-blue italic py-8 text-center bg-card-bg border border-app-border rounded-2xl">
                No progress records saved yet.
              </p>
            )}
          </div>
        </div>
      )}

      {/* 5. Adaptive Settings / Replan Options */}
      {activeCategory === "Settings" && (
        <div className="squircle-card p-6 max-w-xl mx-auto text-left space-y-4">
          <h2 className="text-xl font-bold text-app-text flex items-center space-x-2">
            <RefreshCw className="h-5 w-5 text-calm-blue" />
            <span>Calibrate Adaptive Pacing</span>
          </h2>
          <p className="text-xs text-calm-blue leading-relaxed">
            Specify a custom date to trigger a manual recalculation of all remaining study topics.
          </p>
          <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-4 pt-2">
            <input
              type="date"
              value={replanDate}
              onChange={(e) => setReplanDate(e.target.value)}
              className="bg-app-bg border border-app-border rounded-xl py-2 px-4 text-xs text-app-text focus:outline-hidden"
            />
            <button
              onClick={handleManualReplan}
              disabled={replanLoading}
              style={{ backgroundColor: neonOrange }}
              className="flex-1 text-white rounded-xl py-2 px-4 text-xs font-bold transition-all shadow-md cursor-pointer hover:opacity-90"
            >
              {replanLoading ? "Calibrating..." : "Calibrate Adaptive Replan"}
            </button>
          </div>
        </div>
      )}

      {/* 6. Neural Assist — AI Chat Panel */}
      {activeCategory === "AI Assistant" && (
        <div className="squircle-card p-6 max-w-3xl mx-auto text-left flex flex-col" style={{ minHeight: "520px" }}>
          {/* Header */}
          <h2 className="text-xl font-bold text-app-text mb-1 flex items-center space-x-2">
            <Sparkles className="h-5 w-5 text-calm-blue" />
            <span>Neural Assist</span>
          </h2>
          <p className="text-xs text-calm-blue mb-5 leading-relaxed">
            Ask anything about your syllabus, request a quiz, get topic summaries, or analyze your progress.
          </p>

          {/* Chat messages */}
          <div
            className="flex-1 overflow-y-auto space-y-4 mb-5 pr-1"
            style={{ maxHeight: "340px" }}
          >
            {aiMessages.length === 0 && (
              <div className="text-center py-10">
                <Sparkles className="h-8 w-8 text-calm-blue/30 mx-auto mb-3" />
                <p className="text-xs text-calm-blue/60 font-semibold uppercase tracking-wider">
                  Start a conversation
                </p>
                <div className="mt-4 flex flex-wrap justify-center gap-2">
                  {[
                    "Quiz me on today's topics",
                    "Summarize my next topic",
                    "How am I doing?",
                    "Replan from today"
                  ].map((suggestion) => (
                    <button
                      key={suggestion}
                      onClick={() => setAiInput(suggestion)}
                      className="text-[10px] font-bold px-3 py-1.5 rounded-full border border-app-border bg-app-bg hover:bg-card-bg transition-colors cursor-pointer text-app-text/70 hover:text-app-text"
                    >
                      {suggestion}
                    </button>
                  ))}
                </div>
              </div>
            )}

            {aiMessages.map((msg, idx) => (
              <div
                key={idx}
                className={`flex ${
                  msg.role === "user" ? "justify-end" : "justify-start"
                }`}
              >
                <div
                  className={`max-w-[85%] rounded-2xl px-4 py-3 text-xs leading-relaxed font-medium ${
                    msg.role === "user"
                      ? "bg-app-text text-card-bg rounded-tr-sm"
                      : "bg-app-bg border border-app-border text-app-text rounded-tl-sm"
                  }`}
                  style={{ whiteSpace: "pre-wrap" }}
                >
                  {msg.role === "assistant" && (
                    <div className="flex items-center gap-1 mb-2 text-calm-blue">
                      <Sparkles className="h-2.5 w-2.5" />
                      <span className="text-[9px] font-bold uppercase tracking-wider">Syllabot</span>
                    </div>
                  )}
                  {msg.content}
                </div>
              </div>
            ))}

            {aiLoading && (
              <div className="flex justify-start">
                <div className="bg-app-bg border border-app-border rounded-2xl rounded-tl-sm px-4 py-3 text-xs">
                  <div className="flex items-center gap-2 text-calm-blue">
                    <Loader2 className="h-3 w-3 animate-spin" />
                    <span className="text-[10px] font-bold uppercase tracking-wider">Thinking...</span>
                  </div>
                </div>
              </div>
            )}

            {aiError && (
              <div className="flex justify-start">
                <div className="bg-app-bg border border-app-border rounded-2xl rounded-tl-sm px-4 py-3 text-xs text-app-text/70">
                  <div className="flex items-center gap-1.5 mb-1 text-calm-blue">
                    <AlertCircle className="h-3 w-3" />
                    <span className="text-[9px] font-bold uppercase">Notice</span>
                  </div>
                  {aiError}
                </div>
              </div>
            )}

            <div ref={aiChatEndRef} />
          </div>

          {/* Input form */}
          <form
            id="ai-chat-form"
            onSubmit={async (e) => {
              e.preventDefault();
              const msg = aiInput.trim();
              if (!msg || aiLoading) return;

              const userMsg: AIChatMessage = { role: "user", content: msg };
              setAiMessages((prev) => [...prev, userMsg]);
              setAiInput("");
              setAiLoading(true);
              setAiError(null);

              try {
                const res = await aiApi.chat(msg, aiConversationId);
                setAiMessages((prev) => [
                  ...prev,
                  { role: "assistant", content: res.response },
                ]);
                // Scroll to bottom
                setTimeout(() => aiChatEndRef.current?.scrollIntoView({ behavior: "smooth" }), 50);
              } catch (err: any) {
                const errMsg =
                  err?.message?.includes("503") || err?.message?.includes("Service Unavailable")
                    ? "🔑 AI features aren't configured yet. Add GEMINI_API_KEY or GROQ_API_KEY to your .env file to activate Neural Assist."
                    : err?.message || "Something went wrong. Please try again.";
                setAiError(errMsg);
              } finally {
                setAiLoading(false);
              }
            }}
            className="flex items-center gap-3 border-t border-app-border pt-4"
          >
            <input
              id="ai-chat-input"
              type="text"
              value={aiInput}
              onChange={(e) => setAiInput(e.target.value)}
              disabled={aiLoading}
              placeholder="Ask anything... quiz me, summarize a topic, how am I doing?"
              className="flex-1 bg-app-bg border border-app-border rounded-xl py-2.5 px-4 text-xs text-app-text focus:outline-none placeholder:text-app-text/40 disabled:opacity-50"
            />
            <button
              id="ai-chat-submit"
              type="submit"
              disabled={aiLoading || !aiInput.trim()}
              className="h-9 w-9 rounded-xl bg-app-text flex items-center justify-center text-card-bg hover:opacity-85 transition-all disabled:opacity-30 cursor-pointer shrink-0"
            >
              {aiLoading ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <ChevronRight className="h-4 w-4" />
              )}
            </button>
          </form>
        </div>
      )}

    </div>
  );
}
