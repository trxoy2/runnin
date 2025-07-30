# Strava ELT Project

This project is designed to extract, load, and transform data from the Strava API into a database. It utilizes Python for the ETL processes and SQL for database interactions, all managed within Docker containers.

## Project Structure

```
strava-elt-project
├── src
│   ├── extract.py       # Functions to connect to the Strava API and extract data
│   ├── load.py          # Functions to load extracted data into the database
│   ├── transform.py      # Functions to transform and clean data before loading
│   └── utils.py         # Utility functions for logging, error handling, etc.
├── sql
│   ├── create_tables.sql # SQL statements to create necessary database tables
│   └── insert_data.sql   # SQL statements for inserting transformed data
├── Dockerfile            # Instructions to build the Docker image
├── docker-compose.yml    # Configuration for Docker services
├── requirements.txt      # Python dependencies for the project
└── README.md             # Documentation for the project
```

## Setup Instructions

1. **Clone the Repository**
   ```bash
   git clone <repository-url>
   cd strava-elt-project
   ```

2. **Build the Docker Image**
   ```bash
   docker build -t strava-elt .
   ```

3. **Run the Application**
   ```bash
   docker-compose up
   ```

## Usage

- The `extract.py` module will connect to the Strava API and fetch activity data.
- The `transform.py` module will clean and format the data.
- The `load.py` module will insert the transformed data into the database.

## Dependencies

Ensure that the following dependencies are included in `requirements.txt`:

- requests
- SQLAlchemy
- pandas (if data manipulation is needed)

## License

This project is licensed under the MIT License. See the LICENSE file for more details.