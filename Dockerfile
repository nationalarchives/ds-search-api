FROM ghcr.io/nationalarchives/tna-python:latest

# Copy in the application code
COPY --chown=app . .

# Install the dependencies
RUN tna-build

# Run the application
CMD ["tna-run", "etna-search-api:app"]
