# ETD-Globe

🌍 ETD Globe — Earth Temperature Detective Globe

An interactive way to explore Earth's temperature patterns through data analysis and a 3D globe.

ETD Globe is a data-driven project developed for the 2026 NASA Space Apps Challenge, under the challenge “Be an Earth System Trend Detective.”

The project explores Earth's temperature patterns using environmental data and transforms the results into an interactive experience. By combining Python-based data analysis with a 3D globe visualization, ETD Globe helps users explore temperature variations across different regions of the planet.

---

🚀 Project Overview

Understanding Earth's climate system requires exploring environmental data across different locations and time periods.

ETD Globe focuses on near-surface air temperature and its spatial and temporal variations. The project processes temperature data, investigates regional patterns, identifies monthly changes, and presents the results through an interactive globe.

The main temperature variable used in this project is T2M, which represents air temperature at 2 meters above the Earth's surface.

The original temperature values are provided in Kelvin and converted to Celsius for easier interpretation.

---

🎯 Project Objectives

- Explore temperature patterns across different regions of Earth.
- Analyze monthly and seasonal temperature variations.
- Compare temperature behavior across selected geographical regions.
- Identify temperature anomalies within the available dataset.
- Present environmental data through an interactive 3D globe.
- Make Earth observation data easier to explore and understand.

---

🛰️ Data Description

The analysis uses environmental data containing temperature measurements and geographical coordinates.

Main variables include:

Variable| Description
"T2M"| Air temperature at 2 meters
"T10M"| Air temperature at 10 meters
"TS"| Earth skin temperature
"lat"| Latitude
"lon"| Longitude
"time"| Date and time information

The original dataset contains approximately:

- 500,000 records
- 37 monthly timestamps
- 190,554 unique geographical locations
- Time coverage: September 2020 – September 2023

Sample Dataset Included

A CSV file is included in this repository for demonstration and testing purposes.

Important: The included CSV file is only a small sample extracted and converted from the original dataset. It does not contain the complete dataset or all of its records.

The sample is provided to help users understand the dataset structure, inspect the available variables, and test the project more easily.

The analysis described in this project is based on the larger dataset used during development, not only on the small sample CSV included in the repository.

Data Source: (https://disc.gsfc.nasa.gov/datasets/M2IMNXASM_5.12.4/summary)
---

🧹 Data Preprocessing

Before analysis, the dataset goes through several preprocessing steps:

1. Loading and combining the available data files.
2. Inspecting the dataset structure and data types.
3. Handling missing values.
4. Converting date and time information into a consistent format.
5. Checking geographical coordinates.
6. Converting temperature values from Kelvin to Celsius.

The temperature conversion formula is:

[
T(°C) = T(K) - 273.15
]

---

📊 Data Analysis

Several analytical approaches are used to investigate temperature behavior:

- Temperature Distribution: Exploring the distribution of T2M, T10M, and TS.
- Monthly Analysis: Examining temperature changes across available months.
- Seasonal Analysis: Exploring seasonal and quarterly patterns.
- Regional Comparison: Comparing Greenland, the Sahara Desert, and the Amazon region.
- Temperature Anomalies: Investigating deviations from the dataset's monthly reference averages.
- Correlation Analysis: Exploring relationships between selected temperature variables and regions.
- Trend Exploration: Applying statistical analysis and linear regression to examine patterns in the available observations.

Selected Regional Analysis

The project compares three geographically different regions:

Region| Mean T2M
Greenland| -6.90°C
Sahara| 24.80°C
Amazon| 24.29°C

These values represent averages from the selected regional samples in the dataset.

---

🌐 ETD Globe — Interactive Visualization

ETD Globe presents the project through an interactive 3D Earth visualization.

Main Features

- 3D Earth Globe: Explore the planet through a globe-based interface.
- Automatic Rotation: The globe continuously rotates to provide a dynamic view.
- Mouse and Touch Interaction: Rotate and explore the globe manually.
- Zoom Interaction: Get a closer look at different areas.
- Country Exploration: Select countries to explore available geographical information.
- Temperature Insights: View temperature-related information and analytical results.
- Data Visualization: Explore temperature patterns through charts and visual summaries.

The goal is to make environmental data more accessible by connecting numerical analysis with geographical exploration.

---

🛠️ Technologies Used

Technology| Purpose
Python| Data processing and analysis
Pandas| Data manipulation
NumPy| Numerical operations
Jupyter Notebook| Exploratory data analysis
Streamlit| Interactive web application
Plotly| Data visualization
HTML / JavaScript / Canvas| Interactive globe interface
GeoJSON| Geographical boundaries

---

🔮 Future Improvements

Possible future developments include:

- Integrating longer historical temperature records.
- Adding more environmental variables.
- Improving geographical resolution and regional selection.
- Developing more advanced anomaly detection methods.
- Adding interactive time-based temperature exploration.
- Improving the globe's visualization and performance.
- Incorporating additional Earth observation datasets.

---

🏆 NASA Space Apps Challenge 2026

Challenge: Be an Earth System Trend Detective

Project: ETD Globe — Earth Temperature Detective Globe

ETD Globe aims to turn environmental data into an accessible and interactive experience, helping people explore Earth's temperature patterns and better understand the complexity of our planet's systems.

---

👩‍💻 Author

Mina — minaniazizade

GitHub: "@minaniazizade" (https://github.com/minaniazizade)

---

Exploring Earth, one data point at a time. 🌍
