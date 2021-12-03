package controllers

import (
	"encoding/json"
	"io/ioutil"
	"log"
	"net/http"
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

func callApi(c chan ApiResponse, path string) {
	response, err := http.Get("https://moquette.rbillon.ovh/" + path)
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

	go callApi(priceChan, "price")
	go callApi(deliveryChan, "delivery")
	go callApi(stockChan, "stock")
	go callApi(wishlistChan, "wishlist")

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
