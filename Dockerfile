ARG IMAGE_TAG=latest

FROM ghcr.io/nationalarchives/tna-python:"$IMAGE_TAG"

# Copy in the dependencies config
COPY --chown=app pyproject.toml poetry.lock ./

# Install the dependencies
RUN tna-build

# Copy in the application code
COPY --chown=app . .

# Run the application
CMD ["tna-run", "-a", "etna-search-api:app"]
