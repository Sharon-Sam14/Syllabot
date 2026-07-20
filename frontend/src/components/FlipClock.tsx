"use client";

import React, { useEffect, useState } from "react";

interface FlipCardProps {
  current: number;
  previous: number;
}

const FlipCard = ({ current, previous }: FlipCardProps) => {
  const [isFlipping, setIsFlipping] = useState(false);

  useEffect(() => {
    if (current !== previous) {
      setIsFlipping(true);
      const timer = setTimeout(() => {
        setIsFlipping(false);
      }, 550);
      return () => clearTimeout(timer);
    }
  }, [current, previous]);

  return (
    <div className="flip-card-container">
      {/* Top half static (always shows current value) */}
      <div className="flip-half up">
        <div className="inn">{current}</div>
      </div>

      {/* Bottom half static (shows previous value when flipping, current value when static) */}
      <div className="flip-half down">
        <div className="inn">{isFlipping ? previous : current}</div>
      </div>

      {/* Flipping card top-to-bottom */}
      {isFlipping && (
        <div className="flip-card-fold flip-anim">
          <div className="flip-half up fold-front">
            <div className="inn">{previous}</div>
          </div>
          <div className="flip-half down fold-back">
            <div className="inn">{current}</div>
          </div>
        </div>
      )}

      {/* Center divider line */}
      <div className="center-divider" />

      <style jsx>{`
        .flip-card-container {
          position: relative;
          --flip-w: 54px;
          --flip-h: 80px;
          --flip-fs: 52px;
          --flip-lh: 80px;
          width: var(--flip-w);
          height: var(--flip-h);
          perspective: 300px;
          box-shadow: 0 4px 10px rgba(0, 0, 0, 0.4);
          border-radius: 8px;
        }

        @media (max-width: 640px) {
          .flip-card-container {
            --flip-w: 36px;
            --flip-h: 56px;
            --flip-fs: 34px;
            --flip-lh: 56px;
          }
        }

        .flip-half {
          position: absolute;
          left: 0;
          width: 100%;
          height: 50%;
          overflow: hidden;
          backface-visibility: hidden;
        }

        .up {
          top: 0;
          border-top-left-radius: 8px;
          border-top-right-radius: 8px;
        }

        .down {
          bottom: 0;
          border-bottom-left-radius: 8px;
          border-bottom-right-radius: 8px;
        }

        .inn {
          position: absolute;
          left: 0;
          width: 100%;
          height: var(--flip-h);
          background-color: #15161b;
          border: 1px solid rgba(255, 255, 255, 0.08);
          border-radius: 8px;
          font-family: var(--font-comfortaa), ui-sans-serif, system-ui, sans-serif;
          font-size: var(--flip-fs);
          font-weight: 800;
          color: #ffffff;
          line-height: var(--flip-lh);
          text-align: center;
        }

        .up .inn {
          top: 0;
        }

        .down .inn {
          bottom: 0;
        }

        /* Flipping fold container */
        .flip-card-fold {
          position: absolute;
          left: 0;
          top: 0;
          width: 100%;
          height: 50%;
          transform-origin: bottom center;
          transform-style: preserve-3d;
          z-index: 5;
        }

        .fold-front {
          position: absolute;
          left: 0;
          top: 0;
          width: 100%;
          height: 100%;
          overflow: hidden;
          backface-visibility: hidden;
          z-index: 2;
        }

        .fold-back {
          position: absolute;
          left: 0;
          top: 0;
          width: 100%;
          height: 100%;
          overflow: hidden;
          backface-visibility: hidden;
          transform: rotateX(180deg);
          z-index: 1;
        }

        .flip-anim {
          animation: flip-keyframes 0.55s cubic-bezier(0.25, 0.46, 0.45, 0.94) forwards;
        }

        @keyframes flip-keyframes {
          0% {
            transform: rotateX(0deg);
          }
          100% {
            transform: rotateX(-180deg);
          }
        }

        .center-divider {
          position: absolute;
          left: 0;
          top: 50%;
          width: 100%;
          height: 2px;
          background: #000000;
          z-index: 10;
          opacity: 0.9;
        }
      `}</style>
    </div>
  );
};

const FlipDigit = ({ val }: { val: number }) => {
  const [current, setCurrent] = useState(val);
  const [previous, setPrevious] = useState(val);

  useEffect(() => {
    if (val !== current) {
      setPrevious(current);
      setCurrent(val);
    }
  }, [val, current]);

  return <FlipCard current={current} previous={previous} />;
};

export default function FlipClock() {
  const [time, setTime] = useState<Date | null>(null);

  useEffect(() => {
    setTime(new Date());
    const timer = setInterval(() => {
      setTime(new Date());
    }, 1000);
    return () => clearInterval(timer);
  }, []);

  if (!time) {
    return (
      <div className="flex items-center space-x-1 font-mono text-xl text-calm-blue">
        <span>Loading clock...</span>
      </div>
    );
  }

  const hrs = time.getHours();
  const mins = time.getMinutes();
  const secs = time.getSeconds();

  const h1 = Math.floor(hrs / 10);
  const h2 = hrs % 10;
  const m1 = Math.floor(mins / 10);
  const m2 = mins % 10;
  const s1 = Math.floor(secs / 10);
  const s2 = secs % 10;

  return (
    <div className="flex items-center space-x-2 sm:space-x-4 select-none">
      {/* Hours */}
      <div className="flex space-x-1 sm:space-x-1.5">
        <FlipDigit val={h1} />
        <FlipDigit val={h2} />
      </div>

      <span className="text-2xl sm:text-4xl font-black text-app-text animate-pulse">:</span>

      {/* Minutes */}
      <div className="flex space-x-1 sm:space-x-1.5">
        <FlipDigit val={m1} />
        <FlipDigit val={m2} />
      </div>

      <span className="text-2xl sm:text-4xl font-black text-app-text animate-pulse">:</span>

      {/* Seconds */}
      <div className="flex space-x-1 sm:space-x-1.5">
        <FlipDigit val={s1} />
        <FlipDigit val={s2} />
      </div>
    </div>
  );
}
