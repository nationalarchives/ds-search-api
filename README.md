# beta.nationalarchives.gov.uk search API

## Quickstart

```sh
docker-compose up -d
```

Docs available on: http://localhost:65534/docs

## Environment variables

In addition to the [base Docker image variables](https://github.com/nationalarchives/docker/blob/main/docker/tna-python/README.md#environment-variables), this application has support for:

| Variable            | Purpose                                                                | Default |
| ------------------- | ---------------------------------------------------------------------- | ------- |
| `DEBUG`             | If true, allow debugging[^1]                                           | `False` |
| `LOG_LEVEL`         | The log level to stream to the console[^2]                             | `info`  |
| `DISCOVERY_API_URL` | The base URL of the Discovery API, including the `/API/search/v1` path | _none_  |
| `WAGTAIL_API_URL`   | The base URL of the content API, including the `/api/v2` path          | _none_  |

[^1] [Debugging in Flask](https://flask.palletsprojects.com/en/2.3.x/debugging/)
[^2]: Supported levels are `critical`, `error`, `warn`, `info` and `debug` [Gunicorn docs - log level](https://docs.gunicorn.org/en/latest/settings.html?highlight=log#loglevel)
