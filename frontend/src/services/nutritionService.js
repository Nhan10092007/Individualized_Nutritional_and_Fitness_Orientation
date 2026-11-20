import api from "./api";

export const nutritionService = {
  async getMealPlan() {
    const response = await api.get("/api/nutrition/plan");
    return response.data;
  },

  async generateMealPlan(days = 7) {
    const response = await api.post("/api/nutrition/generate", { days });
    return response.data;
  },
};
