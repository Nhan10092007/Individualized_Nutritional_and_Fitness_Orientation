import api from "./api";

export const userService = {
  async getProfile() {
    const response = await api.get("/api/users/profile");
    return response.data;
  },

  async submitOnboarding(payload) {
    const response = await api.post("/api/users/onboarding", payload);
    return response.data;
  },
};
