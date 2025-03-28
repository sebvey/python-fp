---
layout: page
title: Word Count
parent: Samples
permalink: /samples/word_count
nav_order: 1
---

<h1 style="font-weight: bold">Word Count</h1>

Considering a file "book.txt", we are going to read it line by line and do a wordcount over it.  
1. First we are going to count the overall number of words in the book :
    ```python
    from xfp import Xlist

    with open("book.txt", "r") as book:
        print(
            Xlist(book.readlines())
            .map(lambda line: line.split(" "))
            .map(len)
            .fold_left(0,lambda x, y: x + y)
        )
    ```
2. Now let's imagine we want to have a distinct count per word, then display the number of occurrence for each word :
    ```python
    from xfp import Xlist, Xdict

    with open("book.txt", "r") as book:
        (
            Xlist(book.readlines())
            .map(lambda line: line.strip())
            .flat_map(lambda line: line.split(" "))
            .fold_left(Xdict[str, int]({}), lambda acc, el: acc.updated(el, acc.get(el, 0) + 1))
            .foreach(lambda key, value: print(f"word '{key}': {value} occurence(s)"))
        )
    ```
3. Sort them to display the more frequent first :
    ```python
    from xfp import Xlist, Xdict
    from xfp.functions import tupled2

    with open("book.txt", "r") as book:
        (
            Xlist(book.readlines())
            .map(lambda line: line.strip())
            .flat_map(lambda line: line.split(" "))
            .fold_left(Xdict[str, int]({}), lambda acc, el: acc.updated(el, acc.get(el, 0) + 1))
            .items()
            .sorted(tupled2(lambda _, value: value), reverse=True)
            .foreach(tupled2(lambda key, value: print(f"word '{key}': {value} occurence(s)")))
        )
    ```
4. What if the we are working with the biggest book of the universe ? let's stream the lines one by one :
    ```python
    from typing import Generator, Any
    from xfp import Xiter, Xdict
    from xfp.functions import tupled2
    
    def lines() -> Generator[str, Any, None]:
        with open("book.txt", "r") as f:
            for line in f:
                yield line
    
    (
        Xiter(lines())
        .map(lambda line: line.strip())
        .flat_map(lambda line: line.split(" "))
        .fold_left(Xdict[str, int]({}), lambda acc, el: acc.updated(el, acc.get(el, 0) + 1))
        .items()
        .sorted(tupled2(lambda _, value: value), reverse=True)
        .foreach(tupled2(lambda key, value: print(f"'{key}': {value} occurence(s)")))
    )
    ```
