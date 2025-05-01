from crewai import Agent, Task, Crew, Process
from datetime import datetime, timedelta
from blockfrost import BlockFrostApi
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class WalletAnalyzer:
    def __init__(self, wallet_address):
        self.wallet_address = wallet_address
        self.api = BlockFrostApi(project_id=os.getenv('BLOCKFROST_API_KEY'))
        
    def get_transactions(self, days=60, page=1):
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        try:
            # Get all transactions for the wallet with pagination
            all_transactions = []
            page = 1
            while True:
                transactions = self.api.address_transactions(self.wallet_address, page=page)
                if not transactions:
                    break
                all_transactions.extend(transactions)
                page += 1
                
            print(f"Found {len(all_transactions)} total transactions")
            
            # Filter transactions by date range
            filtered_transactions = []
            for tx in all_transactions:
                tx_time = datetime.fromtimestamp(tx.block_time)
                print(f"Transaction {tx.tx_hash} at {tx_time}")
                if start_date <= tx_time <= end_date:
                    filtered_transactions.append(tx)
                    print(f"Including transaction {tx.tx_hash} in analysis (within {days} days)")
            
            print(f"Found {len(filtered_transactions)} transactions in the specified date range")
            return filtered_transactions
        except Exception as e:
            print(f"Error fetching transactions: {str(e)}")
            return []
    
    def analyze_transactions(self, transactions):
        total_received = 0
        total_spent = 0
        
        for tx in transactions:
            try:
                # Get transaction details
                tx_details = self.api.transaction_utxos(tx.tx_hash)
                print(f"Analyzing transaction {tx.tx_hash}")
                
                # Check if the wallet is the receiver
                for output in tx_details.outputs:
                    if output.address == self.wallet_address:
                        # Find the ADA amount in the transaction
                        ada_amount = next((int(asset.quantity) / 1000000 for asset in output.amount if asset.unit == 'lovelace'), 0)
                        total_received += ada_amount
                        if ada_amount > 0:
                            print(f"Received {ada_amount} ADA in transaction {tx.tx_hash}")
                
                # Check if the wallet is the sender
                for input in tx_details.inputs:
                    if input.address == self.wallet_address:
                        # Find the ADA amount in the transaction
                        ada_amount = next((int(asset.quantity) / 1000000 for asset in input.amount if asset.unit == 'lovelace'), 0)
                        total_spent += ada_amount
                        if ada_amount > 0:
                            print(f"Spent {ada_amount} ADA in transaction {tx.tx_hash}")
            except Exception as e:
                print(f"Error analyzing transaction {tx.tx_hash}: {str(e)}")
        
        return {
            'total_received': total_received,
            'total_spent': total_spent,
            'net_flow': total_received - total_spent
        }

def create_wallet_analyzer_agent():
    return Agent(
        role='Wallet Activity Analyzer',
        goal='Analyze Cardano wallet transactions and provide detailed summaries',
        backstory="""You are an expert in analyzing blockchain transactions and providing 
        clear, concise summaries of wallet activity. You specialize in Cardano blockchain 
        analysis and can break down complex transaction patterns into understandable insights.""",
        verbose=True,
        allow_delegation=False
    )

def analyze_wallet(wallet_address):
    # Create the wallet analyzer
    analyzer = WalletAnalyzer(wallet_address)
    
    # Create the agent
    agent = create_wallet_analyzer_agent()
    
    # Get all transactions from last 60 days
    two_month_txs = analyzer.get_transactions(days=60)
    
    # Filter for different time periods
    now = datetime.now()
    monthly_txs = [tx for tx in two_month_txs if (now - datetime.fromtimestamp(tx.block_time)).days <= 30]
    weekly_txs = [tx for tx in two_month_txs if (now - datetime.fromtimestamp(tx.block_time)).days <= 7]
    daily_txs = [tx for tx in two_month_txs if (now - datetime.fromtimestamp(tx.block_time)).days <= 1]
    
    # Analyze transactions for each period
    two_month_stats = analyzer.analyze_transactions(two_month_txs)
    monthly_stats = analyzer.analyze_transactions(monthly_txs)
    weekly_stats = analyzer.analyze_transactions(weekly_txs)
    daily_stats = analyzer.analyze_transactions(daily_txs)
    
    # Create the analysis task
    task = Task(
        description=f"""Analyze the following wallet statistics and provide a detailed summary:
        
        2-Month Statistics (Last 60 days):
        - Total ADA Received: {two_month_stats['total_received']:.2f} ADA
        - Total ADA Spent: {two_month_stats['total_spent']:.2f} ADA
        - Net Flow: {two_month_stats['net_flow']:.2f} ADA
        
        Monthly Statistics (Last 30 days):
        - Total ADA Received: {monthly_stats['total_received']:.2f} ADA
        - Total ADA Spent: {monthly_stats['total_spent']:.2f} ADA
        - Net Flow: {monthly_stats['net_flow']:.2f} ADA
        
        Weekly Statistics (Last 7 days):
        - Total ADA Received: {weekly_stats['total_received']:.2f} ADA
        - Total ADA Spent: {weekly_stats['total_spent']:.2f} ADA
        - Net Flow: {weekly_stats['net_flow']:.2f} ADA
        
        Daily Statistics (Last 24 hours):
        - Total ADA Received: {daily_stats['total_received']:.2f} ADA
        - Total ADA Spent: {daily_stats['total_spent']:.2f} ADA
        - Net Flow: {daily_stats['net_flow']:.2f} ADA
        
        Provide insights about the wallet's activity patterns and any notable trends.""",
        agent=agent
    )
    
    # Create and run the crew
    crew = Crew(
        agents=[agent],
        tasks=[task],
        verbose=2,
        process=Process.sequential
    )
    
    result = crew.kickoff()
    return result

if __name__ == "__main__":
    # Example usage
    wallet_address = input("Enter Cardano wallet address: ")
    result = analyze_wallet(wallet_address)
    print("\nAnalysis Results:")
    print(result) 