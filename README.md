# Fire-Emblem-Data

A collection of data about Fire Emblem. This is very much a work in progress right now.

The [updateSQL.py](updateSQL.py) file, when run (with Python 3), will create a MySQL database (completely overwriting any old database that's called Fireemblemdata) with the raw CSV data, which is in the FE14 folder. Note that you may need to edit this Python file to get it to work: you may not have the Python database manager that I have (though Python standardizes database function calls, so if you swap out `import` statements everything else should still work), and also, you need to provide a password.txt in the current folder with your username and password information to log into the database.

## Data source

The data is (almost) entirely from [Serenes Forest](http://serenesforest.net/); see also [their data usage policy](http://serenesforest.net/general/about-us/) - basically, they're OK with pretty much anything, but if you're making an English-language Fire Emblem website, you should contact them first.

## Misc.
On [this Serenes Forest page](http://serenesforest.net/fire-emblem-fates/nohrian-characters/class-sets/), Siegbert's name is misspelled as "Siegert" (without a b)