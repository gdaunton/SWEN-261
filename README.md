![HealthNet](https://health.rhosoft.co/static/healthnet.png)
HealthNet is a Django and python based web application with sqlite for data storage. The objective of this project was to create an easy to use system that met all of the requirements that we were given. At the beginning of the semester we were broken into groups of five and assigned this project to develop over the course of the class. In our team of 4 we managed the project as if it were being delivered to a customer. This included creating design documents, GUI mock-ups, class diagrams and other related documentation to make sure we planned every aspect of the project. My role was to focus on the development of the application. After development we tested and shipped the app. Our Professor noted that we had the best implementation in the class.

##Installation
Download and install [Python 3.4](https://www.python.org/downloads/) which should have pip packaged with it.
If not install [pip](https://pip.pypa.io/en/latest/installing.html).

Also add (path to python installation)\Python34 and \Python34\Scripts to your path. On Windows python usually installs on your C: drive.

Now open your favorite command line, navigate to the project directory and run:
```bash
$ pip install -r requirments.txt
```
Once that finishes installing all of the dependencies run:
```bash
$ python manage.py syncdb
```
This will ask you to create a new superuser which you don't have to do.
After that is done run:
```bash
$ python manage.py loaddata data.json
$ python manage.py runserver
```
This will load some dummy information and start the development server.

Now all you have to do is goto [localhost:8000](http://localhost:8000/).

Volla! You have HealthNet up and running!

##Usage
You can login to the website as several different types of users:
```
	Admin
		Username: admin
		Password: pass

	Doctor
		Username: doctor
		Password: pass

	Nurse
		Username: nurse
		Password: pass
```
You can also enter the website as a patient by registering as a new patient.

From here you can utilize all of the features such as:

	- Messaging
	- Managing Appointments
	- Managing Prescriptions/Tests
	- Viewing/Managing Hospitals
	- Updating User Information
	- and much much more!