---
title: Simple data pipelining in C++
author: jayvesmir
date: 2025-06-08
barcode: 40028866
---

## Introduction - The bullshit that a blogpost needs to start with

Pipelines are constructs that let us define an algorithm in a high-level, rigid, step-by-step fashion.  

Let's say you wish to parse some sort of file, you're first going to need the actual data from the file, then you'll probably parse some kind of header, then you'll parse the raw data stored in the file, decode it, etc. Some of these steps might be reusable in completely different algorithms. Now, let's say you want to parse another kind of file, you still need to read it, right? That first step is already reusable!  

If we're clever enough, we can generalize any step to be reusable across many pipelines. Take [Huffman Coding](https://en.wikipedia.org/wiki/Huffman_coding) for example, it's used in many compression algorithms like [JPEG](https://en.wikipedia.org/wiki/JPEG), [PNG](https://en.wikipedia.org/wiki/PNG), and even [H.264](https://cs.wikipedia.org/wiki/H.264) uses it to encode the DCT transform coefficients.

Let's take a look at this idea then!

![Gopy](/public/img/cxx_pipelines/gopy.jpg)

## Prerequisite info - Things to consider before misunderstanding

This might be a bummer, but understanding what I'm about to describe requires (even if pretty basic) knowledge of C++ templates, C++ concepts, and a general knowledge of the modern C++ STL.

I'm not competent enough to try and explain how all this shit works, I'm just here to try and share an idea I had one evening. I tried to put as many links to resources to the parts I think would be the most difficult to understand for beginners, but I'm not a teacher, go look this stuff up, try to implement shit on your own and fail a couple times, that's the best way to learn!

[cppreference.com](https://en.cppreference.com/) - Basically a retelling of the C++ standard in web form, it's great, use it!  
[Cherno's C++ series](https://www.youtube.com/playlist?list=PLlrATfBNZ98dudnM48yfGUldqGD0S4FFb) - A YouTube playlist that tries to teach you C++

## Defining a pipeline - Boilerplate to manage our steps

To define a pipeline like this in C++ efficiently, we're going to use templating and let the compiler figure out how to structure it in the fastest way possible.

```cpp
// pipeline.hpp

template <typename... Steps>
class pipeline;
```

This is a basic definition of our pipeline, it doesn't do anything, just lets the compiler know that an object of type ***pipeline*** can be instantiated with **any** other types, we're going to restrict this later on.

```cpp
// pipeline.hpp

template <typename... Steps>
class pipeline;

template <typename CurrentStep, typename... Rest>
class pipeline {
    // Store the steps inside the pipeline for cleaner invokaction
    CurrentStep m_current_step;
    pipeline<Rest...> m_rest;

    public:
        template <typename Input>
        constexpr auto operator()(Input&& input) {
            return m_rest(m_current_step(std::forward<Input>(input)));

            // If the steps weren't instantiated as members inside the pipeline this function would look something like this:
            //   return pipeline<Rest...>()(CurrentStep()(std::forward<Input>(input)));
            // You can see we have to construct the recursed pipeline and the current step in-place,
            // which isn't very pretty, plus, if we enable optimizations, many compilers will do this without storing them inside the pipeline anyways 
        }
}
```

Now we've added another definition for ***pipeline***, this one actually has a way to invoke the steps stord inside it! They get invoked by calling the **()** operator on any instance of ***pipeline***.

```cpp
auto some_pipeline = pipeline<...>();
auto result = some_pipeline(...) // Like this!!
```

And since we've marked the **()** operator as ***constexpr***, if all of the inputs can be inferred by the compiler (and it can see all of our steps' definitions as ***constexpr***), the pipeline's result gets computed at compile-time!! Sadly, this doesn't happen very often in practice, since we can't predict what kind of data we'll be handling. 😞

Our pipeline works thanks to template recursion, you can see we construct another pipeline object with the remaining steps inside our pipeline, which then gets expanded further and further, until only one step is left. But we haven't defined what happens when the last step is reached! We can do that by just defining another case for our pipeline template. 

```cpp
// pipeline.hpp

template <typename... Steps>
class pipeline;

template <typename CurrentStep, typename... Rest>
class pipeline {
    // Store the steps inside the pipeline for cleaner invokaction
    CurrentStep m_current_step;
    pipeline<Rest...> m_rest;

    public:
        template <typename Input>
        constexpr auto operator()(Input&& input) {
            return m_rest(m_current_step(std::forward<Input>(input)));

            // If the steps weren't instantiated as members inside the pipeline this function would look something like this:
            //   return pipeline<Rest...>()(CurrentStep()(std::forward<Input>(input)));
            // You can see we have to construct the recursed pipeline and the current step in-place,
            // which isn't very pretty, plus, if we enable optimizations, many compilers will do this without storing them inside the pipeline anyways 
        }
}

template <typename LastStep>
class pipeline {
    LastStep m_last_step;

    public:
        template <typename Input>
        constexpr auto operator()(Input&& input) {
            return m_last_step(std::forward<Input>(input));
        }
}
```

It might be a little messy to imagine what's actually happening here, but essentially, when we construct our ***pipeline*** with steps *n - 1* more pipelines get constructed until the case with ***LastStep*** is reached, at this point, inlining happens, and the compiler (I only know about clang doing this, but MSVC probably does this too) basically only calls our steps without the pipeline layer. With 4 steps our pipeline would get compiled down to this:

```cpp
auto result = m_last_step(m_step_2(m_step_1(m_step_0(input))));
```

Keep in mind that since C++14 the ***std::forward*** calls all get evaluated at compile-time, you can read about what ***std::forward*** does in detail here: [cppreference.com](https://cppreference.com/w/cpp/utility/forward.html)

## Defining a pipeline step - The slave doing the dirty work

Defining a step for our pipeline is actually extremely simple! All we need to do is create an object that has a valid **()** operator for it's input.

```cpp
// file_reader.hpp

#include <vector>     // For std::vector
#include <cstdint>    // For uint8_T
#include <fstream>    // For std::ifstream & std::ios::binary
#include <filesystem> // For std::filesystem::path

struct read_file_binary {
    constexpr std::vector<uint8_t> operator()(const std::filesystem::path& path) {
        auto stream = std::ifstream(path, std::ios::binary);
        if (!stream) {
            // I'm too lazy to write examples of handling errors, I'm sure you can figure that out on your own 😛
            return {}; 
        }

        return {
            std::istreambuf_iterator<char>(stream), std::istreambuf_iterator<char>()
        };
    }
}
```

I chose to define our example step as a struct with a **()** operator that actually does the work. But you can define a step as pretty much anything that can be invoked, be it a [std::function](https://en.cppreference.com/w/cpp/utility/functional/function.html) object, a lambda or just a regular C++ function.

What it does is just read a file into a ***std::vector***, if we write another step that takes a ***std::vector*** as input, we can then define a pipeline around these!

```cpp
// data_selector.hpp

#include <ranges>    // For std::ranges::copy_if
#include <algorithm> // For std::ranges::copy_if
#include <vector>    // For std::vector
#include <cstdint>   // For uint8_t

struct select_ones {
    constexpr std::vector<uint8_t> operator()(const std::vector<uint8_t>& data) {
        std::vector<uint8_t> output;

        std::ranges::copy_if(data, std::back_inserter(output), [](auto byte) { return byte == 0x01; });

        return output;
    }
}
```

This step doesn't do anything useful, it copies the bytes it gets from any other step that outputs a ***std::vector*** that equal ***0x01*** into an output buffer and returns it. But we can now actually define a pipeline that reads a file and outputs the ***0x01*** bytes it found in it!

```cpp
// some_file.cpp

#include <cstdint> // For int32_t

// Include our little pipeline library
#include "pipeline.hpp"
#include "file_reader.hpp"
#include "data_selector.hpp"

int32_t main() {
    auto get_ones = pipeline<read_file_binary, select_ones>();

    auto ones = get_ones("some_file.bin");
}
```

I don't know if I have anything else to say about this other than that, if you supply it with a hard-coded path like this, something beautiful happens, and that is... Inlining! When we compile this code, it actually gets compiled to something close to this:

```cpp
// some_file.cpp

#include <cstdint> // For int32_t

// Include our little pipeline library
#include "pipeline.hpp"
#include "file_reader.hpp"
#include "data_selector.hpp"

int32_t main() {
    auto ones = select_ones()(read_file_binary()("some_file.bin"));
}
```

And if we make our step functions ***static*** we can get closer to this, which is an entire **2** function calls less!

```cpp
auto ones = select_ones::operator()(read_file_binary::operator()("some_file.bin"));
```

If we pretend compilers could actually read files in constexpr functions for us, then we can take this optimization fantasy further: 

```cpp
auto ones = {0x01, 0x01, 0x01, ..., 0x01, 0x01}; // However many ones were in some_file.bin
```

But I digress, this is never going to happen, keep in mind it's possible though!

Currently, when we fuck something up, the compiler is gonna thrown an essay at us, we can get it to shut up a little bit by using concepts! Let's explore that!

## Constraining our pipeline - Template errors are the fucking worst, let's make them better

We can contrain the inputs we give to our pipeline using C++ concepts, a concept in C++ is basically a compile-time rule for types. Of course, our code will fail just fine without them, but we want nice error messages!

 A basic one for defining a step for our pipeline would look like this:

```cpp
// pipeline.hpp

template <typename Step, typename Input>
concept ValidStep = requires(Step step, Input input) {
    { step(input) };
}
```

This concept checks to see if a ***Step*** we provided can actually take ***Input*** as an argument.

Again, I'm not going to even try to explain concepts, if you've gotten this far, you probaly already know about them, if not, please consult [cppreference.com](https://en.cppreference.com/w/cpp/concepts.html).

We can use concepts in our pipeline definition like this:

```cpp
template <typename CurrentStep, typename... Rest>
class pipeline {
    // Store the steps inside the pipeline for cleaner invokaction
    CurrentStep m_current_step;
    pipeline<Rest...> m_rest;

    public:
        template <typename Input>
            requires ValidInput<CurrentStep, Input>
        constexpr auto operator()(Input&& input) {
            return m_rest(m_current_step(std::forward<Input>(input)));

            // If the steps weren't instantiated as members inside the pipeline this function would look something like this:
            //   return pipeline<Rest...>()(CurrentStep()(std::forward<Input>(input)));
            // You can see we have to construct the recursed pipeline and the current step in-place,
            // which isn't very pretty, plus, if we enable optimizations, many compilers will do this without storing them inside the pipeline anyways 
        }
}
```

All we did was slap it on before the **()** operator definition, this is really all it takes to make our error messages 10x clearer in what actually went wrong! Make sure to also include it on all other cases of our pipeline template, otherwise you might just get hit in the face with another wall of text coming from those.

## Bye Bye

That's pretty much it, hope you learned something new you might not have thought of, Bye!  
My github is [@jayvesmir](https://github.com/jayvesmir) if you wanna read through my terrible code.