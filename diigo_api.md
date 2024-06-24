Diigo API documentation as part of the [nextcloud-bookmarks](README.md) repository

# The Diigo API

Apart from being not very well-documented, the API has the distinct disadvantage of offering a very limited set of actions, with a very harsh rate restriction. The Diigo website wouldn't actually work with this - and uses its own API.

So instead of one API, there are actually two: 
- the "official" API on the endpoint ```https://secure.diigo.com/api/v2/```
- the interaction API on the endpoint ```https://www.diigo.com/interact_api/```

They both share the way they are used: with a CURL command like GET or POST (and, in one case, DELETE), and [basic authentication](https://en.wikipedia.org/wiki/Basic_access_authentication) - i.e. a header entry containing the user name and password in base-64. The official secure API also needs you to send an API token and the user as parameters to authenticate. The interaction API needs an authenticated session. 

For those who are better with those things than I am: They are both REST APIs, I think that may cover it. 

## The Secure API

("Secure" as in: inconvenient) - the official API calls for accessing your bookmarks. Secured double by user/password, and an API token that can be generated here on the DIIGO page. 

Although there is no mention of a rate limit, the numer of calls per quarter hour seems to be limited to a couple of dozens. If you exceed that number, you will get a timeout for a minute, then for twenty minutes. 

* End point: ```https://secure/diigo.com/api/v2/```
* Authentication: HTTP Basic **and** username plus API token

Known commands:
* **Get bookmarks** - Return a list of bookmarks
* **Write a bookmark** - Create or overwrite a bookmark identified by URL and title
* **Delete a bookmark** - Remove a bookmark identified by URL and title (undocumented)

The little original documentation there is can be found at https://www.diigo.com/api_dev

### Get bookmarks

Get a list of bookmarks, sorted by the API, and hopefully filtered by the parameters. (It does not seem to work correctly for tags.)

Parameters (via a params dictionary):
- start: offset (default = 0)
- count: number of bookmarks to list
- sort: 0-3; 0='created_at', 1='updated_at', 2: 'popularity', 3: 'hot', defaults to 0
- tags: string of comma-separated tags to filter by; does not seem to work correctly
- filter: <'public'|'all'> (only public bookmarks, or private ones as well)
- list: string naming a bookmark list (a sparsely used Diigo feature)

Returns a json/dict with items containing these parameters: 
-    "title": string
-    "url": string,
-   "user":" string
-    "desc": string
-    "tags": string
-    "shared":" string <'yes'|'no'>
-    "created_at":string datetime (with timezone),
-    "updated_at":string datetime (with timezone),
-    "comments": list of strings,
-    "annotations": list of strings

Python Example: 
```
response = requests.get("https://secure.diigo.com/api/v2/bookmarks",
                            headers = {
                                "Accept": "application/json",
                                "Authorization": "basic" },
                            params = {
                                "key": api_key_string,
                                "user": user_id_string,
                                "count": 10
                            },
                            auth= (user_id_string, user_password),
                            )
```
### Write a bookmark

Bookmarks are identified via URL and title, so if those already exist, the bookmark is modified; if not, it is created. The merge=<"yes"|"no"> parameter selects whether the specifications are appended or overwritten. 

Python Example: 
```
response = requests.post("https://secure.diigo.com/api/v2/bookmarks",
                            headers = {
                                "Accept": "application/json",
                                "Authorization": "basic" },
                            params = {
                                "key": api_key_string,
                                "user": user_id_string,
                                "url": "https://www.test.de",
                                "title": "Test",
                                "desc": "A test."
                            },
                            auth= (user_id_string, user_password),
                            )
```

Responds with a json stating success. Contents are not really that valuable.
### Delete a bookmark

Undocumented method to delete a bookmark via a CURL DELETE call. Bookmark to delete is identified by URL and title. 

Heavily rate-limited. 

Responds with a json stating success. Contents are not really that valuable.

Python Example
```
response = requests.delete("https://secure.diigo.com/api/v2/bookmarks",
                            headers = {
                                "Accept": "application/json",
                                "Authorization": "basic" },
                            params = {
                                "key": api_key_string,
                                "user": user_id_string,
                                "url": "https://www.test.de",
                                "title": "Test",
                            },
                            auth= (user_id_string, user_password),
                            )

```
## The Interaction API

This is the API used by the website itself; you can see it at work loading the Diigo website with the browser tools opened, looking at the Network tab. 

* End point: ```https://www.diigo.com/interact_api/```
* Authentication: HTTP Basic, session cookie

**To use the Interaction API, you have to authenticate manually for the proper session cookies.*** We could automate that but the login page has a Captcha - which is normally A Good Thing but makes things a bit more complicated. So the pragmatic thing to do is: authenticate manually before running calls of the Interaction API. 

In my code, there is a routine 

Known commands: 
* **load_user_items**
* **load_user_info**
* **load_user_tags**
* **load_user_groups**
* **load_shared_to_groups**
* **delete_b**

### Get bookmarks

Get a list of bookmarks, sorted by the API, and hopefully filtered by the parameters. (It does not seem to work correctly for tags.)

Parameters (via a params dictionary):
- start: offset (default = 0)
- count: number of bookmarks to list
- sort: 0-3; 0='created_at', 1='updated_at', 2: 'popularity', 3: 'hot', defaults to 0
- tags: string of comma-separated tags to filter by; does not seem to work correctly
- filter: <'public'|'all'> (only public bookmarks, or private ones as well)
- list: string naming a bookmark list (a sparsely used Diigo feature)

Returns a json/dict with items containing these parameters: 
-    "title": string
-    "url": string,
-   "user":" string
-    "desc": string
-    "tags": string
-    "shared":" string <'yes'|'no'>
-    "created_at":string datetime (with timezone),
-    "updated_at":string datetime (with timezone),
-    "comments": list of strings,
-    "annotations": list of strings

Python Example: 
```
