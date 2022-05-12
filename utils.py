import warlock


class utils:
    def __init__(self):
        self. schema = {
            'name': 'Search',
            'properties': {
                'id': {'type': 'string'},
                'titulo': {'type': 'string'},
                'subtitulo': {'type': 'string'},
                'autor': {'type': 'string'},
                'categoria': {'type': 'string'},
                'fecha_publicacion': {'type': 'string'},
                'editor': {'type': 'string'},
                'descripcion': {'type': 'string'},
                'fields': {'type': 'string'},
            },
            'additionalProperties': False,
        }

    def validation_fields(self,json):
        Search = warlock.model_factory(self.schema)
        try:
            return Search(json)
        except Exception as e:
            return e
