class VivadoProperty:
    def __init__(self, name, ro=False):
        self.name = name
        self.ro = ro
        
    def __get__(self, instance, owner=None):
        if instance is None:
            return self
        return instance.get_property(self.name)

    def __set__(self, instance, value):
        if self.ro:
            raise AttributeError(f"Property {self.name} is read only")
        return instance.set_property(self.name, value)
        
