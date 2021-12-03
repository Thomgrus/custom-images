package controllers

import (
	"fmt"
	"net/http"
)

// HealthCheck : endpoint for Health Check
func HealthCheck(w http.ResponseWriter, r *http.Request) {
	w.WriteHeader(http.StatusOK)
	fmt.Fprintf(w, "Up")
}
