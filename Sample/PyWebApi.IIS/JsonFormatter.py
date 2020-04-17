
from jsonpickle import dumps
from pywebapi import MediaTypeFormatter


class JsonFormatter(MediaTypeFormatter):
    """description of class"""

    @property
    def supported_media_types(self):
       return ['application/json', 'text/json']


    def can_support_media_types(self, media_types:str) -> set:
        if not media_types:  # Makes JSON as the default MediaType
            return {this.supported_media_types[0]}
        return super().can_support_media_types(media_types)


    def format(self, obj, media_type:str, **kwargs):
        kwargs['unpicklable'] = kwargs.get('unpicklable', False)
        return dumps(obj, kwargs)
