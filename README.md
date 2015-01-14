# Instrap

Bootstrap a package based instack undercloud.

See [the documentation](http://instrap.rtfd.org) for further
details. Or, just go for the quick start approach.

    git clone git@github.com:d0ugal/instrap.git
    cd instrap
    pip install -r requirements.txt
    fab -H $HOST full

Another handy function, to re-create the undercloud.

    fab -H $HOST undercloud.recreate

View `fab -l` to see the other commands.
