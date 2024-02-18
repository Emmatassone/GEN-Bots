# -*- coding: utf-8 -*-

In [9]: def f(b=0, d=dict()):
   ...:     print(d)
   ...:     for k,v in {'b':b}.items():
   ...:         d.setdefault(k, v)
   ...:     print(b)
   ...:     print(d)
   ...:     


In [10]: f(2)
{}
2
{'b': 2}


In [11]: f(4)
{'b': 2}
4
{'b': 2}

El problema en el script está relacionado con el uso de un valor predeterminado mutable (dict()) 
para el parámetro credentials. Cuando proporcionas un valor mutable como valor predeterminado 
para un parámetro, ten en cuenta que ese objeto mutable se crea solo una vez cuando se define
la función, y las llamadas posteriores a la función compartirán la misma referencia al objeto mutable.

Para evitar este comportamiento, hay que utilizar None como valor predeterminado y luego crear 
un diccionario dentro de la función si el valor es None. Aquí tienes una forma de corregir tu función:

In [24]: def f(b=0, d=None):
    ...:     if d is None:
    ...:         d = {}
    ...:     print(d)
    ...:     for k,v in {'b':b}.items():
    ...:         d.setdefault(k, v)
    ...:     print(b)
    ...:     print(d)
    ...:     

In [25]: f(3)
{}
3
{'b': 3}

In [26]: f(2)
{}
2
{'b': 2}

In [27]: 






# Haciendo lo siguiente tampoco resuelve el problema:

def ddict():
    d = None
    d = dict()
    return d


In [21]: def f(b=0, d=ddict()):
    ...:     print(d)
    ...:     for k,v in {'b':b}.items():
    ...:         d.setdefault(k, v)
    ...:     print(b)
    ...:     print(d)
    ...:     

In [22]: f(3)
{}
3
{'b': 3}

In [23]: f(2)
{'b': 3}
2
{'b': 3}
