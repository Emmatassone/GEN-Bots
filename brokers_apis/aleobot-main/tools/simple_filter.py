
"""
https://numpy.org/doc/stable/reference/routines.sort.html
https://numpy.org/doc/stable/reference/generated/numpy.isin.html

"""

# Version _4_22_beta


import operator as op
import numpy as np
from functools import partial,reduce
"""
import ctypes
ctypes.cast(2612438654352, ctypes.py_object)
id('object')==2612438654352
"""

class fx:
    
    oper, cond = op.eq, op.or_
    f_method, _axis = 0, 0
    invert, lista, tweaked, built = False, False, False, False
    
    def __init__(self, *args, **_kwargs_):  # los kwargs se reciben internamente y no deberian pasarse al instanciar un objeto por fuera de la clase
        args = list(args,) if len(args)>0 and not isinstance(args[0],list) or self.lista else list(*args)
        self.elem = args if self.lista else sum( (i if isinstance(i,list) else [i] for i in args),[] )
        for k,v in _kwargs_.items(): setattr(self, k, v)  # Dado que kwargs no deberia utilizarse por fuera es que no se verfican los parametros recibidos
        self.fx_elem, self._groupby, self.key = [], '-', None
        self.method_speed= self.f_method*10+1
        self.f_method=getattr(self,'f_method_'+str(self.f_method))  # analizar si conviene ponerlo en __set_up__


    def axis(self, axis:int):  # Para cambiar el axis tengo que hacer fx_object.axis(#)
        self._axis=axis
        return self
    
    @property
    def joint(self):  # Necesito esta funcion para que no falle la llamada a la funcion np.all or np.any
        return np.all if self.cond==op.and_ else np.any

    """
    @staticmethod
    def check_and_instanciate(var):  # podría llamarse 'only' (as in: it's fx the type allways return) o tambien to_fx, rturn, bring
        return (var if isinstance(var,fx) else fx(var)).__set_up__()
    """
    @staticmethod
    def build(var, key=None):
      # var=fx.check_and_instanciate(var)
        var = (var if isinstance(var,fx) else fx(var)).__set_up__()
        if var.built == True: return var
        var.built=True
        if var.key==None: var.key=key
        var.tot_speed = reduce(lambda x, y: x+fx.build(y,key).tot_speed, [var.method_speed]+var.fx_elem)
        return var._total_qty_()

    def _total_qty_(self):
        self.tot_qty = reduce(lambda x, y: x + y._total_qty_().tot_qty, [self.qty-len(self.fx_elem)]+self.fx_elem )
        self.tot_and_qty = reduce(lambda x, z: x + (z.tot_and_qty if z.cond==op.and_ and z.qty>1 else 0), [self.qty if self.cond==op.and_ and self.qty>1 else 0]+self.fx_elem )
        # concat_qty
        return self

    def __set_up__(self):  # podría cambiar el nombre por __fx_set_up__
        for i in range(len(self.elem)-1,-1,-1):  # podria usarse reversed(range)
            if isinstance(self[i],fx): self.fx_elem += [self.pop(i)]
        self.filter_method_tweak()
        self.qty = (0 if self.f_method==None else 1) + len(self.fx_elem)
        return self


    def filter_method_tweak(self):
        if self.tweaked==False:
            self.tweaked=True
            if len(self.elem)==0:
                if self.f_method==self.f_method_0: self.f_method = None  # Si no es f_method_0 no entra en ninguna opcion, por tanto va a aplicar el metodo correspondiente
            elif len(self.elem)==1 and not isinstance(self.elem[0], (list, tuple)): # en esos formatos (y habria que chequear is otros también) no funciona arrays vectorize sino pandas isin
                # Cuando entra acá se aplica 'vectorize with numpy arrays' (con f_method_0 por defecto)
                pass  # necesito esta opcion para evitar que entre en pd_isin en los casos en que no sea una instancia de las listadas
            elif len(self.elem)>1 and self.oper in [op.eq, op.ne] and (isinstance(self.elem[0], (set,dict)) or ( len(self.elem)<26 and all(map(lambda x: isinstance(x, (float, int)), self.elem)) ) ):
                self.oper, self.method_speed = np.in1d, (2+len(self.elem))*(5 if isinstance(self.elem[0], (set,dict)) else 1)   # solo necesito cambiar el operador ya que el metodo por defecto sirve para aplicar np.in1d
            else:
                def pd_isin(df, key, idx): return (df[key] if idx[0]==None else df[key].iloc[idx]).isin(self.elem)
                self.f_method, self.method_speed = pd_isin, 20+len(self.elem)*5 # le guardo el puntero a la funcion creada en la linea anterior
                
                
    def filter_apply(self, df, key, idx=[None]):
        if self.invert: return ~self.f_method(df, key, idx)
        return self.f_method(df, key, idx) 
    
    
    # ------
    
    def f_method_0(self, df, key, idx):
        return self.oper(df[key].values if idx[0]==None else df[key].values[idx], self.elem if len(self.elem)>1 else self[0])
    
    @classmethod
    def ne(cls,*args):  # !=
        return cls(*args, oper=op.eq, invert=not cls.invert)
        
    @classmethod
    def le(cls,*args):  # <=
        return cls(*args, oper=op.le)
    
    @classmethod
    def lt(cls,*args):  # <
        return cls(*args, oper=op.lt)
        
    @classmethod
    def ge(cls,*args):  # >=
        return cls(*args, oper=op.ge)
    
    @classmethod
    def gt(cls,*args):  # >
        return cls(*args, oper=op.gt)
    
    # ------
    
    def f_method_1(self, df, key, idx):
        self.elem.append(self.oper(df[key].values if idx[0]==None else df[key].values[idx]))
        self.oper = op.eq
        return self.f_method_0(df, key, idx)
    
    @classmethod
    def max(cls):  # max
        return cls(oper=np.nanmax, f_method=1)
    
    @classmethod
    def min(cls):  # min
        return cls(oper=np.nanmin, f_method=1)
    
    @classmethod
    def apply_func(cls, oper):
        ## possible oper options: np.nanmedian, nanmean, nanstd, nanvar, nanquantile, nanpercentile, average, etc.    
        return cls(oper=oper, f_method=1)
    
    # ------
        
    @classmethod
    def rng(cls, lower, higher, incl_lower=True, incl_higher=True):  # ?? usar no en lugar de fx para el inverso
        lower=  (cls.ge if incl_lower else cls.gt)(lower)
        higher= (cls.le if incl_higher else cls.lt)(higher)
        return (y if not cls.invert else fx)(lower, higher)
    
    @classmethod  
    def dev(cls, from_, extent, incl_lower=True, incl_higher=True):
        return cls.rng(from_-extent, from_+extent, incl_lower=incl_lower, incl_higher=incl_higher)
    
    # ------
    
    def f_method_2(self, df, key, idx):
        filtro=partial( getattr((df[key] if idx[0]==None else df[key].iloc[idx]).str,self.oper), self[0])
        if '_case' in self.__dict__ and '_regex' in self.__dict__:
            return filtro(self._case, regex=self._regex)
        return filtro()
        
    @classmethod
    def contains(cls, *args, _case=True, _regex=True):
        return cls(*args, oper='contains', f_method=2)

    @classmethod
    def sw(cls, *args):
        return cls(*args, oper='startswith', f_method=2)  # 'startswith' es por pd.Series.str.startswith.__name__ a utilizar con python's built-in setattr() function
    
    @classmethod
    def ew(cls, *args):
        return cls(*args, oper='endswith', f_method=2)  # 'endswith' es por pd.Series.str.endswith.__name__ a utilizar con python's built-in setattr() function
    
    
    # ------

    def groupby(self, grpby_key):  # Para agregar groupby tengo que hacer fx_object.groupby(key string)
        self._groupby=grpby_key
        self.op_group=2              #############  CORREGIR  !!!!!!!!!!!!!
        return self
    """
        def oper(df,key): return df.groupby(grpby_key)[key]
        self._groupby=groupby
        self.op_group=2
        
        return filter_apply(key, (no if fx_obj.invert else fx)( *groupby_apply(
            df.groupby(fx_obj._groupby)[key], fx_obj.oper) ).__set_up__())
        return self
    
    def groupby_apply(grpby,op): # no funciona con sets, listas o diccionarios. Sí funciona con tuplas
        if op==fx.max().oper: return grpby.max().values
        elif op==fx.min().oper: return grpby.min().values
    """

    # ------

    def __getitem__(self, index):  # consigo el elemento en base al indice haciendo fx_object[i]
        return self.elem[index]
    
    def __setitem__(self, index, value):
        self.elem[index]=value
    
    def __delitem__(self, index):
        del self.elem[index]
        
    def pop(self,i=-1):  # retorna el último elemento y luego lo elimina de la lista haciendo fx_object.pop()
        return self.elem.pop(i)
    
    def add(self, value):
        self.elem= self.elem+[value]
            
    def __contains__(self, value): # consigo evaluar si un elemento está en el listado haciendo value in fx_object
        return value in self.elem

    def __iter__(self):  # consigo iterar los elementos haciendo for i in fx_object
        return iter(tuple(self.elem))

    def __call__(self, i=0):  # consigo la lista de elementos haciendo fx_object()
        if i==0: return self.elem
        if i==1: return self.fx_elem
        if i==2: return self.fx_elem2
    
    def __lt__(self, other):  # Es necesario para ordenar
        if self.tot_speed < other.tot_speed:
            return True
        elif self.tot_speed == other.tot_speed:
            return True if self.tot_qty < other.tot_qty else False
        return False
    
    def __eq__(self, other):   ### ??? falta resolver
        if self.build().elem==other.build().elem and self.fx_elem==other.fx_elem and self.cond==other.cond and self.f_method==other.f_method: ##faltan mas
            return True  # usar self.d para obtener la lista de atributos y recorrerlas
        return False
    
    @property
    def d(self):
        print(self.__dict__)
    
    @property
    def p(self):
        x=fx.build(self)
        print(' FX OBJECT',x.info())
        for i in range(len(x.fx_elem)-1,-1,-1): 
            print('\n FX ELEMENT IN FX OBJECT:')
            x.fx_elem[i].p

    def info(x): # x es self  ## def __str__(self):
        return ( 'Id: {} \n ------------------------------------------------ \n'.format(str(x))+
                (' joint: np.{} ( condition: {} )   axis: {}   groupby: {} \n oper: {}   invert: {}  '+
                 ' lista: {} \n method: {}  method_speed: {}  total_speed: {} \n Nº elem y fx_elem: {}, {}   '+
                 '( qty(Nº yields): {}   total qty: {} ) \n elementos: {} \n fx_elementos: {}').format(str(x.joint)[10:13], 
                x.cond, x._axis, x._groupby, x.oper, x.invert, x.lista, (x.f_method.__name__ if x.f_method!=None else None),
                x.method_speed, x.tot_speed, len(x.elem), len(x.fx_elem), x.qty, x.tot_qty, x.elem, x.fx_elem)+
                 '\n key: {}   total oper.and qty: {}'.format(x.key, x.tot_and_qty)).replace('__main__.',' ')


    
class y(fx):
    cond=op.and_ #np.all
        
class o(fx):
    cond=op.or_ #np.any

class l(fx):  # necesito esta clase en caso de que el elemento con el que se evalua sea una lista
    lista=True
    class y(y):
        lista=True
    class o(o):
        lista=True

class no(fx): # El valor invert no va a ser correcto cuando se hacen las encadenaciones no.l.[y/o].op
    invert=not fx.invert    
    class y(y):
        invert=not y.invert
    class o(o):
        invert=not o.invert
    class l(l):
        invert=not l.invert
        
def filtrar(df, f_axis=0, filtersDict={}, **filters):
    filters.update(filtersDict)
 #  filters = fx.build( y([fx.build(val,key) for key,val in filters.items()]) )
    filters = [fx.build(val,key) for key,val in filters.items()]
 #    tiene que ser tot_speed>.3 y tot_qty>2

    """
    lst = list(fx.build(val,key) for key,val in filters.items())
    if len(lst)>2:
        for i in range(2,len(lst)):
            if lst[i].tot_speed>=40:
                fx_stack_acum = fx.build(y(lst[i:]))
                break
    fx_stack = fx.build(y(lst[:i]))
    
    """
    if len(filters)>2:  # and filters.tot_speed>42:
        filters.sort()
        flag=False
        for i in range(len(filters)-1,1,-1):
            if filters[i].tot_speed<35:
                fx_stack_acum = fx.build( y(filters[i:]) )
                fx_stack = fx.build( y(filters[:i]) )
                flag = True
                break
    else:
        filters = fx.build( y(filters) )

    
    def stack(fx_obj):
        if fx_obj.f_method!=None: 
            yield fx_obj.filter_apply( df, fx_obj.key)  #, index)
        for element in fx_obj.fx_elem: yield process(element)
        
    def stack_acum(fx_obj, index):
        if fx_obj.f_method!=None: 
            index= index[fx_obj.filter_apply(df, fx_obj.key, index)]
        for element in fx_obj.fx_elem: 
            index=stack_acum(element,index)
        return index
            
    """
        GUARDAR EL OBJ.KEY EN UNA CLASE CRUZADA !!!!!!!!!!!!!!!!!!!!!!!!!!!
    """
   
    def process(fx_obj)->np.array:
 #  def sub_process(list_of_fx_elem):
        if fx_obj.qty==1: return        next( stack(fx_obj) )
        if fx_obj.qty==2: return fx_obj.cond(*stack(fx_obj) )   #### CHEQUEAR ESTA LINEA POR EL AXIS!
        return fx_obj.joint( list(stack(fx_obj)), axis=fx_obj._axis )

        #func=partial(stack,fx_obj)
    if isinstance(filters,fx):
        return df[process(filters)]
    else:
        if flag==True:
            index=np.arange(df.shape[0])  # Como alternativa len(df) y len(df.columns) para la cant de columnas
            return df.iloc[ stack_acum(fx_stack_acum, index[process(fx_stack)] ) ]
        else:
            return df[process( fx.build( y(filters) ) ) ] 

  # return process(filters)
   # return (df.iloc if filters.tot_and_qty>2 else df)[ process(filters) ]  #por ahora uso loc pero deberia ser iloc



def groupby_apply(grpby,op): # no funciona con sets, listas o diccionarios. Sí funciona con tuplas
    if op==fx.max().oper: return grpby.max().values
    elif op==fx.min().oper: return grpby.min().values
    #elif op==mean: return grpby.mean().values
    #elif op == std: return grpby.std().values


