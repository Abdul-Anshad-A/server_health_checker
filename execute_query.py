import sqlite3
conn = sqlite3.connect('test.db')
cursor = conn.execute("""select DATE, DESCRIPTION, TESTBED from ILO WHERE DATE LIKE "%2015" """)
#cursor = conn.execute("""select DATE, DESCRIPTION, TESTBED from ILO """)
#cursor = conn.execute("""select DATE, DESCRIPTION from ILO where TESTBED="server1.domain.com" """)
for row in cursor:
	print row
