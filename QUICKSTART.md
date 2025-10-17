# Quick Start Guide

Get the Smart City Data Generator running in 5 minutes!

## 1. Prerequisites

- Docker & Docker Compose
- Python 3.8+
- pip

## 2. Quick Setup

```bash
# Clone the repository
git clone https://github.com/nuttooo/generate-data-for-smart-city.git
cd generate-data-for-smart-city

# Start PostgreSQL database
docker compose up -d

# Install Python dependencies
pip install -r requirements.txt

# Setup environment
cp .env.example .env
```

## 3. Generate Data

```bash
# Generate single data cycle
python main.py generate

# Start continuous generation (every 60 seconds)
python main.py continuous

# Or with custom interval (every 30 seconds)
python main.py continuous 30
```

## 4. Control Smart Poles

```bash
# Turn on a pole
python main.py control SP001 on

# Turn off a pole
python main.py control SP002 off

# Toggle pole status
python main.py control SP003 toggle

# List all poles
python main.py list

# View latest data
python main.py view
```

## 5. Query the Database

```bash
# Connect to database
docker compose exec postgres psql -U admin -d smart_city

# View latest energy data
SELECT * FROM smart_pole_energy ORDER BY timestamp DESC LIMIT 10;

# View weather data
SELECT * FROM weather_station ORDER BY timestamp DESC LIMIT 10;

# Exit psql
\q
```

## 6. Stop Everything

```bash
# Stop database
docker compose down

# Remove all data (optional)
docker compose down -v
```

## Common Commands

```bash
python main.py help              # Show help
python main.py list              # List smart poles
python main.py view              # View latest data
python main.py generate          # Generate single cycle
python main.py continuous        # Start continuous generation
python main.py control SP001 on  # Control specific pole
./test.sh                        # Run automated tests
```

## What's Included?

- **5 Smart Poles** with different module configurations
- **Weather Station** with realistic Bangkok climate data
- **Module Types**: Lighting, Camera, Sensors, WiFi, Display, EV Charging
- **Realistic Power Simulation** based on time and weather
- **PostgreSQL Database** for data storage
- **CLI Interface** for easy control

## Next Steps

- Read [README.md](README.md) for detailed documentation
- Check [DEMO.md](DEMO.md) for comprehensive demo guide
- Explore [example_queries.sql](example_queries.sql) for data analysis
- Run `./test.sh` to verify everything works

## Troubleshooting

**Can't connect to database?**
```bash
docker compose ps  # Check if postgres is running
docker compose logs postgres  # View logs
```

**Module not found error?**
```bash
pip install -r requirements.txt  # Reinstall dependencies
```

**Permission denied on test.sh?**
```bash
chmod +x test.sh  # Make it executable
```

## Support

For issues or questions, please open an issue on GitHub.

Enjoy exploring smart city data! 🌆✨
