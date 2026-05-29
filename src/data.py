import yfinance as yf
import pandas as pd
import numpy as np

class EnergyDataLoader:
    """
    Standardized data loader for energy sector financial analysis.
    Fetches live data from yfinance and maps raw accounting tags to clean concepts.
    """
    def __init__(self, tickers=["XOM", "CVX", "SHEL", "TTE", "BP", "EQNR"]):
        self.tickers = tickers
        # Expanded data mappings to handle US GAAP vs IFRS vs European minor variations
        self.mappings = {
            'OCF': [
                'Operating Cash Flow', 
                'Cash Flow From Continuing Operating Activities',
                'Net Cash From Operating Activities'
            ],
            'Capex': [
                'Capital Expenditure', 
                'Capital Expenditures',
                'Payments For Property Plant And Equipment'
            ],
            'Dividends': [
                'Cash Dividends Paid', 
                'Dividends Paid', 
                'Common Stock Dividend Paid',
                'Cash Dividend Paid'
            ],
            'Buybacks': [
                'Repurchase Of Capital Stock', 
                'Repurchase Of Stock', 
                'Net Common Stock Issuance',
                'Treasury Stock Payments'
            ],
            'Net_Income': [
                'Net Income', 
                'Net Income Common Stockholders',
                'Net Income From Continuing Operations'
            ],
            'Total_Assets': ['Total Assets', 'Total Non Current Assets'],
            'EBITDA': ['EBITDA', 'Ebitda', 'Normalized EBITDA'],
            'Total_Debt': ['Total Debt', 'Long Term Debt', 'Long Term Debt And Capital Lease Obligation'],
            'Cash': ['Cash And Cash Equivalents', 'Cash Cash Equivalents And Short Term Investments', 'Cash Financial']
        }

    def _get_field(self, df, field_keys, ticker="Unknown"):
        """Helper to find the first available field from a list of aliases."""
        available = df.index.tolist()
        for key in field_keys:
            if key in available:
                return df.loc[key]
        
        # Log missing fields for advanced audit expander in app
        # (This would normally go to a logger, here we return 0 but could trigger a warning)
        return 0

    def fetch_financials(self, years=5):
        """Fetches annual cash flow, income, and balance sheet data."""
        all_data = []
        for ticker in self.tickers:
            print(f"INFO: Fetching live data for {ticker}...")
            stock = yf.Ticker(ticker)
            
            # Fetch TTM/Annual sheets
            cf = stock.cashflow
            inc = stock.financials
            bs = stock.balance_sheet
            
            if cf.empty:
                print(f"WARNING: No cash flow data for {ticker}")
                continue

            # Standardizing Data
            df = pd.DataFrame(index=cf.columns)
            df['Ticker'] = ticker
            df['OCF'] = self._get_field(cf, self.mappings['OCF'])
            df['Capex'] = self._get_field(cf, self.mappings['Capex']).abs()
            df['Dividends'] = self._get_field(cf, self.mappings['Dividends']).abs()
            df['Buybacks'] = self._get_field(cf, self.mappings['Buybacks']).abs()
            
            # Net Income from Financials
            df['Net_Income'] = self._get_field(inc, self.mappings['Net_Income'])
            df['EBITDA'] = self._get_field(inc, self.mappings['EBITDA'])
            
            # Balance Sheet Fields
            df['Total_Assets'] = self._get_field(bs, self.mappings['Total_Assets'])
            df['Total_Debt'] = self._get_field(bs, self.mappings['Total_Debt'])
            df['Cash'] = self._get_field(bs, self.mappings['Cash'])
            
            # Add Market Cap (Current) - yfinance provides this in info
            try:
                df['Market_Cap'] = stock.info.get('marketCap', np.nan)
            except:
                df['Market_Cap'] = np.nan
            
            all_data.append(df.reset_index().rename(columns={'index': 'Date'}))
            
        if not all_data:
            return pd.DataFrame()
            
        final_df = pd.concat(all_data).reset_index(drop=True)
        
        # Ensure Date is strictly datetime for reliable plotting and sorting
        final_df['Date'] = pd.to_datetime(final_df['Date'], errors='coerce')
        
        # Drop entries where Date could not be parsed (e.g. invalid yfinance headers)
        final_df = final_df.dropna(subset=['Date'])
        
        # Final sort for continuity
        return final_df.sort_values(['Ticker', 'Date'])

if __name__ == "__main__":
    # Quick verification run
    loader = EnergyDataLoader(tickers=["XOM", "TTE"])
    data = loader.fetch_financials()
    print("\n--- Verified Data Sample ---")
    print(data.head())
    print("\nColumns found:", data.columns.tolist())
