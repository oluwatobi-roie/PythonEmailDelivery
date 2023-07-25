# PythonEmailDelivery
This project automatically sends email via a python script to users from a Database.

  Author: Akomolafe Victor Oluwatobi
  Email: hello@tobiakomolafe.com
  Website: https://tobiakomolafe.com
  Company: Roie Technologies

The App works this way
1. It connects to an external SQL database and extract users email that are expiring at a certain time. This is called the target email
2. It query database further to consolidate any associated services assigned to that email
3. It then connects to SMTP server of your email hosting and sends email
4. When email is successfully sent, a count is added and a print of total email sent is recorded.
5. To keep track of emails that has been recently sent, we create a local new database called "recent"
6. The next time you run the script, it checks recent database to see if the user has recently been contacted within the last 7 days at least
7. however, if the user is expiring in the next 3 days, he is considered an urgent customer that needs to be contacted regardless if he has recently been contacted

# Additional Layer
To protect sensitive data, a new file named credential is used to store all credentials that are used in the main app and they are imported using the line "import Credential"
To keep track of activities that happens everytime you run the script, A detailed log is saved that automatically takes the current date as the name of the logfile. this is used to understand and trace performance of the script
