<template>
  <!-- No changes to template section -->
</template>

<script>
import axios from "axios";

export default {
  methods: {
    handleCheckIn() {
      this.isSubmitting = true;
      const data = {
        food_completed: this.foodCompleted,
        activity_completed: this.activityCompleted,
      };

      const url = this.isTestMode
        ? `${API_URL}/recommendations/checkin-test`
        : `${API_URL}/recommendations/checkin`;

      axios
        .post(url, data, {
          headers: { Authorization: `Bearer ${this.token}` },
        })
        .then((response) => {
          this.isSubmitting = false;
          this.submissionSuccess = true;

          // Store next day recommendation in local storage for dashboard
          if (response.data.next_day_recommendation) {
            localStorage.setItem(
              "next_day_recommendation",
              JSON.stringify(response.data.next_day_recommendation)
            );
            localStorage.setItem("next_date", response.data.next_date);
            localStorage.setItem(
              "will_regenerate_tomorrow",
              response.data.will_regenerate_tomorrow
            );
          }

          // Display success message briefly before redirecting
          this.$toast.success("Check-in berhasil! Mengarahkan ke dashboard...");

          // Redirect to dashboard after short delay
          setTimeout(() => {
            this.$router.push({ name: "Dashboard" });
          }, 2000);
        })
        .catch((error) => {
          this.isSubmitting = false;
          this.submissionError = true;
          this.errorMessage =
            error.response?.data?.error || "Gagal melakukan check-in";
          console.error("Check-in error:", error);
        });
    },
  },
};
</script>

<style>
/* No changes to style section */
</style>
