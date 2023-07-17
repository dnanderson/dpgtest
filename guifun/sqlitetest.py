import sqlite3


con = sqlite3.connect("tut.db")

cur = con.cursor()

#cur.execute("create table movie(title, year, score)")

res = cur.executescript("PRAGMA journal_mode=wal;")
res = cur.executescript("""BEGIN;
                     insert into movie values('one', 1975, 8.2); COMMIT;""")
res = cur.execute("select * from movie")
import pdb; pdb.set_trace()
                    
print(res.fetchall())