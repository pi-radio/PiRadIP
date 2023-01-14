class VLNVRegistry:
    @classmethod
    def register(cls, subcls):
        if not hasattr(cls, "registry"):
            cls.registry = dict()
        assert(subcls.vlnv not in cls.registry)
        cls.registry[subcls.vlnv] = subcls
        return subcls
            
    @classmethod
    def create_class(cls, name, vlnv):            
        return cls.register(type(name, (cls, ), { 'vlnv': vlnv }))

    @classmethod
    def construct(cls, vlnv, *args, **kwargs):
        return cls.registry[vlnv](*args, **kwargs)

    @classmethod
    def create_new(cls, vlnv, *args, **kwargs):
        c = cls.construct(vlnv, *args, **kwargs)
        c.create()
        return c
