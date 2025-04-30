Coroutine Function - cofunc - (async def)
description paramétrable d'un code à exécuter
l'appel à la fonction produit une coroutine

Dans le scope XFP peuvent être de plusieurs 'genres' :
- décrive la production d'un XResult (XRFunc?)
- plus générale : (XFunc?)
- peuvent prendre un ou plusieurs paramètres ...

XRfunc = objet qui porte la description d'un code produisant XResult
Xfunc = objet qui porte la description d'un code PUR produisant X
__call__ renvoi XRCoroutine / XCoroutine

Coroutine object = objet 'résolu' (plus d'arguments à fournir, déjà injectés)
représentant du code exécutable de manière asynchrone
-> il ne reste plus qu'à await l'objet pour orchestrer l'exécution asynchrone

Dans le scope XFP, les coroutines peuvent soit :
- retourner un Xresult[L,R] => coroutine de type PyCoXR[L,R]
- plus généralement retourner un type X => coroutine de type PyCo[X]

XRCoroutine = XFP Result Coroutine
Conteneur pour coroutines produisant un XResult
-> va permettre de faire de la composition
   = appliquer de nouveaux effets pour produire de nouvelle XRCoroutines

XCoroutine = XFP Coroutine
Conteneur pour coroutines produisant un type lambda
-> va permettre de faire du pipe (et peut être d'autres choses)
