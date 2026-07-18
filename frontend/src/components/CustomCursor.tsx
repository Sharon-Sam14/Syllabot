"use client";

import React, { useEffect, useRef } from "react";

export default function CustomCursor() {
  const bigBallRef = useRef<HTMLDivElement>(null);
  const smallBallRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (typeof window === "undefined") return;

    const bigBall = bigBallRef.current;
    const smallBall = smallBallRef.current;
    if (!bigBall || !smallBall) return;

    let mouseX = 0;
    let mouseY = 0;
    let bigX = 0;
    let bigY = 0;
    let smallX = 0;
    let smallY = 0;

    const handleMouseMove = (e: MouseEvent) => {
      mouseX = e.clientX;
      mouseY = e.clientY;
    };

    window.addEventListener("mousemove", handleMouseMove);

    // Smooth trailing animation using Linear Interpolation (lerp)
    let animationFrameId: number;
    const updatePosition = () => {
      bigX += (mouseX - bigX) * 0.15;
      bigY += (mouseY - bigY) * 0.15;

      smallX += (mouseX - smallX) * 0.3;
      smallY += (mouseY - smallY) * 0.3;

      if (bigBall) {
        bigBall.style.transform = `translate3d(${bigX - 15}px, ${bigY - 15}px, 0)`;
      }
      if (smallBall) {
        smallBall.style.transform = `translate3d(${smallX - 5}px, ${smallY - 5}px, 0)`;
      }

      animationFrameId = requestAnimationFrame(updatePosition);
    };

    updatePosition();

    // Hover Scaling effects for clickables and links
    const handleMouseEnter = () => {
      if (bigBall) {
        bigBall.style.width = "40px";
        bigBall.style.height = "40px";
        bigBall.style.borderRadius = "50%";
        bigBall.style.transition = "width 0.2s ease, height 0.2s ease";
      }
    };

    const handleMouseLeave = () => {
      if (bigBall) {
        bigBall.style.width = "30px";
        bigBall.style.height = "30px";
        bigBall.style.transition = "width 0.2s ease, height 0.2s ease";
      }
    };

    const addHoverListeners = () => {
      const hoverables = document.querySelectorAll(
        "a, button, input, select, textarea, [role='button'], .hoverable"
      );
      hoverables.forEach((el) => {
        el.addEventListener("mouseenter", handleMouseEnter);
        el.addEventListener("mouseleave", handleMouseLeave);
      });
    };

    addHoverListeners();

    // Dynamically watch for dynamic elements (e.g. tab switches)
    const observer = new MutationObserver(addHoverListeners);
    observer.observe(document.body, { childList: true, subtree: true });

    return () => {
      window.removeEventListener("mousemove", handleMouseMove);
      cancelAnimationFrame(animationFrameId);
      observer.disconnect();
    };
  }, []);

  return (
    <div className="hidden md:block pointer-events-none fixed inset-0 z-[9999] overflow-hidden">
      {/* Big Ball */}
      <div
        ref={bigBallRef}
        className="fixed top-0 left-0 w-[30px] h-[30px] rounded-full mix-blend-difference pointer-events-none"
        style={{ zIndex: 1000 }}
      >
        <svg height="40" width="40" viewBox="0 0 30 30" className="w-full h-full">
          <circle cx="15" cy="15" r="12" fill="#FAFBFD" strokeWidth="0" />
        </svg>
      </div>

      {/* Small Ball */}
      <div
        ref={smallBallRef}
        className="fixed top-0 left-0 w-[10px] h-[10px] rounded-full mix-blend-difference pointer-events-none"
        style={{ zIndex: 1001 }}
      >
        <svg height="10" width="10" viewBox="0 0 10 10" className="w-full h-full">
          <circle cx="5" cy="5" r="4" fill="#FAFBFD" strokeWidth="0" />
        </svg>
      </div>

      <style jsx global>{`
        @media (min-width: 768px) {
          body, a, button, input, select, textarea, .hoverable, [role='button'] {
            cursor: none !important;
          }
        }
      `}</style>
    </div>
  );
}
