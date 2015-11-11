# greentext

### Still work in progress

Do you love coding? Do you enjoy some good greentext stories and dank memes? With this interpreter you can **write code in greentext**!!!111!!11!

### Usage

The interpreter takes input from stdin. Run it and write code, or pass a pre-written input file into it.

### The language

Every line must start with the greentext arrow a.k.a. meme arrow '>'

Everything in a line after any '#' is commented out

Boolean values are true = `:^)` false = `:^(`. They are actually just string constants.

- **Print output** with `>mfw`
- As usual, double quotes denote string literal
- Separate with commas to print multiple values on the same line
````
>mfw 3, 4.5, "string"   # Outputs 3 4.5 string
>mfw 3 < 5,  3 * 4 - 5  # Outputs :^) 7
````
- **Declare and assign variables** with `>be like`
- Format: `>be var_name like var_value`
````
>be me like 19              # me = 19
>be var like 1 * 2 + me     # var = 21
>be foo                     # foo = no value (empty string)

````
- **Conditional statements** are done with `>implying`
- `>implying` is "if"; `>or not` is "else"; `>done implying` is "end if"
- Condition can be any expression that evaluates to a Boolean value
  - `a is b` a == b
  - `a isn't b` a != b
  - >, <, >=, <= work the same way
````
>implying 3 is 4 and 7 > 5
  >mfw "true"
>or not
  >mfw "false"    # Outputs false
>done implying
````
- **For loops** are done with `>inb4`
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

### Program Structure

Greentext works similarly to C, with a main function and other functions that can be defined and called

- **Main function** is declared with `>dank memes`
- Code execution begins at main
- **Functions** can be declared with `>wewlad func_name(params)` and called with `>wew func_name(params)`
- All functions are returned with `>tfw expression`
- Value returned by a function is accessed by `wew`; this variable stores the value of the last "non-void" function called

````
>wewlad foo(param1, param2)
    #stuff here
    >tfw param1 + param2

>wewlad bar                 # function takes no arguments
    #stuff here
    >tfw                    # function returns no value

>dank memes
    >wew foo(1, 2)
    >wew bar
    >be a like wew          # a = 3
    >tfw
````
- All variables declared inside functions are local to the scope of that function
- Global variables can be declared outside of any function

### Example - Factorial

````
>wewlad factorial(n)
  >be result like 1
  >implying n > 1
    >be m like n - 1
    >wew factorial(m)
    >be result like wew
  >done implying
  >tfw n * r

>dank memes
  >be n like 10
  >wew factorial(n)
  >mfw wew                  # Outputs n!
  >tfw
````

### Upcoming Stuff
- "else if" statements
- Multi-token string literals
- Data structures and pointers??? (Sounds like fun)
