package main

import (
	"fmt"
	"os"

	"task/strutil"
)

func main() {
	fmt.Println(strutil.Reverse(os.Args[1]))
}
