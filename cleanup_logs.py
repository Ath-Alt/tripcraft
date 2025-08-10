from datetime import datetime, timedelta, timezone
from elasticsearch import Elasticsearch

es = Elasticsearch("http://localhost:9200")

old_time = datetime.now() - timedelta(days=1)
formatted_old_time = old_time.strftime("%Y-%m-%dT%H:%M:%S")

query = {
    "query": {
        "range": {
            "@timestamp": {
                "lt": formatted_old_time
            }
        }
    }
}

res = es.delete_by_query(index="logstash-django", body=query)
print("Deleted", res['deleted'], "old logs")