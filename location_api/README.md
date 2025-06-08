# Location API Service

This service provides an API endpoint to search for locations. It's part of the weather application.

## Prerequisites

- Go (version 1.20 or higher recommended)

## Running the service

1.  Open your terminal.
2.  Navigate to the `location_api` directory within your `weather_app` project:
    ```bash
    cd /path/to/your/weather_app/location_api
    ```
    (Replace `/path/to/your/` with the actual path to your project, e.g., `/home/tylerthecreaton/Sites/weather_app/location_api`)

3.  Ensure Go modules are up to date (this step is usually needed if you add external dependencies, but good practice):
    ```bash
    go mod tidy
    ```

4.  Run the service:
    ```bash
    go run main.go
    ```

The server will start, and you should see output like:
`Location API server starting on http://localhost:8081`
`Try accessing: http://localhost:8081/api/search-locations?query=jap`

## Testing the Endpoint

Once the server is running, you can test the endpoint by opening the following URL in your web browser or using a tool like `curl`:

-   For English query: `http://localhost:8081/api/search-locations?query=jap`
-   For Thai query: `http://localhost:8081/api/search-locations?query=เชียงใหม่`

You should receive a JSON response with location suggestions based on the mock data.

## Project Structure

-   `main.go`: Entry point of the application, sets up the HTTP server and routes.
-   `go.mod`: Defines the module and its dependencies.
-   `handlers/`: Contains HTTP request handlers.
    -   `location_handler.go`: Handles logic for the `/api/search-locations` endpoint.
-   `models/`: Contains data structures (structs).
    -   `location.go`: Defines the `LocationSuggestion` struct.

## Next Steps

-   Integrate a real external geographical API (e.g., GeoNames) to replace the mock data in `location_handler.go`.
-   Implement more robust error handling and logging.
-   Add unit tests.
