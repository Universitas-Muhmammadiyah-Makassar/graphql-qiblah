# Solar and Qibla Direction Calculator API

This is a Flask-based GraphQL API that calculates the solar position and Qibla direction based on the given latitude, longitude, and datetime. The API is implemented using Strawberry GraphQL.

## Features

- Calculate the solar position (elevation, azimuth) for a given location and time.
- Calculate the Qibla direction from a given location.
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

Here is an example mutation you can run in the GraphiQL interface to calculate the solar position and Qibla direction:

```graphql
mutation {
  calculateSolar(locationData: {
    latitude: "5° 11' 25.8\" S",
    longitude: "119° 27' 3.24\" E",
    datetimeStr: "2024/07/31 17:27:00"
  })
}
```

### Response

The API will return a string containing the solar position and Qibla direction:

```json
{
  "data": {
    "calculateSolar": "Local Time: 2024/07/31 17:27:00 (Asia/Makassar - WITA)\nUTC Time: 2024/07/31 09:27:00\nQibla Direction: 292.48° from the North\nSolar Elevation: 8.31°\nSolar Azimuth: 289.16°\nShadow Azimuth: 109.16°\nSolar Azimuth and Qibla Difference: 3.32°\nShadow Azimuth and Qibla Difference: 176.68°"
  }
}
```

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

