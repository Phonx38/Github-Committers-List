# Assignment Logic


### Steps Followed ###

* First, We call **getUsernames()** function, which parses the given links from excel sheet and converts
data into list of github usernames to be used by **getRepos**  function
      
      
* Then, **getRepos()** function, fetches the repos of a user from github and save it in a list

* Then **getContributors()** function takes repos list of a user as input and fetches list of contributors in each
repository , fetching of contributors is done asynchronously as each user can contain various repos and each can
contain several contributors, so it is wise optimise the api call with async programming
  
    * **getContributors()** also have helper function **get_tasks()** to gather all the getContributor requests and handling
        them asynchronously

* **main()**  does the error handling and saves the final result to a excel sheet called final.xlsx.
  


