Coroutine Function (async def) - cofunc
description paramétrable d'un code à exécuter
l'appel à la fonction produit un coroutine object

Coroutine Object - coroutine
description paramétré d'un code à exécuter
les paramètres ont été injecté, 'il ne reste plus qu'à await'
type = abc.Coroutine[Any,Any,X]

Awaitable
un peu plus général que le coroutine object :
tout object que l'on peut await (en arrière plan il va construire et await un coroutine object )

TYPING:
COROUTINE FUNCTION:
- Callable[P,Coroutine[Any,Any,X]]
