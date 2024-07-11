# Nextcloud/Diigo Bookmarks V0.5

VERY PRE-ALPHA: Code to use the API of bookmarking service [Diigo](https://www.diigo.com) to rescue and eventually delete them, and to add, edit and improve bookmarks in the [Nextcloud Bookmarks](https://apps.nextcloud.com/apps/bookmarks) app. 

**Although quite a lot of the stuff already works, the function needed to bulk-delete Diigo bookmarks does not.** The only way to remove a bookmark, as of now, is to use the (slow, complicated, buggy) offical API call. -- Have a thorough look at the ```test_diigo_api()``` routine in ```diigo_ap.py``` to understand what works and how it is done. 

This code was created to save my [Diigo](https://www.diigo.com) bookmarks library. I have been a long-time paying user of the Diigo bookmarking service, but as it seems to be breaking down gradually, and and it is not a good idea to have a public bookmark file in the age of AIs being trained on public data, I decided to move all of my bookmarks to my Nextcloud. 

Only some of the functions are up and running; but most of it is there in the code. Will 
improve step by step. 

## A word on Diigo

Diigo was unique when I first started using it - and paying for it - around 2016. But it seems to be the effort of esentially one programmer, and the API gives a strong vibe of "I'll complete that when I get round to it". As of 2024, it is still running - sort of. My bookmarks library is never quite up to date, and searching is a hit-and-miss thing. I take this as a sign that the servers and code are no longer properly maintained, and that it is time to leave. 

So the original task was to import a bookmarks file exported from Diigo, and import it to a Nextcloud installation via the [Nextcloud Bookmarks API](https://nextcloud-bookmarks.readthedocs.io/en/latest/). Once that worked, I added code to maintain and clean the Nextcloud bookmarks, and access, read, edit, and remove the Diigo bookmarks via Diigo's API. 

The Diigo API is a mixed bag - [find my documentation of it here](doc/diigo_api.md). I am still evaluating the API calls the Diigo website itself uses, as they are capable of doing things the official API does not support. 

## What this code is for

- Import a CSV file containing Diigo bookmarks
- Write new bookmarks to a DIIGO folder 
- Backup Diigo bookmarks
- Delete Diigo bookmarks
- Import Diigo bookmarks into Nextcloud
- Improve Nextcloud bookmarks with AI
- Improve tagging 
- Display dump files, analyze them, compare them

It is supposed to be doing those things as well pretty soon: 
- Groom the tags: check all tags that have been used only once
- Use a local AI for summarizing and tagging websites that have no description

### How to install and run

* You will need a Python environment. Anything >= 3.7 should be fine.
* Get a copy of the files to your computer: 
	* Download a ZIP of the repository and unpack to a local folder 
	* ...or simply use git: ```git clone https://github.com/untergeekDE/nextcloud-diigo-bookmarks.git```
* If you want to, put your user/password information for Diigo and Nextcloud into the key file at ```~/.ncdbookmarks/key.yaml```. (As of now, you might still need a Diigo API key although I don't actually use it for most functions)
* Change into the directory.
* Get the necessary libraries: ```pip -r requirements.txt```
* Start on the command line: ```python main.py```

The program checks the credentials for Diigo and your Nextcloud installation, opens a Firefox browser window to have you authenticate a Diigo session, and offers you a set of tools and functions via a simple command-line interface. 

### What you need to run it
- Python (anything >= 3.7 should be fine)
- The libraries listed in the ```requirements.txt``` file - some odd ones like [Selenium](https://www.selenium.dev/), [console-menu](https://github.com/aegirhall/console-menu), PyYAML
- A Firefox browser (Chrome support will be added soon)
- A diigo account
- A [Nextcloud](https://nextcloud.com/install/#instructions-server) instance running the [Bookmarks](https://apps.nextcloud.com/apps/bookmarks) app
- if you want to use AI to check bookmarks for you, I rely on a local model running on your machine: You will need [Ollama](https://ollama.com/) running on your computer, and enough memory, disk space and compute to run the [Aya](https://ollama.com/library/aya) or [Gemma2-9B](https://ollama.com/library/gemma2) model (which are both quite capable). Which kind of excludes anything below 8GB graphics memory.
- patience

### Todo 

- Tagging with AI
- Reimport into Diigo (if only for further testing)
- Tools submenu
	- Comparison of Diigo and Nextcloud bookmarks
	- Tags analysis
	- Manual editing
- Check whether Firefox, or Chrome, is actually on the system
- Add OpenAI GPT4o/Anthropic Claude3 API support 

I hope the code is documented and structured well enough that you can use it for your own projects, and save you some time. I am not the world's best Python coder but things work. 

## Using AI to improve your bookmarks

Many of my bookmarks missed a description, and tagging is far from perfect: lots of little spelling mistakes, and bookmarks that have been used only once (and are thus probably not that useful). Rather than gritting my teeth and working through the 8,000+ bookmarks of the recent years, I decided to summon help by the demons I have been busy conjuring in the last couple of months: Large language models (LLMs). 

This contains some experimental code to use a LLM to tag and describe bookmarks for you. LLMs are well capable of that, even smaller ones, but they might miss your original intention in bookmarking a URL. And reading websites and evaluating them with an LLM will produce quite a lot of tokens. So I decided to use a small LLM I can run locally on my machine ([Cohere's Aya](https://ollama.com/library/aya)) rather than the API of a larger model. 

Local LLMs are damn slow, and they are infuriatingly ignorant, at least if you have grown accustomed the the power of State-of-the-art LLMs like OpenAI's GPT4o or Anthropic Claude 3 Opus, but they are cheaper, and they are more discreet. Aya does the job - it works well enough in German (my native language) to be able to use it. The recent Gemma2 model by Google is extremely capable for something of that size. Yet if you would want to use a State-of-the-art LLM, my best pick at the moment would be Anthropic Claude 3.5, or GPT4o - I'll add support for them, maybe. 

## Things I miss in Nextcloud Bookmarks

There are a couple of things the NC Bookmarks app does not do quite as well as Diigo, so I had to work around them: 

- No highlights: Diigo allows you to highlight text, and keeps these highlights in a separate 'annotations' field. I merged this into the description under an '# ANNOTATIONS' header. (Keep things simple, folks.) Once I have time to adapt my own Firefox bookmarking app, I'll have it evaluate this part of the description field to show highlights and annotations. 
- Creation date: The NC Bookmarks writes a creation date to the bookmark entries that cannot be accessed via the API. So I saved the original save date from Diigo in the description under a '# BOOKMARKED' header for later use. -- The only way to rewrite it is by changing the entries in Nextcloud's SQL database... no problem in theory, but my provider positively blocks the SQL database from being accessed from the outside, and that is probably A Good Thing. So this code will need you to (a) export your precious Nextcloud database, (b) have some tedious and half-baked code perform some surgery on it, and (c) re-import into Nextcloud. Good luck with that. 
- Read Later: One of Diigo's most useful features is to have it save a web page as a bookmark for later reading. This is simulated by having a separate folder (called "LESEN", "TO READ" in German) and move anything unread there.

## Main app and libraries

* **main.py**: A simple command-line app for executing functions. Run with ```python main.py``` (TODO)
* **import_export.py**: Upload .csv diigo bookmark dump file to Nextcloud 
* **nc_llm_improve.py**: Reads all Nextcloud bookmarks, and adds an LLM description of the website, if possible. 

### Authentication

The program looks in the ```.ncdbookmarks``` directory for credentials for Diigo and Nextcloud. If it doesn't find them, or they don't work, it asks for the credentials. 

* **To use Diigo**, the main routine will ask you to:
	- create an API key [here](https://www.diigo.com/api_keys/new/)
	- supply user and password
	- authenticate Diigo in a browser session when prompted

* **To authenticate your Nextcloud bookmarks app**, you will have to suppy user and password

User and credentials for Diigo and Nextcloud are saved in a YAML file at ```.ncdbookmarks/key.yaml```. You can modify the file directy. A sample file ```sample_key.yaml``` can be found in the project directory. 

The code uses session cookies to authenticate most API calls. Once the Diigo session is authenticated, the session cookies are saved to a YAML file at ```.ncdbookmarks/session_cookies.yaml```, where it can be used by the requests library. 

### Libraries and files: 

Hinting where you find the routines you may use for your own code
* **nc_bookmarks_api.py**: Routines to manipulate bookmarks in the NC Bookmarks app
* **process.py**: Routines to evaluate tags, to check on URLs, and to generate descriptions and tags with AI. 
* **diigo_maintenance.py**: Routines to access Diigo via the official or the interaction API, and a routine to export and destroy the Diigo bookmarks. (I know there is an exporter in Diigo, but I guess it is a good idea to keep a dump anyway). 
* **import_export.py** h

* **config.py** contains global constants as well as a global variable and code for handling it

* Documentation dump on what the functions do, and on data formats, [can be found here](doc/code_doc.md).
* My [findings and documentations of the Diigo API](doc/diigo_api.md)
