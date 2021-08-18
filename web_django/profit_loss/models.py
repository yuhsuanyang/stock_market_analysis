from django.db import models
from dashboard_utils.terms import terms
# Create your models here.


class HoldingsProfitLossData(models.Model):

    code = models.CharField(max_length=4, help_text="公司代碼")
    season = models.CharField(max_length=6, help_text="季度")  # year_season
    net_interest_income = models.FloatField(help_text="利息淨收益")
    net_noninterest_income = models.FloatField(help_text="利息外淨收益")
    net_income = models.FloatField(help_text="淨收益")
    net_profit_before_tax = models.FloatField(help_text="稅前淨利")
    net_profit_after_tax = models.FloatField(help_text="稅後淨利")
    operation_expenses = models.FloatField(help_text="營業費用")
    EPS = models.FloatField(help_text="基本每股盈餘")

    def __str__(self):
        return f"{self.code} {self.season}"

    @staticmethod
    def get_columns():
        col_dict = {}
        for col in [
                'code', 'season', 'net_interest_income',
                'net_noninterest_income', 'net_income',
                'net_profit_before_tax', 'net_profit_after_tax',
                'operation_expenses'
        ]:
            col_dict[col] = terms[col]
        col_dict['EPS'] = '基本每股盈餘'
        return col_dict

    def get_values(self):
        return {
            'net_interest_income': self.net_interest_income,
            'net_noninterest_income': self.net_noninterest_income,
            'net_income': self.net_income,
            'net_profit_before_tax': self.net_profit_before_tax,
            'net_profit_after_tax': self.net_profit_after_tax,
            'operation_expenses': self.operation_expenses,
            'EPS': self.EPS
        }


class BankProfitLossData(models.Model):

    code = models.CharField(max_length=4, help_text="公司代碼")
    season = models.CharField(max_length=6, help_text="季度")
    net_interest_income = models.FloatField(help_text="利息淨收益")
    net_noninterest_income = models.FloatField(help_text="利息外淨收益")
    deposits = models.FloatField(help_text="各項提存")
    net_profit_before_tax = models.FloatField(help_text="稅前淨利")
    net_profit_after_tax = models.FloatField(help_text="稅後淨利")
    operation_expenses = models.FloatField(help_text="營業費用")
    EPS = models.FloatField(help_text="基本每股盈餘")

    def __str__(self):
        return f"{self.code} {self.season}"

    @staticmethod
    def get_columns():
        col_dict = {}
        for col in [
                'code', 'season', 'net_interest_income',
                'net_noninterest_income', 'deposit', 'net_profit_before_tax',
                'net_profit_after_tax', 'operation_expenses'
        ]:
            col_dict[col] = terms[col]
        col_dict['EPS'] = '基本每股盈餘'
        return col_dict

    def get_values(self):
        return {
            'net_interest_income': self.net_interest_income,
            'net_noninterest_income': self.net_noninterest_income,
            'deposits': self.deposits,
            'net_profit_before_tax': self.net_profit_before_tax,
            'net_profit_after_tax': self.net_profit_after_tax,
            'operation_expenses': self.operation_expenses,
            'EPS': self.EPS
        }


class StandardProfitLossData(models.Model):

    code = models.CharField(max_length=4, help_text="公司代碼")
    season = models.CharField(max_length=6, help_text="季度")
    business_income = models.FloatField(help_text="營業收入")
    business_interest = models.FloatField(help_text="營業利益")
    gross = models.FloatField(help_text="營業毛利")
    operation_cost = models.FloatField(help_text="營業成本")
    operation_expenses = models.FloatField(help_text="營業費用")
    non_operation_income = models.FloatField(help_text="營業外收入及支出")
    net_profit_before_tax = models.FloatField(help_text="稅前淨利")
    net_profit_after_tax = models.FloatField(help_text="稅後淨利")
    EPS = models.FloatField(help_text="基本每股盈餘")

    def __str__(self):
        return f"{self.code} {self.season}"

    @staticmethod
    def get_columns():
        col_dict = {}
        for col in [
                'code', 'season', 'business_income', 'business_interest',
                'gross', 'net_profit_before_tax', 'net_profit_after_tax',
                'operation_expenses', 'operation_cost'
        ]:
            col_dict[col] = terms[col]
        col_dict['EPS'] = '基本每股盈餘'
        return col_dict

    def get_values(self):
        return {
            'business_income': self.business_income,
            'business_interest': self.business_interest,
            'gross': self.gross,
            'operation_cost': self.operation_cost,
            'operation_expenses': self.operation_expenses,
            'non_operation_income': self.non_operation_income,
            'net_profit_before_tax': self.net_profit_before_tax,
            'net_profit_after_tax': self.net_profit_after_tax,
            'EPS': self.EPS
        }


class InsuranceProfitLossData(models.Model):

    code = models.CharField(max_length=4, help_text="公司代碼")
    season = models.CharField(max_length=6, help_text="季度")
    business_income = models.FloatField(help_text="營業收入")
    business_interest = models.FloatField(help_text="營業利益")
    operation_cost = models.FloatField(help_text="營業成本")
    operation_expenses = models.FloatField(help_text="營業費用")
    non_operation_income = models.FloatField(help_text="營業外收入及支出")
    net_profit_before_tax = models.FloatField(help_text="稅前淨利")
    net_profit_after_tax = models.FloatField(help_text="稅後淨利")
    EPS = models.FloatField(help_text="基本每股盈餘")

    def __str__(self):
        return f"{self.code} {self.season}"

    @staticmethod
    def get_columns():
        col_dict = {}
        for col in [
                'code', 'season', 'net_business_income',
                'net_business_interest', 'net_income', 'net_profit_before_tax',
                'net_profit_after_tax', 'operation_expenses', 'operation_cost',
                'non_operation_income'
        ]:
            col_dict[col] = terms[col]
        col_dict['EPS'] = '基本每股盈餘'
        return col_dict

    def get_values(self):
        return {
            'net_business_income': self.business_income,
            'net_business_interest': self.business_interest,
            'net_income': self.net_income,
            'operation_cost': self.operation_cost,
            'operation_expenses': self.operation_expenses,
            'non_operation_income': self.non_operation_income,
            'net_profit_before_tax': self.net_profit_before_tax,
            'net_profit_after_tax': self.net_profit_after_tax,
            'EPS': self.EPS
        }


class OtherProfitLossData(models.Model):

    code = models.CharField(max_length=4, help_text="公司代碼")
    season = models.CharField(max_length=6, help_text="季度")
    income = models.FloatField(help_text="收入")
    expenses = models.FloatField(help_text="支出")
    net_profit_before_tax = models.FloatField(help_text="稅前淨利")
    net_profit_after_tax = models.FloatField(help_text="稅後淨利")
    EPS = models.FloatField(help_text="基本每股盈餘")

    def __str__(self):
        return f"{self.code} {self.season}"

    @staticmethod
    def get_columns():
        col_dict = {}
        for col in [
                'code', 'season', 'expenses', 'net_profit_before_tax',
                'net_profit_after_tax'
        ]:
            col_dict[col] = terms[col]
        col_dict['EPS'] = '基本每股盈餘'
        return col_dict

    def get_values(self):
        return {
            'income': self.income,
            'expenses': self.expenses,
            'net_profit_before_tax': self.net_profit_before_tax,
            'net_profit_after_tax': self.net_profit_after_tax,
            'EPS': self.EPS
        }
