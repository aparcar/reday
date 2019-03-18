# reday

In adventures times, keep track of what happened like the day before yesterday!
Simple encrypted diary for daily entries

## installation

```shell
python3 -m pip install flask pysqlchipher3 sqlite3
```

## usage

Create a `session_key` via the following command.

```shell
dd if=/dev/urandom bs=16 count=1 2>/dev/null | sha256sum | cut -d' ' -f1 > session_key

```

Run the web interface while beeing in this repos folder.

```shell
flask run
```

Visit [localhost:5000](http://localhost:5000) to load web interface.

On first run, choose a password, you can't change it once setup.

Write stuff, done. You can not edit entries older than 7 days.

## acknowledgements

Thanks to [sr.ht](https://sr.ht) for the style sheet. I hope that's okay.
