# FROM ghcr.io/nationalarchives/tna-python:latest
FROM tna-python-async

# Copy in the application code
COPY --chown=app . .

# Install the dependencies
RUN tna-build

# Run the application
CMD ["tna-run", "-a", "etna-search-api:app"]
