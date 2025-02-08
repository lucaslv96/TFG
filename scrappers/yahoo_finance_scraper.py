import yfinance as yf
import pandas as pd

class YahooFinanceScraper:
    def get_financial_data(self, ticker, data_type='balance'):
        """Obtiene los datos financieros de la empresa a partir del ticker de Yahoo Finance."""
        try:
            # Obtener el objeto de datos financieros
            company = yf.Ticker(ticker)

            if data_type == 'balance':
                # Obtener el balance anual (annual balance sheet) en formato de DataFrame
                data = company.balance_sheet
            elif data_type == 'income':
                # Obtener la cuenta de resultados anual (annual income statement) en formato de DataFrame
                data = company.financials
            elif data_type == 'cashflow':
                # Obtener el flujo de caja anual (annual cash flow statement) en formato de DataFrame
                data = company.cashflow
            else:
                return pd.DataFrame()

            # Filtrar solo los últimos años
            if not data.empty:
                data = data.iloc[:, :4]  # Seleccionar las primeras cuatro columnas (últimos cuatro años)

                # Eliminar filas que contienen NaN
                #data = data.dropna()

            # Añadir las fechas como encabezados de columna
            data.columns = [f"{col.year}" for col in data.columns]

            # Renombrar la primera columna a 'Datos'
            data.reset_index(inplace=True)
            data.rename(columns={'index': 'Datos'}, inplace=True)

            return data
        except Exception:
            return pd.DataFrame()

    def get_company_name(self, ticker):
        """Obtiene el nombre de la empresa a partir del ticker de Yahoo Finance."""
        try:
            company = yf.Ticker(ticker)
            return company.info['longName']
        except Exception:
            return "Nombre de la empresa no disponible"

    def get_combined_financial_data(self, ticker):
        """Obtiene el balance, la cuenta de resultados y el flujo de caja de los últimos años de la empresa en un solo DataFrame."""
        balance_data = self.get_financial_data(ticker, 'balance')
        income_data = self.get_financial_data(ticker, 'income')
        cashflow_data = self.get_financial_data(ticker, 'cashflow')

        if balance_data.empty and income_data.empty and cashflow_data.empty:
            for suffix in self.market_suffixes:
                balance_data = self.get_financial_data(ticker + suffix, 'balance')
                income_data = self.get_financial_data(ticker + suffix, 'income')
                cashflow_data = self.get_financial_data(ticker + suffix, 'cashflow')
                if not balance_data.empty or not income_data.empty or not cashflow_data.empty:
                    break

        combined_data = pd.concat([balance_data, income_data, cashflow_data], axis=0)
        combined_data.reset_index(inplace=True)  # Ensure the index is reset to include the labels
        combined_data.rename(columns={'index': 'Datos'}, inplace=True)  # Rename the index column to 'Datos'
        return combined_data
