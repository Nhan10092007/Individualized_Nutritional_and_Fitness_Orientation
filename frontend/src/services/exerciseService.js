import api from "./api";

export const exerciseService = {
  async getExercises(params = {}) {
    const response = await api.get("/api/exercises", { params });
    return response.data;
  },

  async getExerciseById(exerciseId) {
    const response = await api.get(`/api/exercises/${exerciseId}`);
    return response.data;
  },
};
