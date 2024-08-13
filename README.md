# Solar and Qibla Direction Calculator API

This is a Flask-based GraphQL API that calculates the solar position and Qibla direction based on the given latitude and longitude. The API is implemented using Strawberry GraphQL.

## Features

- Calculate the solar position (elevation, azimuth) for a given location and time.
- Calculate the Qibla direction from a given location.
- Optionally use the current time if no specific datetime is provided.
- Built with Strawberry GraphQL and Flask for a simple and efficient API.

## Requirements

- Python 3.10+
- Flask
- Strawberry GraphQL
- PyEphem
- TimezoneFinder
- Pytz

## Installation

1. **Clone the repository:**

   ```bash
   git clone https://github.com/yourusername/solar-qibla-calculator.git
   cd solar-qibla-calculator
   ```

2. **Create a virtual environment (optional but recommended):**

   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. **Install the required packages:**

   ```bash
   pip install -r requirements.txt
   ```

   If the `requirements.txt` file doesn't exist, you can install the dependencies manually:

   ```bash
   pip install flask strawberry-graphql ephem timezonefinder pytz
   ```

## Usage

1. **Run the Flask server:**

   ```bash
   python app.py
   ```

2. **Access the API:**

   Open your browser and go to `http://127.0.0.1:5000/graphql`. You will see the GraphiQL interface where you can test the API.

## Example Query

You can use the following query to calculate the solar position and Qibla direction based on latitude and longitude:

```graphql
query {
  calculateSolar(
    latitude: "5° 11' 25.8\" S", 
    longitude: "119° 27' 3.24\" E"
  )
}
```

### Parameters

- **latitude**: The latitude of the observation location in DMS (Degrees, Minutes, Seconds) format. For example, `"5° 11' 25.8\" S"`.
- **longitude**: The longitude of the observation location in DMS format. For example, `"119° 27' 3.24\" E"`.
- **datetimeStr** (optional): The date and time of the observation in the format `YYYY/MM/DD HH:MM:SS`. If not provided, the current date and time will be used automatically.

### Response

The API will return a string containing detailed information about the solar position, Qibla direction, and distance from the specified location to the Ka'bah:

```json
{
  "data": {
    "calculateSolar": "1. Koordinat Lokasi Pengamatan: ..."
  }
}
```

This response includes:
- The coordinates of the observation location and the Ka'bah.
- Conversion of coordinates from DMS to decimal degrees and radians.
- The Qibla direction in degrees.
- The distance to the Ka'bah in kilometers.

## Project Structure

- **app.py**: Main application file that sets up the Flask server and defines the GraphQL schema and resolvers.
- **requirements.txt**: File listing all the dependencies required for the project.

## Contributing

Contributions are welcome! Please fork the repository and submit a pull request with your changes.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [Strawberry GraphQL](https://strawberry.rocks/)
- [Flask](https://flask.palletsprojects.com/)
- [PyEphem](https://rhodesmill.org/pyephem/)
- [TimezoneFinder](https://pypi.org/project/timezonefinder/)
