Code and format documentation as part of the [nextcloud-bookmarks](README.md) repository

# Documentation

#### Subroutine: describe
- If there is a human description, check if valid and add LLM page description
- If there is none, create

#### Subroutine: Tag cleaner
- Look for all tags that appear only once
- look for all bookmarks that are untagged (or with tag no_tag)

### 

- Check if website is still available
- If yes, do LLM summary, Create in "imported" folder
- if no, create in OBSOLETE- folder 

### Format of description

f"""
{description}
 # BOOKMARKED
{created_at}
 # LLM_DESCRIPTION
{suggested}
 # ANNOTATIONS
"""


### Nice to have
- Check for unavailable bookmarks, and mark/tag as obsolete
- Write created_at to "added" Unix ts (which is not in the API) (possible via SQL data base access: os)

## Database access

database-5015790379; Datenbank: dbs12878957
- Table: oc_bookmarks
    - id
    - url
    - title
    - user_id
    - description
    - added
    - lastmodified
    - clickcount
    - last_preview
    - available
    - archived_file
    - html_content
    - text_content

archived_file, html_content and text_content seem to be empty. 

### Diigo CSV format
title,url,tags,description,comments,annotations,created_at

Highlights are stored with the word "Highlight: " in annotations, so just add these text
Tags are separated by a space. 