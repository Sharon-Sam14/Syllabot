import type { Metadata } from "next";
import { Cormorant_Garamond, Comfortaa } from "next/font/google";
import "./globals.css";
import CustomCursor from "../components/CustomCursor";

const cormorantGaramond = Cormorant_Garamond({
  variable: "--font-cormorant",
  subsets: ["latin"],
  weight: ["300", "400", "500", "600", "700"],
  style: ["normal", "italic"],
  display: "swap",
});

const comfortaa = Comfortaa({
  variable: "--font-comfortaa",
  subsets: ["latin"],
  weight: ["300", "400", "500", "600", "700"],
  display: "swap",
});

export const metadata: Metadata = {
  title: "Syllabot - Adaptive Study Planner",
  description: "The Google Maps for your syllabus. Turn unstructured syllabus text into adaptive daily study plans, track progress, and automatically replan when behind.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html
      lang="en"
      className={`${cormorantGaramond.variable} ${comfortaa.variable} h-full antialiased`}
    >
      <body className="min-h-full flex flex-col font-sans bg-app-bg text-app-text transition-all duration-300">
        <CustomCursor />
        {children}
      </body>
    </html>
  );
}
