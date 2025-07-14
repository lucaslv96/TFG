import yfinance as yf
import pandas as pd

class YahooFinanceScraper:
    def __init__(self):
        self.market_suffixes = ['.MC', '.DE', '.L', '.PA', '.MI', '.AS', '.SW', '.TO', '.MX', '.HK', '.AX', '']

    def get_financial_data(self, ticker, data_type='balance'):
        """Obtiene los datos financieros a partir del ticker, intentando primero sin sufijos."""
        try:
            company = yf.Ticker(ticker)
            
            if data_type == 'balance':
                data = company.balance_sheet
            elif data_type == 'income':
                data = company.financials
            elif data_type == 'cashflow':
                data = company.cashflow
            else:
                return pd.DataFrame()
            
            if not data.empty:
                data = data.iloc[:, :4]  
                data.columns = [f"{col.year}" for col in data.columns]
                data.reset_index(inplace=True)
                data.rename(columns={'index': 'Datos'}, inplace=True)
                return data
                
            return self._try_with_suffixes(ticker, data_type)
            
        except Exception as e:
            return self._try_with_suffixes(ticker, data_type)

    def _try_with_suffixes(self, ticker, data_type):
        print(f"Intentando ticker {ticker} con diferentes sufijos de mercado...")
        
        for suffix in self.market_suffixes:
            try:
                full_ticker = ticker + suffix
                
                company = yf.Ticker(full_ticker)
                
                if data_type == 'balance':
                    data = company.balance_sheet
                elif data_type == 'income':
                    data = company.financials
                elif data_type == 'cashflow':
                    data = company.cashflow
                else:
                    data = pd.DataFrame()
                
                if not data.empty:
                    data = data.iloc[:, :4]
                    data.columns = [f"{col.year}" for col in data.columns]
                    data.reset_index(inplace=True)
                    data.rename(columns={'index': 'Datos'}, inplace=True)
                    
                    return data
            except Exception as e:
                print(f"Error con {ticker + suffix}: {e}")
        
        return pd.DataFrame()

    def get_company_name(self, ticker):
        """Obtiene el nombre de la empresa a partir del ticker, intentando primero sin sufijos."""
        try:
            company = yf.Ticker(ticker)
            info = company.info
            
            if 'longName' in info and info['longName']:
                return info['longName']
                
            for suffix in self.market_suffixes:
                if suffix == '':  
                    continue
                    
                try:
                    company = yf.Ticker(ticker + suffix)
                    info = company.info
                    if 'longName' in info and info['longName']:
                        return info['longName']
                except:
                    continue
                    
            return None  # Return None instead of error message
        except Exception:
            # Network error, timeout, or any other error - return None
            return None

    def get_combined_financial_data(self, ticker):
        balance_data = self.get_financial_data(ticker, 'balance')
        income_data = self.get_financial_data(ticker, 'income')
        cashflow_data = self.get_financial_data(ticker, 'cashflow')
        
        # --- CAMBIO: NO añadir prefijos al campo 'Datos' ---
        # Simplemente concatenar los datos tal cual
        combined_data = pd.concat([balance_data, income_data, cashflow_data], axis=0)
        
        if not combined_data.empty:
            combined_data.reset_index(inplace=True, drop=True)
        else:
            combined_data = pd.DataFrame(columns=["Datos", "2024", "2023", "2022", "2021"])
            
        return combined_data
