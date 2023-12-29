from app.lib import cache, cache_key_prefix
from app.records import bp
from app.sources import DiscoveryRecords
from flask import request


@bp.route("/")
# @cache.cached(key_prefix=cache_key_prefix)
def index():
    """
    Search records
    ---
    tags:
      - records
    definitions:
      - schema:
          id: Record
          properties:
            name:
              type: string
              description: the group's name
    parameters:
      - in: query
        name: q
        schema:
          type: string
        description: The query sting to search with
    responses:
      200:
        description:
        content:
          application/json:
              schema:
                $ref: '#/definitions/Record'
    """
    discovery_api = DiscoveryRecords()
    if "q" in request.args:
        discovery_api.add_query(request.args.get("q"))
    else:
        discovery_api.add_query("*")
    results = discovery_api.get_results()
    return results


# @bp.route("/digitised")
# # @cache.cached(key_prefix=cache_key_prefix)
# def digitised():
#     """
#     Search digitised records
#     ---
#     tags:
#       - records
#     parameters:
#       - in: query
#         name: q
#         schema:
#           type: string
#         description: The query sting to search with
#     responses:
#       200:
#         description:
#         content:
#           application/json:
#               schema:
#                 $ref: '#/definitions/Record'
#     """
#     query = request.args["q"] if "q" in request.args else ""

#     return f"Heya, {query}"
