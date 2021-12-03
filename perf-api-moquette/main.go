package main

import (
	"log"
	"net/http"
	"os"

	"github.com/dktunited/perf-api-moquette/controllers"
)

func getPort() string {
	p := os.Getenv("PORT")
	if p != "" {
		return ":" + p
	}
	return ":8080"
}

func main() {
	controllers.InitCache()
	router := InitializeRouter()

	// Listen
	log.Fatal(http.ListenAndServe(getPort(), router))
}
