from flask import Flask, request, jsonify

from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool

from hiku.engine import Engine
from hiku.result import denormalize
from hiku.sources import sqlalchemy as sa
from hiku.executors.sync import SyncExecutor
from hiku.validate.query import QueryValidator
from hiku.readers.graphql import read
from hiku.introspection.graphql import add_introspection

from tests.test_source_sqlalchemy import setup_db, get_graph, get_queries
from tests.test_source_sqlalchemy import SA_ENGINE_KEY, SyncQueries


app = Flask(__name__)


@app.route('/', methods=['POST'])
def handler():
    hiku_engine = app.config['HIKU_ENGINE']
    data = request.get_json()
    try:
        query = read(data['query'], data.get('variables'))
        validator = QueryValidator(app.config['GRAPH'])
        validator.visit(query)
        if validator.errors.list:
            result = {'errors': [{'message': e}
                                 for e in validator.errors.list]}
        else:
            result = hiku_engine.execute(app.config['GRAPH'],
                                         query,
                                         ctx=app.config['HIKU_CTX'])
            result = {'data': denormalize(app.config['GRAPH'], result, query)}
    except Exception as err:
        result = {'errors': [{'message': repr(err)}]}
    return jsonify(result)


if __name__ == "__main__":
    sa_engine = create_engine('sqlite://',
                              connect_args={'check_same_thread': False},
                              poolclass=StaticPool)
    setup_db(sa_engine)

    app.config['HIKU_ENGINE'] = Engine(SyncExecutor())
    app.config['HIKU_CTX'] = {SA_ENGINE_KEY: sa_engine}

    graph = get_graph(sa, get_queries(sa, SA_ENGINE_KEY, SyncQueries))
    graph = add_introspection(graph)
    app.config['GRAPH'] = graph

    app.run()
