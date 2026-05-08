import { BookOpen, Compass, LogOut, Search, Sparkles, UserRound } from "lucide-react";
import { NavLink, Outlet } from "react-router-dom";
import { useAuth } from "../contexts/AuthContext";
import { Button } from "./ui/button";

const nav = [
  { to: "/dashboard", label: "Dashboard", icon: Compass },
  { to: "/recommendations", label: "For You", icon: Sparkles },
  { to: "/search", label: "Search", icon: Search },
  { to: "/profile", label: "Profile", icon: UserRound },
];

export function AppShell() {
  const { logout, user } = useAuth();
  return (
    <div className="min-h-screen bg-background text-foreground">
      <header className="sticky top-0 z-20 border-b border-border bg-background/90 backdrop-blur">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-4 py-3">
          <NavLink to="/dashboard" className="flex items-center gap-2 text-lg font-bold">
            <BookOpen className="h-5 w-5 text-rose-500" />
            WhatNext
          </NavLink>
          <nav className="hidden items-center gap-1 md:flex">
            {nav.map((item) => (
              <NavLink
                key={item.to}
                to={item.to}
                className={({ isActive }) =>
                  `flex items-center gap-2 rounded-md px-3 py-2 text-sm ${isActive ? "bg-zinc-800 text-white" : "text-zinc-400 hover:text-white"}`
                }
              >
                <item.icon className="h-4 w-4" />
                {item.label}
              </NavLink>
            ))}
          </nav>
          <div className="flex items-center gap-3">
            <span className="hidden text-sm text-zinc-400 sm:inline">{user?.username}</span>
            <Button onClick={logout} className="h-9 bg-zinc-800 px-3 hover:bg-zinc-700" title="Log out">
              <LogOut className="h-4 w-4" />
            </Button>
          </div>
        </div>
      </header>
      <main className="mx-auto max-w-7xl px-4 py-6">
        <Outlet />
      </main>
      <nav className="fixed bottom-0 left-0 right-0 z-20 grid grid-cols-4 border-t border-border bg-background md:hidden">
        {nav.map((item) => (
          <NavLink key={item.to} to={item.to} className="flex flex-col items-center gap-1 py-3 text-xs text-zinc-400">
            <item.icon className="h-4 w-4" />
            {item.label}
          </NavLink>
        ))}
      </nav>
    </div>
  );
}
