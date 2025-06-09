import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database configuration
DB_URI = "mysql+pymysql://{}:{}@{}/{}".format(
    os.getenv("DB_USER"),
    os.getenv("DB_PASSWORD"),
    os.getenv("DB_HOST"),
    os.getenv("DB_NAME"),
)

# Dashboard configuration
DEFAULT_TIME_RANGE = "Last 24 Hours"
REFRESH_INTERVALS = [30, 60, 120, 300]
DEFAULT_REFRESH_INTERVAL = 60

# Temperature thresholds
TEMP_WARNING_THRESHOLD = 150
TEMP_DANGER_THRESHOLD = 250

# Performance thresholds
PERFORMANCE_WARNING_THRESHOLD = 70
QUALITY_WARNING_THRESHOLD = 95
OEE_WARNING_THRESHOLD = 70
