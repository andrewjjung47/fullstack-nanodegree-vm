Udacity Fullstack Nanodegree Project 2
=============

Swiss style tournament results. Matches players based on Swiss style tournament rules. Postgresql is used to store player and match records.

## To Run:
1. Install Virtual Machine and Vagrant (https://docs.vagrantup.com/v2/installation/)
2. From `fullstack-nanodegree-vm/vagrant`, `vagrant up`. Once this is done, `vagrant ssh`.
3. `cd /vagrant/tournament` and connect to Postgresql console by `psql`. Run tournament.sql by `\i tournament.sql`.
Exit the database console by `\q`
4. Run tournament.py by `python tournament_test.py`.
