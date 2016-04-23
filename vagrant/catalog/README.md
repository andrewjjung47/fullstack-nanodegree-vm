Udacity Fullstack Nanodegree Project 3
=============

Item catalog project. Google authenticated users can add, edit, and delete items and categories. It provides json endpoints at '/category/JSON', '/category/(category id)/JSON'.

## To Run:
1. Install Virtual Machine and Vagrant (https://docs.vagrantup.com/v2/installation/)
2. From `fullstack-nanodegree-vm/vagrant`, `vagrant up`. Once this is done, `vagrant ssh`.
3. `cd /vagrant/catalog`
4. Run demodata.py by `python demodata.py`.
5. Create client_secrets.json and add following into the file 
  `{"web":{"client_id":"your-client-id","auth_uri":"https://accounts.google.com/o/oauth2/auth","token_uri":"https://accounts.google.com/o/oauth2/token","auth_provider_x509_cert_url":"https://www.googleapis.com/oauth2/v1/certs","client_secret":"your-client-secret","redirect_uris":["https://www.example.com/oauth2callback"],"javascript_origins":["https://www.example.com","http://localhost:9000"]}}`
6. Run project.py by `python project.py`.
