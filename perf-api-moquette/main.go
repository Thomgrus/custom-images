package main

import (
	"log"
	"net/http"
	"os"
)

func getPort() string {
	p := os.Getenv("PORT")
	if p != "" {
		return ":" + p
	}
	return ":8080"
}

func main() {
	router := InitializeRouter()

	// Listen
	log.Fatal(http.ListenAndServe(getPort(), router))
}
