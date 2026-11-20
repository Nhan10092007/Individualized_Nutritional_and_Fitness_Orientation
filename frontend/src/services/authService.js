import api from "./api";

export const authService = {
  async login(email, password) {
    const response = await api.post("/api/auth/login", { email, password });
    return response.data;
  },

  async register(email, password, full_name) {
    const response = await api.post("/api/auth/register", {
      email,
      password,
      full_name,
    });
    return response.data;
  },

  async getMe() {
    const response = await api.get("/api/auth/me");
    return response.data;
  },
};
