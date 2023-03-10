## Media Sorting Script

> Disclaimer: I'm not a programmer of any kind. The goal of this project is to create a photosorting python script using ChatGPT.


## What it does?

Simply organizing bunch of media files that were uploaded to Dropbox from my iPhone.

Here's before:
![Before](https://i.imgur.com/AQhBOOO.png)

Here's after:
![After](https://i.imgur.com/BZNkav8.png)

**All files unable to sort stay untouched**


## How to use?

**Assumptions**: brew and pip are installed

1. Clone it to your host
2. Install `ffmpeg` via Brew:
    ```
    >>> brew install ffmpeg
    ```
3. Create a new virtual environment and activate it:
    ```
    >>> virtualenv photoSort
    >>> source photoSort/bin/activate
    >>> pip install -r requirements
    ```
4. To run the script over sample media files, launch it and press Enter without typing anything:
    ```
    >>> python3 sorting.py
    ```
5. If your folder name is different, you can pass it as an input string, i.e. type *pics*
The path is relative only at the moment.

## What file does it process?
Images:
- .jpg
- .jpeg
- .dng

Video:
- .mov


## To do:
- normalize extensions
- add mp4
- find out why is it so slow (except bcs it's python)