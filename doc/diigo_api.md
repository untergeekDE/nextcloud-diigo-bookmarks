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

* HTTP Method: GET

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

* HTTP Method: POST

Bookmarks are identified via URL and title, so if those already exist, the bookmark is modified; if not, it is created. The merge=<"yes"|"no"> parameter selects whether the specifications are appended or overwritten. 

Parameters (via a params dictionary):
- key
- user 
- url
- title
- desc
- merge: <"yes"|"no">

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

Heavily rate-limited. It seems to work if you run it in an authenticated session, and with a short delay after each delete (I tried 5 seconds)

* HTTP Method: DELETE

Parameters: 
- user
- apikey
- url
- title

The bookmark to delete is identified by url and title. 

Responds with a json containing a "message" parameter that states the number of actually deleted bookmarks. 

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

* End points: ```https://www.diigo.com/interact_api/```
* Authentication: HTTP Basic, session cookies, user agent

**To use the Interaction API, you have to authenticate manually for the proper session cookies.*** We could automate that but the login page has a Captcha - which is normally A Good Thing but makes things a bit more complicated. So the pragmatic thing to do is: authenticate manually before running calls of the Interaction API. (The code does this by opening a browser window with Selenium and asking you to authenticate there, saving the browser cookies to a file and using it in the requests session.)

**The Interaction API does not like the python-requests user agent.** You will have to spoof a browser via the 'User-Agent' header command to make the server think that you are using a browser. 

Known commands: 
* **load_user_items**
* **search_user_items**
* **load_user_tags**
* **bookmark** 

* **load_user_info**
* **load_user_groups**
* **load_shared_to_groups** 

### ```load_user_items``` - Get bookmark list

Get a list of bookmarks, sorted by the API. 
* Endpoing: ```https://www.diigo.com/interact_api/```
* HTTP method: GET

Parameters (via a params dictionary):
- page_num: offset (default = 0), negative values are allowed
- count: number of bookmarks to list
- sort: <'created'|'updated'|'popularity'|'hot'>
- filter: <'public'|'all'> (only public bookmarks, or private ones as well)

Returns a json/dict with items containing these parameters:
- "comments": list of strings
- "created_at": int32 Unix datetime,
- "updated_at": int32 Unix datetime,
- "annotations": list of strings
-    "url": string,
- "title":string,
-    "description": string
-    "t_name": string
- "private": <true|false>
-    "link_id": int32 

...and a couple more, containing info on who bookmarked an URL first on Diigo, and which groups a bookmark might belong to. See sample output below. 

The most important info is probably *link_id*

Python Example: 
```
# Needs authenticated session, see diigo_login()
response = session.get("https://www.diigo.com/interact_api/load_user_items",
                            headers = {
                                "Accept": "application/json", 
                                "Authorization": "basic"
                                }, 
                            params = {
                                   'key': quote(diigo_key),
                                    'user': quote(diigo_user),
                                    'page_num': page,
                                    'sort': 'updated',
                                    'count': count, 
                                },
                            auth=(diigo_user, diigo_pw),
                            )
```

Sample output: 
```
{"items":[{"comments":[],"pri_sticky_count":0,"created_at":1664870103,"annotations":[],"c_count":0,"real_name":"Jan Eggers","first_by_real_name":"Centre de Documentació Europea Universitat Autònoma de Barcelona","type_name":"bookmark","text_view_link":"https://www.diigo.com/text_view?url=https%3A%2F%2Fcds.climate.copernicus.eu%2F%23%21%2Fhome","pub_sticky_count":0,"user_id":802697,"pri_c_count":0,"updated_at":1664870103,"hasDetails":"false","readed":0,"pub_c_count":0,"outliners_id":[],"groups":[],"pri_a_count":0,"private":true,"description":"","ouliner_id":[],"t_name":"","title":"https://cds.climate.copernicus.eu/#!/home","pub_a_count":0,"tags":"","mode":2,"url":"https://cds.climate.copernicus.eu/#!/home","is_attached_item":true,"first_by":"cde_uab","u_name":"untergeekde","link_id":487558580}]}
```

### ```search_user_items``` - Get filtered bookmark list

Get a list of bookmarks filtered by the "What" parameter (which seems to filter for title)
* Endpoint: ```https://www.diigo.com/interact_api/search_user_items```
* HTTP method: GET

Basically the same as ```load_user_items``` but with filtering by the 'what' parameter. That seems to look through title, url, and description - same as in the webui - and isn't very good. Other parameters are the same as load_user_items

Parameters: 
- sort: <'created'|'updated'|'popularity'|'hot'>
- count: int
- what: search string
- page_num: int

### ```load_user_tags``` - Get a dict of all tags with the frequency of their use

### ```bookmark```- (POST) Create a bookmark

Creates/Overwrites a bookmark
* Endpoint: ```https:///www.diigo.com/item/save/bookmark```
* HTTP Method: POST
* Authentication: session, basic auth, User-Agent

This endpoint needs the User-Agent parameter in the CURL header to be set to a common browser. Having the standard Python requests User-Agent does not work. 

Parameters:
- title
- url
- link_id: str (identifies existing bookmark - see below)
- description: str (optional)
- new_url: str (when editing bookmark)
- private: <'true'|'false'> (optional)
- unread: <'true'|'false'> (optional)
- lists: str (optional)
- group: str (optional)

Creates a new bookmark, or overwrite existing bookmark. Check whether bookmark exists seems to work link_id but also via URL/title (you can overwrite without a link_id). 

Returns a HTML page rather than a JSON but seems to work regardless. 

## The Bulk Management API - same as Interaction API but...

Bulk modifiying, and deleting, is done by yet another set of API commands. You can see it at work loading the Diigo website with the browser tools opened, looking at the Network tab; but authentication does not seem to work as with the Interaction API. Maybe it is only accepted when coming from the Diigo.com website - must check. If that really is true, the fastest way to perform bulk management of bookmarks would be a Selenium session initiating a select/delete process via Selenium or Puppeteer.

* Endpoint: ```https://www.diigo.com/ditem_mana2/```
* Authentication: HTTP Basic, session cookies, user agent, ?
* HTTP Method: POST

**Still not sure how to authenticate.** Although the same kind of authentication methods as with the Interaction API seem to work (session cookies, User-Agent), delete_b returns 403 ('Forbidden'). Looking at the network connection, it might be that this call really needs to be issued from the Diigo server and nowhere else.  

These commands are known. 
* **delete_b** (POST) Delete a list of bookmarks
* **mark_readed** (POST) Read/unread a list of bookmarks
* **convert_mode** (POST) Set  a list of bookmarks Private/Public

### ```delete_b``` - Remove all bookmarks in a list

Remove a list of bookmarks identified by their link ID.

* Endpoint: ```https://www.diigo.com/ditem_mana2/delete_b```
* HTTP method: POST

- link_id: **string with comma-separated list** of link_ids

Python Example: 
```
# Needs authenticated session, see diigo_login()
response = session.get("https://www.diigo.com/ditem_mana2/delete_b",
                            headers = {
                                "Accept": "application/json", 
                                "Authorization": "basic"
                                }, 
                            params = {
                                    'list_id':'12345,67890,23456'  
                                },
                            auth=(diigo_user, diigo_pw),
                            )
```

### ```mark_readed``` (POST)

Mark bookmark(s) as read or unread
* Endpoint: ```https://www.diigo.com/ditem_mana2/mark_readed```
* HTTP method: POST

- link_id: string with comma-separated list of link_ids
- readed: <"0"|"1"> "0" is unread

### ```convert_mode``` - Set public/private

Set bookmark(s) to public/private

* Endpoint: ```https://www.diigo.com/ditem_mana2/convert_mode```
* HTTP method: POST

- link_id: string with comma-separated list of link_ids
- mode: <"0"|"1"|"2"> "0" for public, "1" for ?, "2" for private