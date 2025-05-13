Coroutine Function - cofunc - (async def)
description paramétrable d'un code à exécuter
l'appel à la fonction produit une coroutine

Coroutine object = objet 'résolu' (plus d'arguments à fournir, déjà injectés)
représentant du code exécutable de manière asynchrone
-> il ne reste plus qu'à await l'objet pour orchestrer l'exécution asynchrone


ARfunc = objet qui porte la description d'un code async produisant un Xresult
Afunc = objet qui porte la description d'un code PUR produisant un result
__call__ renvoi ARcoroutine / Acoroutine

ARcoroutine:
- conteneur pour le coroutine object + méthode pour faire les map and co


XRCoroutine = XFP Result Coroutine
Conteneur pour coroutines produisant un XResult
-> va permettre de faire de la composition
   = appliquer de nouveaux effets pour produire de nouvelle XRCoroutines

XCoroutine = XFP Coroutine
Conteneur pour coroutines produisant un type lambda
-> va permettre de faire du pipe (et peut être d'autres choses)
