# Research notes:
## Authors Note:
This file is to contain my research on the inner workings of python. The main things that will be address is safety, best practice, and computation speed. I am making this for my benefit and others who will work with the CSE simulator coding base. What will follow is a list of topics that I have researched and why I decided to code the simulator the way I did. I will also leave notes about things that did and didn't work when I made this system. I hope this will be useful to the reader. 

## Threading
I started have some major concerns about data safety when I was working on the system. The number of thread quickly grew from 1 to 2 then 3 then  10 and now we are easily working with over a dozen threads. Lets look at different ways of using mutex locks and see witch one is the safest. 

### Typing in python
Python has two main typings behind the curtain that will become relevant. Immutable, and Mutable. Immutable data types CAN NOT be changed after they are declared. (This is a direct artifact of python being writer in c and c++). Mutable types can be changed after they are declared. 

| Immutable | Mutable |
| ---- | ---- |
| Numbers | list |
| string | dict |
| Tuple | set |
| frozen set | byte array |
| byte |  |

Note: The above list is not compressive, but is given by way of example. 

#### Now lets consider how python works with its Immutable types. 

![Python Immutable Declaration](python_immutable_types.webp)

The above example shows how an immutable variable is declared in python. Note that the token name of the variable is assigned to the memory location not to the value of the actual variable. Now lest consider what happens when we create a second token for the same variable. 

```python
    A = 23
    B = A
    A = 0
```
NOTE: in this case A and B are the token names for the variables. 

![Token variable example](token_varible_example.webp)
We can see that for immutable types we create a new token for the new value. So when threading if we do something like the following:
```python
shared_data = ... #immutable type

with mutex_lock:
    copy = shared_data
#use copy ...
``` 
It will be safe so long as the variable type is immutable, however if the variable type is mutable then we need to do the following.

the following:
```python
import copy

shared_data = ... #mutable type

with mutex_lock:
    copy_mutable = copy.deepcopy(shared_data)
#use copy_mutable ...
``` 

citation: https://alexkataev.medium.com/magic-python-mutable-vs-immutable-and-how-to-copy-objects-908bffb811fa



## Events notes:
I went back and forth on adding events but eventually I decided to add them. Just be careful not to have the function called by the event to take too long because it will freeze part of the system. 

## Documentation:
Look I am going to be honest, I HATE documentation, the day I wrote this for example I have literally been writing documentation for 8 hours today. However, I have worked on serval coding project, and without accepting projects that were not document got through away. If you want your code to last, then please document it. If you are going to add to  this code base, then please document what you are doing so all this work doesn't go to waste. 

## Linting:  
Look I hate linting as much as documentation, but all I gotta say is do it! If you want people to be able to read what you are doing then you need to lint. It forces your code to be readable. You don't have to lint when you are debugging, once you have a feature working go back though and lint the code then push it to main. 

-Good luck to who ever follows me here. 