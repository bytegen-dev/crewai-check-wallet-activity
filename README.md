# Cardano Wallet Activity Analyzer

This project uses CrewAI to analyze Cardano wallet transactions and provide detailed summaries of wallet activity over different time periods.

## Features

- Analyze wallet transactions for the last 30 days, 7 days, and 24 hours
- Calculate total ADA received and spent
- Provide net flow analysis
- Generate insights about wallet activity patterns

## Setup

1. Clone the repository
2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Create a `.env` file in the project root and add your BlockFrost API key:

   ```
   BLOCKFROST_API_KEY=your_api_key_here
   ```

   You can get a BlockFrost API key by signing up at [BlockFrost.io](https://blockfrost.io/)

## Usage

Run the script:

```bash
python wallet_analyzer.py
```

Enter a Cardano wallet address when prompted, and the script will:

1. Fetch transaction data for the last 30 days, 7 days, and 24 hours
2. Calculate total ADA received and spent for each period
3. Generate a detailed analysis of the wallet's activity

## Output

The script will provide:

- Monthly statistics (last 30 days)
- Weekly statistics (last 7 days)
- Daily statistics (last 24 hours)
- Insights about the wallet's activity patterns

## Requirements

- Python 3.7+
- BlockFrost API key
- Internet connection to fetch blockchain data
