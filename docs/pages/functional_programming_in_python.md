---
layout: page
title: Functional Programming in Python
permalink: /functional_programming/
nav_order: 101
---
<h1 style="font-weight: bold">Functional Programming in Python</h1>

While Python is technically a multi-paradigm language, its dynamic and weak typing system forbids it to apply a strictly functional approach. Moreover it seems a much more common development habits to make a wide use of the imperative, quick time-to-market imperative style. With this in mind, XFP tries to complete the functional programming experience while smoothly integrating with Python and capitalizing on its natural syntax.  
It doesn't come without some drawback though. 
1. XFP programming language doesn't define the strictest type system. As seen in [About typing](/python-fp/about-typing) section, we sometime choose to obfuscate some types against an `Any` equivalent to simplify some signatures. Plus with the tooling provided by today's Python, a fully typing API would cause much trouble implementing it (and using it afterward).
2. The immutability paradigm isn't strongly anchored into Python practices, which makes enforcing it difficult. It can indeed gives a false sentiment of security at best, and conflicts with existing libraries at worst. We have chosen to sometimes only make assumption of immutability and delegate to the developer the responsability of enforcing it.  