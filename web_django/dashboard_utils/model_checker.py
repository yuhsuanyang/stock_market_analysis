# how to use: in "shell":
# from dashboard_utils import model_checker
class Checker(object):
    def __init__(self, model):
        self.model = model
        self.columns = model.get_columns()

    def get_unique_values(self, col_name):
        if col_name not in self.columns:
            print('no such column')
            return
        query_set = self.model.objects.values(col_name).distinct()
        return [q[col_name] for q in query_set]

    def get_sequence_data(self, code):
        query_set = self.model.objects.filter(code=code)
        print('-----data description-----')
        if 'year' in self.columns:
            query_set = query_set.order_by('year', 'season')
            print(f"start year: {query_set[0].year}")
            print(f"end year: {query_set[len(query_set)-1].year}")
        elif 'date' in self.columns:
            query_set = query_set.order_by('date')
            print(f"start date: {query_set[0].date}")
            print(f"end date: {query_set[len(query_set)-1].date}")
        elif 'season' in self.columns:
            query_set = query_set.order_by('season')
            print(f"start season: {query_set[0].season}")
            print(f"end season: {query_set[len(query_set)-1].season}")

        print(f"count: {len(query_set)}")
        return query_set
