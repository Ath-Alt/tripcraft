from django_elasticsearch_dsl import Document, Index, fields
from django_elasticsearch_dsl.registries import registry
from .models import Trip

trip_index = Index('trips')
trip_index.settings(number_of_shards=1, number_of_replicas=0)

@registry.register_document
class TripDocument(Document):
    class Index:
        name = 'trips'
    
    class Django:
        model = Trip
        fields = ['name', 'destination', 'duration', 'date', 'color']