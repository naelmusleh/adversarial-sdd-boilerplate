import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "New application",
  description: "A new application built with the Adversarial SDD template.",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
