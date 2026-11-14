import api from "./api";

export const workoutService = {
  async getWorkoutPlan() {
    const response = await api.get("/api/workout/plan");
    return response.data;
  },

  async generateWorkoutPlan() {
    const response = await api.post("/api/workout/generate");
    return response.data;
  },
};
