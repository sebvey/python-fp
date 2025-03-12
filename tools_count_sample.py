from xfp import Xlist, Xiter, tools


underlying = [1, 2, 3, 2, 4, 5, 3, 2, 1, 1, 3]
xl = Xlist(underlying)
xi = Xiter(underlying)


xl.pipe(tools.count).pipe(print)
xi.pipe(tools.count).pipe(print)


# Pipe / apply -> pour appliquer des fonctions définies ailleurs

# difficile d'implémenter la fonction count directement sur Xlist
# - je retourne un Xdict, Xdict dépend de Xlist ...
# - implémenter ce genre d'utilitaire dans un module tools, à part ?
