import os
import json
import asyncio
import aiohttp
import pandas as pd
import urllib

from dotenv import load_dotenv


load_dotenv()


class GithubAnalysis:

    TOKEN = os.environ.get("token")
    HEADERS = {"authorization": f"Bearer {TOKEN}"}
    BASE_URL = "https://api.github.com"

    def getUsernames(self):
        """
        Fetches and parses usernames from the given data to be
        used by other functions
        """
        dataframe1 = pd.read_excel("data.xlsx", header=None)

        links = list(dataframe1.iloc[:, 0])

        usernames = []
        for link in links:
            path = urllib.parse.urlparse(link).path
            while os.path.dirname(path) != "/":
                path = os.path.dirname(path)
            usernames.append(path.split("/")[1])

        return usernames

    async def getRepos(self, username):
        """
        Fetches and parses repos of a username from github
        """
        async with aiohttp.ClientSession() as session:

            repos = []
            url = f"{self.BASE_URL}/users/{username}/repos"

            response = await session.get(url, headers=self.HEADERS, ssl=False)
            response.raise_for_status()
            if response.status != 204: #because some repos do not exist or can be private in github
                result = await response.json()

            for d in result:
                repos.append(d["name"])
        return repos

    def get_tasks(self, session, repos, username):

        """
        helper function to gather all the getContributor requests and handling
        them asynchronously
        """

        tasks = []
        for i in repos:
            url = f"{self.BASE_URL}/repos/{username}/{i}/contributors"

            tasks.append(session.get(url, headers=self.HEADERS, ssl=False))

        return tasks

    async def getContributors(self, repos, username):
        """
        Fetches contributors of a particular repo from github.

        """
        async with aiohttp.ClientSession() as session:

            repos = repos

            json_contri = {}
            tasks = self.get_tasks(session, repos, username)
            # print(i)
            responses = await asyncio.gather(*tasks)
            for repo, response in zip(repos, responses):
                response.raise_for_status()
                if response.status != 204:
                    resJson = await response.json()

                    json_contri[repo] = [x["login"] for x in resJson]

            return json_contri

    async def main(self):
        final_dic = {}
        usernames = self.getUsernames()
        for username in usernames:
            try:
                repos = await self.getRepos(username)
                contributors = await self.getContributors(repos, username)
            except aiohttp.client_exceptions.ClientResponseError as e: #because some usernames do not exist in github
                print(e)
                continue

            final_dic[username] = contributors

        result = {}
        vals = list(final_dic.values())
        # preparing data before converting to excel sheet 
        for val in vals:
            for repo, users in val.items():
                temp = [user for user in users if user in usernames]
                # list of users for each repo is converted into a string of comma seperated value
                result[repo] = ",".join(temp)
        df = pd.DataFrame(data=result, index=[0])

        df = df.T

        df.to_excel("final.xlsx")


asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
g = GithubAnalysis()
asyncio.run(g.main())
