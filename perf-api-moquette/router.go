package main

import (
	"github.com/dktunited/perf-api-moquette/controllers"
	"github.com/gorilla/mux"
)

// InitializeRouter : init router
func InitializeRouter() *mux.Router {
	// StrictSlash is true => redirect /Users/ to /Users
	router := mux.NewRouter().StrictSlash(true)

	// Health Check
	router.Methods("GET").Path("/up").Name("Health").HandlerFunc(controllers.HealthCheck)

	router.Methods("GET").Path("/cart").Name("Price and stock call").HandlerFunc(controllers.GetCart)

	return router
}
