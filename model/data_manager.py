import pandas as pd
from PyQt5.QtCore import QAbstractTableModel, Qt
from scrappers.yahoo_finance_scraper import YahooFinanceScraper

# Add the PandasModel class directly in this file
class PandasModel(QAbstractTableModel):
    def __init__(self, df=pd.DataFrame(), parent=None):
        QAbstractTableModel.__init__(self, parent)
        self._df = df

    def rowCount(self, parent=None):
        return len(self._df.index)

    def columnCount(self, parent=None):
        return len(self._df.columns)

    def data(self, index, role=Qt.DisplayRole):
        if index.isValid() and role == Qt.DisplayRole:
            return str(self._df.iloc[index.row(), index.column()])
        return None

    def headerData(self, col, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            if col < len(self._df.columns):
                return self._df.columns[col]
        return None

    def setDataFrame(self, df):
        self.beginResetModel()
        self._df = df.copy()
        self.endResetModel()

def filtrar_datos_google(df, data_type):
    if data_type == 'income':
        filtered_df = df.loc[df['Datos'].astype(str).isin([
            'Ingresos', 'Gastos operativos', 'Ingresos netos', 'Margen de beneficio neto',
            'Beneficios por acción', 'EBITDA', 'Tipo impositivo efectivo'
        ])]
    elif data_type == 'balance':
        filtered_df = df.loc[df['Datos'].astype(str).isin([
            'Efectivo y a corto plazo', 'Activos totales', 'Responsabilidades totales',
            'Patrimonio total', 'Acciones en circulación', 'Precio-valor contable',
            'Rentabilidad económica', 'Retorno sobre capital'
        ])]
    elif data_type == 'cashflow':
        filtered_df = df.loc[df['Datos'].astype(str).isin([
            'Ingresos netos', 'Efectivo de operaciones', 'Efectivo de inversión',
            'Efectivo de financiación', 'Variación neta del flujo de caja', 'Flujo de caja libre'
        ])]
    else:
        filtered_df = pd.DataFrame()
    return filtered_df

def filtrar_datos_yahoo(ticker, data_type):
    yahoo_scraper = YahooFinanceScraper()
    data = yahoo_scraper.get_financial_data(ticker, data_type)

    if data_type == 'income':  # Estado de Resultados
        filtered_df = data.loc[data['Datos'].astype(str).isin([
            'Basic EPS', 'Interest Income Non Operating', 'Operating Expense', 
            'Selling General And Administration', 'Diluted EPS', 
            'Net Income From Continuing Operation Net Minority Interest', 
            'Tax Rate For Calcs', 'Net Interest Income', 'Reconciled Cost Of Revenue', 
            'Interest Expense', 'Operating Income', 'Other Non Operating Income Expenses', 
            'EBIT', 'Gross Profit', 'Interest Expense Non Operating', 'Basic Average Shares', 
            'Net Income Common Stockholders', 'Diluted NI Availto Com Stockholders', 
            'Research And Development', 'EBITDA', 'Interest Income', 'Normalized Income', 
            'Pretax Income', 'Other Income Expense', 'Diluted Average Shares', 
            'Normalized EBITDA', 'Reconciled Depreciation', 'Tax Effect Of Unusual Items', 
            'Cost Of Revenue', 'Total Expenses', 'Tax Provision', 
            'Total Operating Income As Reported', 'Operating Revenue', 
            'Net Income From Continuing And Discontinued Operation', 
            'Net Non Operating Interest Income Expense', 'Total Revenue', 'Net Income', 
            'Net Income Continuous Operations', 'Net Income Including Noncontrolling Interests'
        ])]

    elif data_type == 'balance':  # Balance General
        filtered_df = data.loc[data['Datos'].astype(str).isin([
            'Stockholders Equity', 'Current Assets', 'Other Equity Adjustments', 
            'Investments And Advances', 'Common Stock', 'Current Deferred Revenue', 
            'Current Debt', 'Payables', 'Invested Capital', 
            'Other Non Current Liabilities', 
            'Long Term Debt And Capital Lease Obligation', 'Properties', 
            'Total Non Current Liabilities Net Minority Interest', 
            'Cash Cash Equivalents And Short Term Investments', 'Commercial Paper', 
            'Long Term Debt', 'Other Receivables', 'Cash And Cash Equivalents', 
            'Share Issued', 'Total Assets', 'Other Current Borrowings', 
            'Total Capitalization', 'Current Debt And Capital Lease Obligation', 
            'Total Tax Payable', 'Available For Sale Securities', 'Net PPE', 
            'Current Capital Lease Obligation', 'Other Current Assets', 
            'Net Tangible Assets', 'Total Liabilities Net Minority Interest', 
            'Accounts Payable', 'Other Properties', 'Current Deferred Liabilities', 
            'Current Liabilities', 'Income Tax Payable', 'Receivables', 
            'Common Stock Equity', 'Gains Losses Not Affecting Retained Earnings', 
            'Tradeand Other Payables Non Current', 'Total Non Current Assets', 
            'Machinery Furniture Equipment', 'Other Investments', 'Leases', 
            'Investmentin Financial Assets', 'Non Current Deferred Assets', 
            'Capital Stock', 'Total Debt', 'Other Non Current Assets', 
            'Accounts Receivable', 'Gross PPE', 'Inventory', 'Cash Financial', 
            'Accumulated Depreciation', 'Other Current Liabilities', 
            'Treasury Shares Number', 'Working Capital', 'Capital Lease Obligations', 
            'Total Equity Gross Minority Interest', 'Net Debt', 'Tangible Book Value', 
            'Retained Earnings', 'Payables And Accrued Expenses', 
            'Land And Improvements', 'Other Short Term Investments', 
            'Non Current Deferred Taxes Assets', 'Ordinary Shares Number', 
            'Cash Equivalents', 'Long Term Capital Lease Obligation'
        ])]

    elif data_type == 'cashflow':  # Flujo de Caja
        filtered_df = data.loc[data['Datos'].astype(str).isin([
            'Issuance Of Debt', 'Net Issuance Payments Of Debt', 
            'Depreciation And Amortization', 'Change In Payable', 
            'Interest Paid Supplemental Data', 'Change In Inventory', 
            'Deferred Tax', 'Repayment Of Debt', 'Change In Other Current Assets', 
            'Change In Other Current Liabilities', 'Changes In Account Receivables', 
            'Other Non Cash Items', 'Cash Flow From Continuing Investing Activities', 
            'Net Business Purchase And Sale', 'Operating Cash Flow', 
            'Financing Cash Flow', 'Issuance Of Capital Stock', 
            'Net Long Term Debt Issuance', 'Common Stock Issuance', 
            'Change In Account Payable', 'Capital Expenditure', 'Deferred Income Tax', 
            'Depreciation Amortization Depletion', 'Changes In Cash', 
            'Net Short Term Debt Issuance', 'Common Stock Dividend Paid', 
            'Sale Of Investment', 'Stock Based Compensation', 
            'Long Term Debt Payments', 'Cash Flow From Continuing Financing Activities', 
            'Change In Working Capital', 'Investing Cash Flow', 
            'Cash Flow From Continuing Operating Activities', 'Purchase Of Investment', 
            'Repurchase Of Capital Stock', 'Beginning Cash Position', 
            'Common Stock Payments', 'Long Term Debt Issuance', 
            'Net Common Stock Issuance', 'Purchase Of Business', 
            'Income Tax Paid Supplemental Data', 'Net Income From Continuing Operations', 
            'Net Other Investing Changes', 'Free Cash Flow', 
            'Net Investment Purchase And Sale', 'Cash Dividends Paid', 
            'End Cash Position', 'Net PPE Purchase And Sale', 'Change In Receivables', 
            'Net Other Financing Charges', 'Change In Other Working Capital', 
            'Change In Payables And Accrued Expense', 'Purchase Of PPE'
        ])]

    else:
        filtered_df = data 

    return filtered_df



def filtrar_datos_macrotrends(df, data_type):
    # Listas con los nombres de los datos para cada tipo
    income_list = ['Revenue', 'Cost Of Goods Sold', 'Gross Profit', 'Research And Development Expenses', 'SG&A Expenses', 
                   'Other Operating Income Or Expenses', 'Operating Expenses', 'Operating Income', 'Total Non-Operating Income/Expense',
                   'Pre-Tax Income', 'Income Taxes', 'Income After Taxes', 'Other Income', 'Income From Continuous Operations',
                   'Income From Discontinued Operations', 'Net Income', 'EBITDA', 'EBIT', 'Basic Shares Outstanding', 'Shares Outstanding',
                   'Basic EPS', 'EPS - Earnings Per Share']

    balance_list = ['Cash On Hand', 'Receivables', 'Inventory', 'Pre-Paid Expenses', 'Other Current Assets', 'Total Current Assets', 
                    'Property, Plant, And Equipment', 'Long-Term Investments', 'Goodwill And Intangible Assets', 'Other Long-Term Assets', 
                    'Total Long-Term Assets', 'Total Assets', 'Total Current Liabilities', 'Long Term Debt', 'Other Non-Current Liabilities', 
                    'Total Long Term Liabilities', 'Total Liabilities', 'Common Stock Net', 'Retained Earnings (Accumulated Deficit)', 
                    'Comprehensive Income', 'Other Share Holders Equity', 'Share Holder Equity', 'Total Liabilities And Share Holders Equity']

    cashflow_list = ['Net Income/Loss', 'Total Depreciation And Amortization - Cash Flow', 'Other Non-Cash Items', 'Total Non-Cash Items', 
                     'Change In Accounts Receivable', 'Change In Inventories', 'Change In Accounts Payable', 'Change In Assets/Liabilities', 
                     'Total Change In Assets/Liabilities', 'Cash Flow From Operating Activities', 'Net Change In Property, Plant, And Equipment',
                     'Net Change In Intangible Assets', 'Net Acquisitions/Divestitures', 'Net Change In Short-term Investments', 'Net Change In Long-Term Investments',
                     'Net Change In Investments - Total', 'Investing Activities - Other', 'Cash Flow From Investing Activities', 'Net Long-Term Debt', 
                     'Net Current Debt', 'Debt Issuance/Retirement Net - Total', 'Net Common Equity Issued/Repurchased', 'Net Total Equity Issued/Repurchased',
                     'Total Common And Preferred Stock Dividends Paid', 'Financial Activities - Other', 'Cash Flow From Financial Activities', 
                     'Net Cash Flow', 'Stock-Based Compensation', 'Common Stock Dividends Paid']

    # Filtrar el DataFrame según el tipo
    if data_type == 'income':
        filtered_df = df.loc[df['Datos'].astype(str).isin(income_list)]
    elif data_type == 'balance':
        filtered_df = df.loc[df['Datos'].astype(str).isin(balance_list)]
    elif data_type == 'cashflow':
        filtered_df = df.loc[df['Datos'].astype(str).isin(cashflow_list)]
    else:
        filtered_df = pd.DataFrame()  
    return filtered_df
