import datetime, uuid

YESTERDAY = str(datetime.datetime.today().date() - datetime.timedelta(days=1))
TODAY = str(datetime.datetime.today().date())
__TEMP_LOGS_AND_GLOBALS = './__temp_logs_and_globals'
__SESSIONS_FOLDER = f'{__TEMP_LOGS_AND_GLOBALS}/{TODAY}'

get_new_session_id = lambda: uuid.uuid4().__str__()
get_session_pickle_path = lambda session_id: f'{__SESSIONS_FOLDER}/{session_id}.pickle'
SESSION_PICKLE = {'wait':False}

SESSION_TYPE = 'memory'

"""
SESSION_TYPE: (a value equal to: 'local', 'session', 'memory'; default 'memory'):
              The type of the web storage.  memory: only kept in memory, reset
              on page refresh. local: window.localStorage, data is kept after
              the browser quit. session: window.sessionStorage, data is cleared
              once the browser quit.
"""







