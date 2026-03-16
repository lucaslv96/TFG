import logging
import yfinance as yf
import pandas as pd


class YahooFinanceScraper:
    def __init__(self):
        # El sufijo vacío se prueba primero en get_financial_data; aquí solo sufijos reales
        self.market_suffixes = ['.MC', '.DE', '.L', '.PA', '.MI', '.AS', '.SW', '.TO', '.MX', '.HK', '.AX']
        self.logger = logging.getLogger(__name__)

    # ------------------------------------------------------------------
    # Punto de entrada público
    # ------------------------------------------------------------------

    def get_financial_data(self, ticker, data_type='balance'):
        if data_type not in ('balance', 'income', 'cashflow'):
            return pd.DataFrame()
        try:
            data = self._fetch_raw_data(ticker, data_type)
            if not data.empty:
                return self._format_data(data)
            return self._try_with_suffixes(ticker, data_type)
        except Exception:
            return self._try_with_suffixes(ticker, data_type)

    def get_combined_financial_data(self, ticker):
        """Devuelve balance, income y cashflow concatenados en un solo DataFrame."""
        frames = [self.get_financial_data(ticker, t) for t in ('balance', 'income', 'cashflow')]
        combined = pd.concat(frames, axis=0)
        if not combined.empty:
            combined.reset_index(drop=True, inplace=True)
        else:
            combined = pd.DataFrame(columns=["Datos", "2024", "2023", "2022", "2021"])
        return combined

    def get_company_name(self, ticker):
        """Devuelve el nombre largo de la empresa o None si no se encuentra."""
        try:
            info = yf.Ticker(ticker).info
            if info.get('longName'):
                return info['longName']
            for suffix in self.market_suffixes:
                try:
                    info = yf.Ticker(ticker + suffix).info
                    if info.get('longName'):
                        return info['longName']
                except Exception:
                    continue
            return None
        except Exception:
            return None

    # ------------------------------------------------------------------
    # Helpers privados
    # ------------------------------------------------------------------

    def _fetch_raw_data(self, ticker, data_type):
        """Obtiene el DataFrame crudo de yfinance sin formatear."""
        company = yf.Ticker(ticker)
        if data_type == 'balance':
            return company.balance_sheet
        elif data_type == 'income':
            return company.financials
        else:  # cashflow
            return company.cashflow

    def _format_data(self, data):
        """Toma los 4 años más recientes y normaliza la estructura del DataFrame."""
        data = data.iloc[:, :4].copy()
        data.columns = [str(col.year) for col in data.columns]
        data.reset_index(inplace=True)
        # El nombre de la primera columna varía; siempre renombramos a 'Datos'
        data.rename(columns={data.columns[0]: 'Datos'}, inplace=True)
        return data

    def _try_with_suffixes(self, ticker, data_type):
        self.logger.info("Intentando ticker %s con diferentes sufijos de mercado...", ticker)
        for suffix in self.market_suffixes:
            try:
                data = self._fetch_raw_data(ticker + suffix, data_type)
                if not data.empty:
                    return self._format_data(data)
            except Exception as e:
                self.logger.debug("Error con %s: %s", ticker + suffix, e)
        return pd.DataFrame()
