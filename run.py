import sys
import traceback

from bproxypool.scheduler import run
from bproxypool.server import create_app
from bproxypool.utils.notify import ding

app = create_app()


if __name__ == '__main__':
    # app.run(debug=True)
    if len(sys.argv) == 2:
        if sys.argv[1] == 'scheduler':
            try:
                run()
            except Exception as e:
                tp, msg, tb = sys.exc_info()
                e_msg = '>'.join(traceback.format_exception(tp, msg, tb))
                ding(f'> ProxyPoolError: \n{e_msg}', 'ProxyPoolError')
                raise e
