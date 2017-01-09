# greentext

Greentext is a not-to-be-taken-very-seriously procedural programming language written in and interpreted into Python. I was inspired by [this reddit thread](https://www.reddit.com/r/shittyprogramming/comments/3p45zw/new_programming_language_on_the_scene_memearrow/) and decided to turn the idea into reality.

Greentext features most of the basic programming constructs, such as variables, conditional statements, loops, function calls, and recursion. See below for detailed specifications and examples.

This project was made mostly for fun, so the code was kind of written with "*just make this work*" in mind. As a result the error-handling and code readability aspects are fairly lacking. I have plans to recreate something like this as an actual compiler using Haskell in the future.

----

Become an _Internet Connoisseur™_ in `#{CURRENT_YEAR}` and start writing code in memes today!

### Usage

The interpreter takes input from stdin. `python greentext.py < input_file` to run.

### The language

Every line must start with the greentext arrow a.k.a. meme arrow '>'

Everything in a line after any '#' is commented out

Boolean values are true = `:^)` false = `:^(`.

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
>be foo like 19             # foo = 19
>be var like 1 * 2 + foo    # var = 21
>be bar                     # bar = no value (empty string)

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
- **For loops** and **while loops** are both done with `>inb4`
- For loop syntax: `>inb4 counter_name from start to end by step`
- `by step` can be omitted; step value defaults to 1
- While loop syntax: `>inb4 boolean_expression`
- `>done inb4` indicates end of loop
````
>inb4 i from 5 + 5 to 10 - 2 * 5 by -2
  >mfw i
>done inb4

>be n like 0
>inb4 n < 10
  >be n like n + 1
>done inb4
````

### Example - FizzBuzz

````
>inb4 i from 0 to 100
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

- **Main function** is declared with `>be me` and returned with `>thank mr skeltal`
- `>thank mr skeltal` also works as system exit; it can be called anywhere to terminate program execution.
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

>be me
    >wew foo(1, 2)
    >wew bar
    >be a like wew          # a = 3
    >thank mr skeltal
````
- All variables declared inside functions are local to the scope of that function
- Global variables can be declared outside of any function

### Example - Factorial

````
>wewlad factorial(n)
  >be result like 1
  >implying n > 1
    >wew factorial(n - 1)
    >be result like wew
  >done implying
  >tfw n * result

>be me
  >be n like 10
  >wew factorial(n)
  >mfw "factorial of", n, "is", wew
  >thank mr skeltal
````
