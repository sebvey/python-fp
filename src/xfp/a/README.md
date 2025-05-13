# PURE PYTHON

Coroutine Function (async def) - cofunc
description paramétrable d'un code à exécuter
l'appel à la fonction produit un coroutine object

Coroutine Object - Coroutine[YieldType, SendType, ReturnType] 
description paramétré d'un code à exécuter
les paramètres ont été injectés, 'il ne reste plus qu'à await'
possède les méthodes permettant d'être géré par un background:
- send(value) -> 'starts or resume exec of the coroutine'
- throw(value) -> 'raises the specified exception'
- close() -> 'causes the coroutine to clean itself up and exit'

est aussi un Awaitable (objet que l'on peut await dans les coroutine functions)


Awaitable[ReturnType]
objet que l'on peut await dans les coroutines functions
n'est pas en soit une coroutine, ne peut pas être géré tel qu'elle par un backend.
Doit être await dans une coroutine function pour ça
type

# A


