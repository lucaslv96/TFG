import yfinance as yf
import pandas as pd

class YahooFinanceScraper:
    def __init__(self):
        self.market_suffixes = [
            '.DE', '.F', '.MC', '.MA', '.PA', '.L', '.MI', '.AS', '.BR', 
            '.VI', '.ST', '.CO', '.OL', '.LS', '.SW', '.HE', '.IR', '.AT', 
            '.TO', '.MX', '.SA', '.T', '.HK', '.SG', '.AX', '.NZ', '.KS', 
            '.TW', ''
        ]

    def get_financial_data(self, ticker, data_type='balance'):
        """Obtiene los datos financieros a partir del ticker, intentando primero sin sufijos."""
        try:
            # Intentar primero con el ticker original
            company = yf.Ticker(ticker)
            
            # Obtener datos según el tipo solicitado
            if data_type == 'balance':
                data = company.balance_sheet
            elif data_type == 'income':
                data = company.financials
            elif data_type == 'cashflow':
                data = company.cashflow
            else:
                return pd.DataFrame()
            
            # Si tenemos datos válidos, procesarlos y devolverlos
            if not data.empty:
                data = data.iloc[:, :4]  # Seleccionar las primeras cuatro columnas
                data.columns = [f"{col.year}" for col in data.columns]
                data.reset_index(inplace=True)
                data.rename(columns={'index': 'Datos'}, inplace=True)
                return data
                
            # Si no hay datos, intentar con sufijos
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
            # Primero intentar con el ticker original
            company = yf.Ticker(ticker)
            info = company.info
            
            if 'longName' in info and info['longName']:
                return info['longName']
                
            # Si no encontramos el nombre, probar con sufijos
            for suffix in self.market_suffixes:
                if suffix == '':  # Saltar el sufijo vacío, ya lo intentamos
                    continue
                    
                try:
                    company = yf.Ticker(ticker + suffix)
                    info = company.info
                    if 'longName' in info and info['longName']:
                        return info['longName']
                except:
                    continue
                    
            return "Nombre de la empresa no disponible"
        except Exception:
            # Si hay error con el ticker original, intentar con sufijos
            for suffix in self.market_suffixes:
                if suffix == '':  # Saltar el sufijo vacío, ya lo intentamos
                    continue
                    
                try:
                    company = yf.Ticker(ticker + suffix)
                    info = company.info
                    if 'longName' in info and info['longName']:
                        return info['longName']
                except:
                    continue
            
            return "Nombre de la empresa no disponible"

    def get_combined_financial_data(self, ticker):
        balance_data = self.get_financial_data(ticker, 'balance')
        income_data = self.get_financial_data(ticker, 'income')
        cashflow_data = self.get_financial_data(ticker, 'cashflow')
        
        combined_data = pd.concat([balance_data, income_data, cashflow_data], axis=0)
        
        if not combined_data.empty:
            combined_data.reset_index(inplace=True, drop=True)
        else:
            combined_data = pd.DataFrame(columns=["Datos", "2024", "2023", "2022", "2021"])
            
        return combined_data
