# distutils: language = c++
# Module made by Aleix Cotaina Escriva - XScript v3 (Ultra High Speed)

from cpython.ref cimport PyObject, Py_INCREF, Py_DECREF
from libcpp.unordered_map cimport unordered_map
from libcpp.string cimport string
from libcpp.vector cimport vector

# --- OBJETO UNIFICADO ---
cdef class XSObject:
    cdef public int kind   # 1 = FUNC, 2 = VAR
    cdef public object value
    
    def __init__(self, int kind, object value):
        self.kind = kind
        self.value = value

# El mapa ahora guarda punteros a PyObject para evitar errores de compilación
ctypedef unordered_map[string, PyObject*] ScopeMap

# --- LA CLASE MAESTRA REFACTORIZADA ---
cdef class Defines:
    cdef vector[ScopeMap] stack
    cdef ScopeMap global_map

    def __init__(self) -> None: 
        pass

    cpdef find_define(self, str name):
        cdef string c_name = name.encode('utf-8')
        cdef int i
        cdef PyObject* ptr
        
        # Búsqueda en la pila de ámbitos (C++ nativo)
        for i in range(self.stack.size() - 1, -1, -1):
            if self.stack[i].count(c_name):
                ptr = self.stack[i][c_name]
                return <object>ptr  # Casting de puntero a objeto Python

        # Búsqueda en el ámbito global
        if self.global_map.count(c_name):
            ptr = self.global_map[c_name]
            return <object>ptr

        return None

    cpdef add_scope(self):
        cdef ScopeMap new_scope
        self.stack.push_back(new_scope)
    
    cpdef remove_scope(self):
        if self.stack.empty():
            raise RuntimeError("There are no local scopes left to remove")

        cdef ScopeMap last_scope = self.stack.back()
        cdef PyObject* ptr

        for item in last_scope:
            ptr = item.second
            Py_DECREF(<object>ptr)

        # Ahora sí, borramos el contenedor de C++ con seguridad
        self.stack.pop_back()
        
    cpdef set_object(self, int kind, str name, object value):
        cdef string c_name = name.encode('utf-8')
        cdef XSObject obj = XSObject(kind, value)
        
        # Incrementamos referencia para que Python no destruya el objeto 
        # mientras el mapa de C++ tenga su puntero
        Py_INCREF(obj)
        
        if self.stack.empty():
            self.global_map[c_name] = <PyObject*>obj
        else:
            self.stack.back()[c_name] = <PyObject*>obj