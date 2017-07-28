import sys
import argparse
import time
from operator import itemgetter

from workflow import Workflow, ICON_WEB

class MemorableWorkflow(object):

    def __init__(self):
        self.wf = Workflow()

    def parse_argument(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('--log', dest='to_log', nargs='?', default=None)
        parser.add_argument('query', nargs='?', default=None)
        return parser.parse_args(self.wf.args)

    def maybe_get_data(self):
        # Retrieve posts from cache if available and no more than 600
        # seconds old
        data = self.wf.stored_data('data')
        if data is None:
            data = {}
        if (
            len(data.get('data', [])) == 0 or
            time.time() - data.get('queried_time', 0) >= 60 * 10
        ):
            rows = self.get_rows()
            data['data'] = rows
            data['queried_time'] = time.time()
        self.wf.store_data('data', data)
        return data

    def build_items(self, query, data):
        # Loop through the returned posts and add an item for each to
        # the list of results for Alfred
        if query:
            rows = self.wf.filter(
                query, data['rows'], key=itemgetter(0), min_score=20)
        else:
            rows = data.get('recent', []) + data['rows']

        default_item = {'icon': ICON_WEB, 'valid': True}
        for row in rows[:10]:
            row = dict(
                default_item.items() + self.build_row(row).items())
            self.wf.add_item(**row)

        # Send the results to Alfred as XML
        self.wf.send_feedback()


    def log_recent_selections(self, selected_url, data):
        selected = filter(
            lambda (name, url): url == selected_url, data['rows'])
        if len(selected) > 0 and selcted[0] not in data.get('recent', []):
            data['recent'] = [selected[0]] + data.get('recent', [])
        data['recent'] = data['recent'][:10]
        self.wf.store_data('data', data)


    def main(self, wf):
        args = self.parse_argument()
        data = self.maybe_get_data()
        if args.to_log:
           self.log_recent_selections(args.to_log, data)
        else:
            self.build_items(args.query, data)

    def run(self):
        sys.exit(self.wf.run(self.main))

    def get_rows(self):
        raise NotImplementedError()

    def build_row(self, row):
        raise NotImplementedError()
