ARG IMAGE_TAG=latest

FROM ghcr.io/nationalarchives/tna-python:"$IMAGE_TAG"

# Copy in the application code
COPY --chown=app . .

# Install the dependencies
RUN tna-build

# Run the application
CMD ["tna-run", "-a", "etna-search-api:app"]
