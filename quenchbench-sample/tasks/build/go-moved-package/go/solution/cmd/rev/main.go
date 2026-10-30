package main

import (
	"fmt"
	"os"

	"task/text"
)

func main() {
	fmt.Println(text.Reverse(os.Args[1]))
}
