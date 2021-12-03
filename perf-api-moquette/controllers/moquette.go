package controllers

import (
	"encoding/json"
	"io/ioutil"
	"log"
	"net/http"
	"os"
)

// GetCartBody : model for a patient
type GetCartBody struct {
	Number int `json:"numberOfProduct"`
}

type GetCartResponse struct {
	PriceTTC     float32   `json:"priceTTC"`
	Wishlist     []Product `json:"wishlist"`
	DeliveryDate string    `json:"deliveryDate"`
	Quantity     int       `json:"quantity"`
}

func getenv(key, fallback string) string {
	value := os.Getenv(key)
	if len(value) == 0 {
		return fallback
	}
	return value
}

var API_DELIVERY = getenv("API_DELIVERY", "https://moquette.rbillon.ovh/delivery")
var API_STOCK = getenv("API_STOCK", "https://moquette.rbillon.ovh/stock")
var API_WISHLIST = getenv("API_WISHLIST", "https://moquette.rbillon.ovh/wishlist")
var API_PRICE = getenv("API_PRICE", "https://moquette.rbillon.ovh/price")

func callApi(c chan ApiResponse, endpoint string) {
	response, err := http.Get(endpoint)
	if err != nil {
		log.Println(err)
	}

	responseData, err := ioutil.ReadAll(response.Body)
	if err != nil {
		log.Println(err)
	}

	var apiResponse ApiResponse

	err = json.Unmarshal(responseData, &apiResponse)

	if err != nil {
		log.Println(err)
	}

	c <- apiResponse
}

// GetCart : endpoint for creation or update patient
func GetCart(w http.ResponseWriter, r *http.Request) {
	body, err := ioutil.ReadAll(r.Body)

	if err != nil {
		log.Println(err)
	}

	var getCartBody GetCartBody

	err = json.Unmarshal(body, &getCartBody)

	if err != nil {
		log.Println(err)
	}

	priceChan := make(chan ApiResponse)
	deliveryChan := make(chan ApiResponse)
	stockChan := make(chan ApiResponse)
	wishlistChan := make(chan ApiResponse)

	go callApi(priceChan, API_PRICE)
	go callApi(deliveryChan, API_DELIVERY)
	go callApi(stockChan, API_STOCK)
	go callApi(wishlistChan, API_WISHLIST)

	var response GetCartResponse = GetCartResponse{
		PriceTTC:     float32((<-priceChan).Data[0].Attributes.Price*getCartBody.Number) * 1.2,
		DeliveryDate: (<-deliveryChan).Data[0].Attributes.NextAvailability,
		Quantity:     (<-stockChan).Data[0].Attributes.Stock,
		Wishlist:     (<-wishlistChan).Data,
	}

	w.Header().Set("Content-type", "application/json;charset=UTF-8")
	w.WriteHeader(http.StatusOK)
	json.NewEncoder(w).Encode(response)
}

type ApiResponse struct {
	Data []Product `json:"data"`
}

type Product struct {
	Attributes Attribute `json:"attributes"`
}

type Attribute struct {
	Price              int    `json:"price,omitempty"`
	NextAvailability   string `json:"nextAvailability,omitempty"`
	Stock              int    `json:"stock,omitempty"`
	ProductName        string `json:"productName,omitempty"`
	ProductDescription string `json:"productDescription,omitempty"`
}
