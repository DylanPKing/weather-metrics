# Weather Metrics Tracker
A simple FastAPI project to take in basic weather data and calcuate statistics from specific sensors.

## Running
1. Clone the repo
2. Run using docker:
```bash
docker compose up -d --build
```
> This should build the `uv` container the app runs in, and pull the required postgres DB image.
3. Apply DB migrations:
```bash
docker exec -it weather-metrics alembic upgrade head
```
> On creation the DB will be empty. Before adding readings you will need to create sensors by making POST requests against the /v1/sensors endpoint.
## Interacting with the server
curl requests to localhost:8000 will work, or visit localhost:8000/docs to access a swagger documentation page with an API sandbox.

## Testing
```bash
docker exec -it weather-metrics pytest
```

## Caveats
* The DB has 2 tables - `weathersensors` and `weatherreadings`. The small scope of this project means the sensors table isn't really necessary.
* Type hinting is used where possible, but `mypy` has it's limitations. e.g. the `match` statement in the `get_sensor_data` method has a bunch of `ignore` flags to suppress `mypy` errors due to how it interprets the type of the `db_func` variable.
* I'm not the biggest fan of how I implemented that endpoint - I don't like using `getattr` but without it would have made for a clunkier `match` statement above.
* Depending on the editor you view this project in you'll likely see a deprecation warning for the `session.execute` call. The warning is stating that `.exec()` is preferred as it returns scalars. This is good for when you are querying an entire table row but when performing calculation like in this case the `execute` approach is better as it retains all information returned by the DB.
* The use of Pydantic for the ORM models and request params ensures type safety. It checks all request params and response data for the correct type before the request processing begins, and before returning a response.
* Wind speed and temperature do not specifiy unit type. Given more time I would have added a config table to the DB to store the preferred unit types, and the ability to convert between different types. (Celsius -> Fahrenheit, k/mh -> mph, etc.)
 