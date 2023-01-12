class VLNVRegistry:
    @classmethod
    def create_class(cls, name, vlnv):
        if not hasattr(cls, "registry"):
            cls.registry = dict()
            
        assert(vlnv not in cls.registry)
        cls.registry[vlnv] = type(name, (cls, ), { 'vlnv': vlnv })
        return cls.registry[vlnv]

    @classmethod
    def construct(cls, vlnv, *args, **kwargs):
        return cls.registry[vlnv](*args, **kwargs)
