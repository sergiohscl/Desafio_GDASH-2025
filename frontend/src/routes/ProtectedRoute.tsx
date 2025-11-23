// src/routes/ProtectedRoute.tsx
import React from "react";
import { Navigate } from "react-router-dom";
import { authService } from "@/services/authService";
import type { JSX } from "react/jsx-runtime";

interface RouteProps {
  children: JSX.Element;
}

export const ProtectedRoute: React.FC<RouteProps> = ({ children }) => {
  const token = authService.getAuthToken();

  if (!token) {
    return <Navigate to="/" replace />;
  }

  return children;
};

export const PublicRoute: React.FC<RouteProps> = ({ children }) => {
  const token = authService.getAuthToken();

  if (token) {
    return <Navigate to="/home" replace />;
  }

  return children;
};
