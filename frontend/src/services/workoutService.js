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

  async swapExercise({ day, exercise_index, new_exercise_id }) {
    const response = await api.patch("/api/workout/plan/swap-exercise", {
      day,
      exercise_index,
      new_exercise_id,
    });
    return response.data;
  },
};
