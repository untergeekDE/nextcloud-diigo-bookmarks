# Nextcloud Bookmarks V0.2

VERY PRE-ALPHA: Code to add, edit and improve bookmarks in the [Nextcloud Bookmarks]() app. 

This code was created to save my [Diigo](https://www.diigo.com) bookmarks library. I have been a long-time paying user of the Diigo bookmarking service, but as it seems to be breaking down gradually, and and it is not a good idea to have a public bookmark file in the age of AIs being trained on public data, I decided to move all of my bookmarks to my Nextcloud. 

Authentication is a mess, but the routines work as a proof-of-concept so I am uploading them in case I haven't got the time to continue working on this. 

## A word on Diigo

Diigo was unique when I first started using it - and paying for it - around 2016. But it seems to be the effort of esentially one programmer, and the API gives a strong vibe of "I'll complete that when I get round to it". As of 2024, it is still running - sort of. My bookmarks library is never quite up to date, and searching is a hit-and-miss thing. I take this as a sign that the servers and code are no longer properly maintained, and that it is time to leave. 

So the original task was to import a bookmarks file exported from Diigo, and import it to a Nextcloud installation via the [Nextcloud Bookmarks API](https://nextcloud-bookmarks.readthedocs.io/en/latest/). Once that worked, I added code to maintain and clean the Nextcloud bookmarks, and access, read, edit, and remove the Diigo bookmarks via Diigo's API. 

The Diigo API is a mixed bag - [find my documentation of it here](diigo_api.md). I am still evaluating the API calls the Diigo website itself uses, as they are capable of doing things the official API does not support. 

## What this code is for

- Import a CSV file containing Diigo bookmarks
- Write new bookmarks to a DIIGO folder 
- Check whether bookmarks are still valid, and move to another folder if the bookmark url cannot be reached
- Backup and Overwrite/erase Diigo bookmarks

It is supposed to be doing those things as well pretty soon: 
- Groom the tags: check all tags that have been used only once
- Use a local AI for summarizing and tagging websites that have no description
- Import bookmarks directly from a Diigo account

I am going to put the most useful options into a simple command-line app that lets you select what you would like to do. As long as this does not work, you might have to write your own code to use those routines. 

I hope the code is documented and structured well enough that you can use it for your own projects, and save you some time. I am not the world's best Python coder but things work. 

## Using AI to improve your bookmarks

Many of my bookmarks missed a description, and tagging is far from perfect: lots of little spelling mistakes, and bookmarks that have been used only once (and are thus probably not that useful). Rather than gritting my teeth and working through the 8,000+ bookmarks of the recent years, I decided to summon help by the demons I have been busy conjuring in the last couple of months: Large language models (LLMs). 

This contains some experimental code to use a LLM to tag and describe bookmarks for you. LLMs are well capable of that, even smaller ones, but they might miss your original intention in bookmarking a URL. And reading websites and evaluating them with an LLM will produce quite a lot of tokens. So I decided to use a small LLM I can run locally on my machine ([Cohere's Aya](https://ollama.com/library/aya)) rather than the API of a larger model. 

Local LLMs are damn slow, and they are infuriatingly ignorant, at least if you have grown accustomed the the power of State-of-the-art LLMs like OpenAI's GPT4o or Anthropic Claude 3 Opus, but they are cheaper, and they are more discreet. Aya does the job - it works well enough in German (my native language) to be able to use it. Yet if you would want to use a State-of-the-art LLM, my best pick at the moment would be Anthropic Claude 3.5, or GPT4o - I'll add support for them, maybe. 

## Things I miss in Nextcloud Bookmarks

There are a couple of things the NC Bookmarks app does not do quite as well as Diigo, so I had to work around them: 

- No highlights: Diigo allows you to highlight text, and keeps these highlights in a separate 'annotations' field. I merged this into the description under an '# ANNOTATIONS' header. (Keep things simple, folks.) Once I have time to adapt my own Firefox bookmarking app, I'll have it evaluate this part of the description field to show highlights and annotations. 
- Creation date: The NC Bookmarks writes a creation date to the bookmark entries that cannot be accessed via the API. So I saved the original save date from Diigo in the description under a '# BOOKMARKED' header for later use. -- The only way to rewrite it is by changing the entries in Nextcloud's SQL database... no problem in theory, but my provider positively blocks the SQL database from being accessed from the outside, and that is probably A Good Thing. So this code will need you to (a) export your precious Nextcloud database, (b) have some tedious and half-baked code perform some surgery on it, and (c) re-import into Nextcloud. Good luck with that. 
- Read Later: One of Diigo's most useful features is to have it save a web page as a bookmark for later reading. This is simulated by having a separate folder (called "LESEN", "TO READ" in German) and move anything unread there.

## Main app and libraries

* **main.py**: A simple command-line app for executing functions. Run with ```python main.py``` (TODO)
* **upload_bookmarks.py**: Upload .csv diigo bookmark dump file to Nextcloud 
* **rework_sql_library.py**: A routine to import a SQL dump, and set the created_at field to the Diigo creation date saved in the description (TODO)

### Authentication
...is a mess right now, sorry about that. 

* **To authenticate your Nextcloud bookmarks app**, you will have to:
	- define the global variable with the Nextcloud user to use: ```nc_user = "MyUser"``` in the ```config.py``` file
	- generate an application key in Nextcloud for that user, 
	- save that key as a single string in a file ```~/key/nc.key``` (a directory for storing your API keys in your home dir)

* **To use Diigo**, you will have to do a tad bit more:
	- create an API key [here](https://www.diigo.com/api_keys/new/) and save it as a string to a file ```~/key/diigo_api.key```
	- define ```diigo_user = "MyDiigoUser"``` as a global variable in the ```config.py``` file
	- write your Diigo password as a single string to a ```~/key/diigo_pw.key``` file
	- authenticate Diigo in a browser session when prompted

Apologies for the inconvenience, working on a better way to do this. Hopefully, one file with all the users and keys, and reauthentication if necessary. 

### Libraries and files: 

Hinting where you find the routines you may use for your own code
* **nc_bookmarks_api.py**: Routines to manipulate bookmarks in the NC Bookmarks app
* **process.py**: Routines to evaluate tags, to check on URLs, and to generate descriptions and tags with AI. 
* **diigo_maintenance.py**: Routines to access Diigo via the official or the interaction API, and a routine to export and destroy the Diigo bookmarks. (I know there is an exporter in Diigo, but I guess it is a good idea to keep a dump anyway). 
* **import_csv.py** has a function that upload_bookmarks.py uses to read the Diigo bookmarks file (and details on that file's format) 

* **config.py** contains global variables like filenames and paths

Documentation dump on what the functions do, and on data formats, [here](code_doc.md).

### Todo 

- Main routine with simple command-line menus to perform maintenance 
- Actual loop to add AI description
- Tagging with AI

