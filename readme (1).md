# Transport Carbon Footprint Calculator

An interactive web application built with Streamlit that helps users calculate and visualize their monthly carbon footprint based on their daily commute and transportation choices.

## Features

- Calculate carbon emissions based on detailed vehicle specifications
- Support for various transportation modes:
  - Two-wheelers (Scooters, Motorcycles)
  - Three-wheelers
  - Four-wheelers (various car types)
  - Public transport (Taxi, Bus, Metro)
- Compare your emissions with alternative transport options
- Receive personalized sustainability recommendations
- Interactive visualizations and metrics

## Screenshots

*[Screenshots will be added here]*

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/transport-carbon-calculator.git
   cd transport-carbon-calculator
   ```

2. Create a virtual environment (optional but recommended):
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage

1. Run the Streamlit application:
   ```
   streamlit run temp.py
   ```

2. Open your web browser and go to the URL displayed in the terminal (typically http://localhost:8501)

3. Fill in your commute details:
   - Daily one-way distance
   - Commuting days per week
   - Commuting weeks per month
   - Type of transport (private/public/both)
   - Vehicle specifications

4. Click "Calculate Carbon Footprint" to see your results

## Calculation Methodology

The application uses emission factors for different vehicle types, sizes, and fuel types to calculate carbon footprint. These factors are based on typical CO₂ equivalent emissions per kilometer. Key factors that influence emissions include:

- Vehicle type (two-wheeler, three-wheeler, four-wheeler, public transport)
- Fuel type (petrol, diesel, CNG, electric)
- Engine size (cc)
- Ridesharing (number of people sharing the vehicle)
- For combined transport modes, the ratio of private to public transport usage

## Development

### Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

### To-Do

- [ ] Add more detailed emission factors based on vehicle age and maintenance
- [ ] Implement carbon offset suggestions
- [ ] Add yearly projections and historical tracking
- [ ] Create user accounts to save and compare multiple commute patterns
- [ ] Add walk/bicycle options for short distances

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgements

- Emission factor data compiled from multiple environmental research sources
- Built with [Streamlit](https://streamlit.io/)