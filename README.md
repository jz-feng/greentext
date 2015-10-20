# greentext

### Still work in progress

Do you love coding? Do you enjoy some good greentext stories and dank memes? With this interpreter you can **write code in greentext**!!!111!!11!

### Usage

The parser takes input from stdin. Run it and write code, or pass a pre-written input file into it. You know the drill.

### The language

Every line must start with the greentext arrow a.k.a. meme arrow '>'

Note comments are not implemented yet. Pretend the #'s in below snippets work as comments

- Print output with `>mfw`
- Surround token with double quotes to print as literal; multi-token literals coming soon!!11!
- Separate with commas to print multiple values on the same line
- Boolean values: true = `:^)` false = `:^{`
````
>mfw 3, 4.5, "string"   # Outputs 3 4.5 string
>mfw 3 < 5,  3 * 4 - 5  # Outputs :^) 7
````
- Declare and assign variables with `>be like`
- Format: `>be var_name like var_value`
````
>be me like 19
>be var like 1 * 2 - (3 - 4)
>be rare_pepe like me + var
>mfw rare_pepe      # Outputs 22.0
````
- Conditional statements are done with `>implying`
- `>implying` begins an if statement; `>or not` begins the else branch; `>done implying` ends the if statement
- Conditional expression can be either a variable, comparison of constants, or comparison of variables
  - `a is b` a == b
  - `a isn't b` a != b
  - >, <, >=, <= work the same way
````
>implying 3 is 4
  >mfw "true"
>or not
  >mfw "false"    # Outputs false
>done implying
````
- For loops are done with `>inb4`
- Format: `>inb4 counter_name from start to end by step`; `>done inb4` indicates end of loop
````
>inb4 i from 10 to 0 by -2
  >mfw i        # Outputs 10 8 6 4 2 (on separate lines)
>done inb4
````

### Example - FizzBuzz

````
>inb4 i from 0 to 100 by 1
    >implying i % 15 is 0
        >mfw "fizzbuzz", i
    >or not
        >implying i % 3 is 0
            >mfw "fizz", i
        >done implying
        >implying i % 5 is 0
            >mfw "buzz", i
        >done implying
	  >done implying
>done inb4
````

### Planned functionalities
- "else if" statements
- Functions and procedures
