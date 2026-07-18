import React, { useState } from "react";
import { syllabiApi, plansApi, StudyPlanResponse } from "../lib/api";
import { Calendar, Upload, AlertCircle, Sparkles, Loader2, FileText } from "lucide-react";

interface IntakeScreenProps {
  onPlanCreated: (plan: StudyPlanResponse) => void;
}

const SAMPLE_SYLLABUS = `Unit 1: Introduction to Python
- Basic Syntax & Data Types (Variables, Integers, Strings)
- Control Flow (If-Else conditions, Logical operators)
- Loops & Iteration (For loops, While loops, Break/Continue)

Unit 2: Object-Oriented Programming (OOP)
- Classes and Objects (Attributes, Methods, self keyword)
- Inheritance and Polymorphism (Parent/Child classes, Method overriding)

Unit 3: Web Foundations
- HTTP Protocol (Requests, Responses, Headers, Status Codes)
- Basic HTML & CSS structure`;

const COURSE_TEMPLATES = {
  cs101: `Unit 1: Fundamentals of Programming
- Variables, Data Types & Operators
- Conditional Control Flow (if-else)
- Iteration & Loops (for, while)
- Functions & Scope

Unit 2: Object-Oriented Programming (OOP)
- Classes, Objects & Attributes
- Inheritance & Polymorphism
- Encapsulation & Abstraction

Unit 3: Data Structures & Algorithms
- Arrays, Lists & Dictionaries
- Sorting & Searching Algorithms
- Big O Notation & Time Complexity`,

  physics: `Unit 1: Classical Mechanics
- Kinematics & Laws of Motion
- Work, Energy & Power
- Linear Momentum & Rotational Motion

Unit 2: Thermodynamics
- Temperature & Thermal Expansion
- First & Second Law of Thermodynamics
- Heat Engines & Entropy

Unit 3: Electromagnetism
- Electric Fields & Coulomb's Law
- Magnetic Force & Induction
- Maxwell's Equations & Electromagnetic Waves`,

  marketing: `Unit 1: Search Engine Optimization (SEO)
- Keyword Research & Analytics
- On-Page & Off-Page SEO Strategies
- Technical Audit & Site Indexing

Unit 2: Social Media Marketing (SMM)
- Content Design & Scheduling
- Community Management & Brand Building
- Paid Ads Campaign Tuning (Meta, LinkedIn)

Unit 3: Email Marketing & Conversion
- List Segmentation & A/B Testing
- Copywriting & Subject Line Tuning
- Funnel Optimization`,

  datascience: `Unit 1: Statistical Analysis
- Probability Distributions
- Hypothesis Testing & Confidence Intervals
- Correlation & Regression Analysis

Unit 2: Data Preprocessing
- Cleaning Missing Values
- Feature Scaling & Normalization
- Dimensionality Reduction (PCA)

Unit 3: Machine Learning Models
- Supervised Learning: Classification & Regression
- Unsupervised Learning: Clustering & K-Means
- Model Evaluation Metrics (Accuracy, F1, ROC)`
};

export default function IntakeScreen({ onPlanCreated }: IntakeScreenProps) {
  const [rawText, setRawText] = useState("");
  const [startDate, setStartDate] = useState(
    new Date().toISOString().split("T")[0]
  );
  const [endDate, setEndDate] = useState(() => {
    const defaultEnd = new Date();
    defaultEnd.setDate(defaultEnd.getDate() + 7); // Default 7 days plan
    return defaultEnd.toISOString().split("T")[0];
  });
  const [loading, setLoading] = useState(false);
  const [loadingStep, setLoadingStep] = useState<string>("");
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    if (!rawText.trim()) {
      setError("Please select a template or paste your syllabus content.");
      return;
    }

    if (new Date(startDate) > new Date(endDate)) {
      setError("The start date must be on or before the end date.");
      return;
    }

    setLoading(true);
    try {
      setLoadingStep("Reading and parsing your syllabus hierarchy...");
      const syllabus = await syllabiApi.ingest(rawText);

      setLoadingStep("Distributing topics and generating study calendar...");
      const plan = await plansApi.create({
        syllabus_id: syllabus.id,
        start_date: startDate,
        end_date: endDate,
      });

      onPlanCreated(plan);
    } catch (err: any) {
      console.error(err);
      setError(err.message || "An error occurred while generating the plan.");
    } finally {
      setLoading(false);
      setLoadingStep("");
    }
  };

  return (
    <div className="max-w-4xl mx-auto px-4 py-8 sm:px-6 lg:px-8 animate-fade-in">
      <div className="text-center mb-8">
        <h1 className="text-3xl font-display font-extrabold text-app-text tracking-tight sm:text-4xl">
          Create a New Study Plan
        </h1>
        <p className="mt-2 text-md text-calm-blue max-w-lg mx-auto">
          Choose a pre-defined course template or paste your syllabus topics. We'll build a custom day-by-day adaptive path.
        </p>
      </div>

      <div className="bg-card-bg border border-app-border rounded-2xl shadow-xs overflow-hidden relative transition-colors duration-300">
        <div className="absolute top-0 left-0 right-0 h-1 bg-gradient-to-r from-primary-blue to-calm-blue" />
        
        {loading ? (
          <div className="py-24 px-6 flex flex-col items-center justify-center text-center">
            <div className="relative">
              <div className="h-16 w-16 rounded-2xl bg-gradient-to-tr from-primary-blue to-progress-teal opacity-10 absolute animate-ping" />
              <div className="h-16 w-16 rounded-2xl bg-app-bg border border-app-border flex items-center justify-center text-primary-blue relative animate-pulse shadow-xs">
                <Sparkles className="h-8 w-8 text-primary-blue" />
              </div>
            </div>
            <h3 className="mt-6 text-lg font-bold text-app-text">
              Generating Your Adaptive Plan
            </h3>
            <p className="mt-2 text-sm text-calm-blue flex items-center justify-center max-w-sm">
              <Loader2 className="animate-spin h-4 w-4 mr-2 text-primary-blue" />
              {loadingStep}
            </p>
          </div>
        ) : (
          <form onSubmit={handleSubmit} className="p-6 sm:p-8 space-y-6">
            {error && (
              <div className="rounded-xl bg-red-50/10 border border-red-500/20 p-4 flex items-start space-x-2.5">
                <AlertCircle className="h-5 w-5 text-red-500 shrink-0 mt-0.5" />
                <span className="text-sm text-red-500 font-medium">{error}</span>
              </div>
            )}

            <div className="space-y-2 text-left">
              <div className="flex flex-col sm:flex-row sm:justify-between sm:items-center gap-3">
                <label className="block text-xs font-bold text-app-text/80 uppercase tracking-wider">
                  Syllabus Ingestion
                </label>
                
                {/* Course Template Selection Dropdown */}
                <div className="flex items-center space-x-2.5">
                  <select
                    onChange={(e) => {
                      const val = e.target.value;
                      if (val && val in COURSE_TEMPLATES) {
                        setRawText(COURSE_TEMPLATES[val as keyof typeof COURSE_TEMPLATES]);
                      } else if (val === "custom") {
                        setRawText("");
                      }
                    }}
                    className="text-xs bg-app-bg border border-app-border rounded-lg px-2.5 py-1.5 text-app-text focus:outline-hidden focus:ring-2 focus:ring-primary-blue/20 cursor-pointer"
                  >
                    <option value="">Choose a Course Template...</option>
                    <option value="cs101">Computer Science 101</option>
                    <option value="physics">Introduction to Physics</option>
                    <option value="marketing">Digital Marketing Basics</option>
                    <option value="datascience">Data Science Foundations</option>
                    <option value="custom">Custom (Clear / Paste own)</option>
                  </select>

                  <button
                    type="button"
                    onClick={() => setRawText(SAMPLE_SYLLABUS)}
                    className="text-xs font-semibold text-primary-blue hover:text-primary-navy flex items-center space-x-1 hover:underline cursor-pointer bg-app-bg px-2.5 py-1.5 rounded-lg border border-app-border shadow-2xs"
                  >
                    <FileText className="h-3.5 w-3.5" />
                    <span>Sample</span>
                  </button>
                </div>
              </div>
              <textarea
                value={rawText}
                onChange={(e) => setRawText(e.target.value)}
                rows={10}
                required
                className="block w-full px-4 py-3 bg-app-bg border border-app-border rounded-xl text-app-text placeholder-calm-blue/40 focus:outline-hidden focus:ring-2 focus:ring-primary-blue/20 focus:border-primary-blue transition-all text-sm font-mono leading-relaxed"
                placeholder={`Select a template above, or paste your syllabus content here. For example:\nUnit 1: Intro\n- Basic variables\n- Dynamic loops\n\nUnit 2: OOP\n- Classes and objects`}
              />
              <p className="text-[11px] text-calm-blue">
                Tip: You can modify templates freely or select "Custom" to paste your own coursework directly.
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 pt-2 text-left">
              <div className="space-y-2">
                <label className="block text-xs font-bold text-app-text/80 uppercase tracking-wider">
                  Plan Start Date
                </label>
                <div className="relative rounded-xl shadow-xs">
                  <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-calm-blue/70">
                    <Calendar className="h-5 w-5" />
                  </div>
                  <input
                    type="date"
                    required
                    value={startDate}
                    onChange={(e) => setStartDate(e.target.value)}
                    className="block w-full pl-11 pr-4 py-2.5 bg-app-bg border border-app-border rounded-xl text-app-text focus:outline-hidden focus:ring-2 focus:ring-primary-blue/20 focus:border-primary-blue transition-all text-sm"
                  />
                </div>
              </div>

              <div className="space-y-2">
                <label className="block text-xs font-bold text-app-text/80 uppercase tracking-wider">
                  Plan End Date (Exam Target)
                </label>
                <div className="relative rounded-xl shadow-xs">
                  <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-calm-blue/70">
                    <Calendar className="h-5 w-5" />
                  </div>
                  <input
                    type="date"
                    required
                    value={endDate}
                    onChange={(e) => setEndDate(e.target.value)}
                    className="block w-full pl-11 pr-4 py-2.5 bg-app-bg border border-app-border rounded-xl text-app-text focus:outline-hidden focus:ring-2 focus:ring-primary-blue/20 focus:border-primary-blue transition-all text-sm"
                  />
                </div>
              </div>
            </div>

            <div className="pt-4 border-t border-app-border flex justify-end">
              <button
                type="submit"
                className="flex items-center space-x-2 py-3 px-6 border border-transparent rounded-xl shadow-sm text-sm font-semibold text-white bg-gradient-to-r from-primary-blue to-calm-blue hover:from-primary-navy hover:to-primary-blue focus:outline-hidden focus:ring-2 focus:ring-offset-2 focus:ring-primary-blue transition-all cursor-pointer"
              >
                <Upload className="h-4.5 w-4.5" />
                <span>Create Study Calendar</span>
              </button>
            </div>
          </form>
        )}
      </div>
    </div>
  );
}
