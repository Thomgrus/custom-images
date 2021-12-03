package controllers

import (
	"encoding/json"
	"errors"
	"time"

	"github.com/patrickmn/go-cache"
)

// MyCache : app cache
var MyCache *AppCache

type AppCache struct {
	client *cache.Cache
}

func (r *AppCache) Set(key string, data interface{}, expiration time.Duration) error {
	b, err := json.Marshal(data)
	if err != nil {
		return err
	}

	r.client.Set(key, b, expiration)
	return nil
}

func (r *AppCache) Get(key string) ([]byte, error) {
	res, exist := r.client.Get(key)
	if !exist {
		return nil, nil
	}

	resByte, ok := res.([]byte)
	if !ok {
		return nil, errors.New("Format is not arr of bytes")
	}

	return resByte, nil
}

// InitCache : init cache
func InitCache() {
	MyCache = &AppCache{
		client: cache.New(5*time.Minute, 10*time.Minute),
	}
}
