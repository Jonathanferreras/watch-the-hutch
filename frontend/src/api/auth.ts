import { redirect } from "@tanstack/react-router";

const API = {
  login: "/api/v1/auth/login",
  currentUser: "/api/v1/auth/me",
  logout: "/api/v1/auth/logout",
};

export type UserCredentials = {
  username: string;
  password: string;
};

export type AdminUser = {
  id: number;
  username: string;
  role: "VIEWER" | "EDITOR" | "ADMIN";
  created_at: string;
  updated_at: string;
  last_login_at?: string | null;
  is_active: boolean;
};

export type LoginResponse = {
  admin: AdminUser;
};

let currentUser: AdminUser | null | undefined;

export const loginUser = async (credentials: UserCredentials) => {
  const { username, password } = credentials;
  const requestOptions: RequestInit = {
    method: "POST",
    credentials: "include",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      username,
      password,
    }),
  };

  try {
    const response = await fetch(API.login, requestOptions);
    if (response.ok) {
      const { admin }: LoginResponse = await response.json();

      currentUser = admin;

      return admin;
    }
  } catch (error) {
    console.error("Error logging in user:", error);
    throw error;
  }
};

export const verifyUser = async () => {
  if (currentUser !== undefined) {
    return currentUser;
  }

  const requestOptions: RequestInit = {
    method: "GET",
    credentials: "include",
  };

  try {
    const response = await fetch(API.currentUser, requestOptions);
    if (response.ok) {
      currentUser = (await response.json()) as AdminUser;

      return currentUser;
    }

    if (response.status === 401 || response.status === 403) {
      currentUser = null;
      return null;
    }
  } catch (error) {
    console.error("Error verifying user:", error);
  }

  return null;
};

export const requireUser = async () => {
  const currentUser = await verifyUser();

  if (!currentUser) {
    throw redirect({
      to: "/admin",
    });
  }

  return currentUser;
};

export const logoutUser = async () => {
  const requestOptions: RequestInit = {
    method: "POST",
    credentials: "include",
  };

  try {
    await fetch(API.logout, requestOptions);
  } catch (error) {
    console.error("Error logging out user:", error);
  } finally {
    currentUser = null;
  }
};
