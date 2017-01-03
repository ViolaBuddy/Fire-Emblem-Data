# Fire-Emblem-Data

A collection of data about Fire Emblem. This is very much a work in progress right now.

The [updateSQL.py](updateSQL.py) file, when run (with Python 3), will create a MySQL database (completely overwriting any old database that's called Fireemblemdata) with the raw CSV data, which is in the FE14 folder. Note that you may need to edit this Python file to get it to work: you may not have the Python database manager that I have (though Python standardizes database function calls, so if you swap out `import` statements everything else should still work), and also, you need to provide a password.txt in the current folder with your username and password information to log into the database.

## Data source

The data is (almost) entirely from [Serenes Forest](http://serenesforest.net/); see also [their data usage policy](http://serenesforest.net/general/about-us/) - basically, they're OK with pretty much anything, but if you're making an English-language Fire Emblem website, you should contact them first.

The following additional data is from the Fire Emblem Wikia:

- (None yet, though it's been referenced)

Additional thanks to ByaKudo on Reddit; see also [his/her Github repository for Fates data](https://github.com/ByaKudo/FE-Fates-AssetsDB), and [the Android companion app (s)he created with this data](https://www.reddit.com/r/fireemblem/comments/5hcx1x/fe_fates_database_an_android_companion_app/) ([here's the direct link to the Google Play store](https://play.google.com/store/apps/details?id=org.byakudo.fefatesdb)).

## Misc.

- ~~On [this Serenes Forest page](http://serenesforest.net/fire-emblem-fates/nohrian-characters/class-sets/), Siegbert's name is misspelled as "Siegert" (without a b).~~ Apparently, this has been fixed since I first accessed this page.
- On Serenes Forest, Kaze, Rinkah, Azura, and Sakura (whom you control from Chapter 4 for the first two, and Chapter 5 for the second two respectively) are listed as joining on Chapter 6 instead (when your path splits, since they don't stay with you if you choose Nohr). In this database (see [characterbasestats.csv](FE14/characterbasestats.csv)) I write their original starting chapters, even for Rinkah and Sakura in Conquest even though they never rejoin. Kaze has a second entry for when he rejoins the party in Chapter 11 of Conquest with new stats; Azura rejoins with the same stats in Chapter 9 of Conquest, so does not get another entry.
- The og:description HTML meta field of [the official Fire Emblem page](http://fireemblemfates.nintendo.com/dlc/) calls the third path "Revelations" (with an extra S), which you can see in the HTML source. In fact, more visibly, the title of the page also calls it Revelations (usually visible if you mouse over the tab or top ribbon of your browser).

## TODOs and Known Issues

- Revelation base stats/join times have not been inputted.